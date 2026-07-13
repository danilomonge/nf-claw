from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from runner import (discovery, engine_version, execution, nextflow_command,
                    outputs, parameters, plugin_compat, preflight, provenance,
                    resources, samplesheet, versions)
from runner import schema as schema_mod
from runner.errors import ErrorCode, NfclawError


@dataclass
class RunResult:
    command: str
    outdir: Path
    checked_only: bool
    outputs_report: "outputs.OutputsReport | None"
    warnings: list[str] = field(default_factory=list)


def run_pipeline(name: str, *, repo_root: Path, input_path: "Path | str | None",
                 outdir: Path, profile: str, params_file: Path | None,
                 cli_overrides: dict, resume: bool, demo: bool,
                 check_only: bool, write_provenance: bool,
                 timeout_seconds: int, pipeline_version: str | None = None,
                 nxf_ver: str | None = None,
                 nxf_env: dict[str, str] | None = None,
                 allow_spaces: bool = False,
                 configs: tuple[str, ...] | list[str] = (),
                 limits: "resources.ResourceLimits | None" = None) -> RunResult:
    pipelines_dir = repo_root / "pipelines"
    discovery.find(name, pipelines_dir)                       # 404 if unknown
    # Extra Nextflow config files passed straight through as `-c` (e.g. a docker host-network or
    # custom-resources config). Resolved to absolute and validated up front so a typo fails fast.
    extra_configs: list[Path] = []
    for c in configs:
        cfg = Path(c).expanduser().resolve()
        if not cfg.is_file():
            raise NfclawError(ErrorCode.ENVIRONMENT, f"--config file not found: {c}",
                              fix="Pass a path to an existing Nextflow config file.")
        extra_configs.append(cfg)
    # A --params-file the user named must exist: nfclaw reads it itself (merge, below), so a typo'd
    # path would otherwise be silently dropped and the run proceed with none of its values. Fail
    # fast, naming the path — the same fail-fast contract as --config above.
    if params_file is not None:
        params_file = params_file.expanduser()
        if not params_file.is_file():
            raise NfclawError(ErrorCode.PARAMS_INVALID, f"--params-file not found: {params_file}",
                              fix="Pass a path to an existing JSON or YAML params file.")
    # None → pinned latest (unchanged); a tag → that release, validated + materialized.
    # Everything downstream consumes `st`/`st.path`, so it all targets the chosen version.
    st = versions.ensure(name, pipeline_version, pipelines_dir=pipelines_dir,
                         repo_root=repo_root)
    # The Nextflow runtime env nfclaw applies for this run: --nxf-env vars plus --nxf-ver
    # (sugar for NXF_VER, which wins if both set it). Threaded to the engine check, the
    # subprocess and provenance so the engine actually used is consistent and recorded.
    nxf_overlay = dict(nxf_env or {})
    if nxf_ver:
        nxf_overlay["NXF_VER"] = nxf_ver
    # The Nextflow work directory for this run: NXF_WORK (overlay wins over the shell) if set,
    # else the repository work directory. Resolve it before Nextflow changes cwd to the outdir,
    # so a relative user value has one stable meaning in preflight, execution and provenance.
    work_dir = Path(nxf_overlay.get("NXF_WORK") or os.environ.get("NXF_WORK")
                    or repo_root / "work").expanduser().resolve()
    param_schema = schema_mod.load_param_schema(st.path)
    input_schema = schema_mod.load_input_schema(st.path)

    # Only a local samplesheet (a Path) gets the deterministic pre-check. A remote --input (URL, a
    # str) can't be read locally — Nextflow stages it and nf-schema validates it at runtime — so it
    # is forwarded unchanged, exactly as nf-core pipelines accept it.
    if isinstance(input_path, Path) and input_schema is not None:
        problems = samplesheet.validate(input_path, input_schema)
        if problems:
            raise NfclawError(ErrorCode.SAMPLESHEET_INVALID,
                              "Samplesheet failed validation.",
                              details={"issues": problems})

    # Merge params-file + --input/--outdir + CLI first, then validate the WHOLE map — a typo
    # or bad enum in the params-file must fail fast too, not only CLI flags.
    merged = parameters.merge(cli_overrides=cli_overrides, params_file=params_file,
                              input_path=input_path, outdir=outdir)
    # Coerce CLI strings to their schema scalar type (e.g. `--skip-busco true` → real boolean)
    # before validating and writing the params-file, so nf-schema sees correctly-typed values.
    merged = parameters.coerce_to_schema(merged, param_schema)
    # Fix the report/timeline/trace/DAG filenames for this run instead of letting the pipeline
    # re-evaluate `now()` on every launch, so replaying the bundle reproduces the run's outputs
    # rather than writing a second, differently-named set of reports beside them.
    merged = parameters.pin_report_suffix(merged, param_schema)
    param_errors = parameters.validate_params(merged, param_schema)
    if not demo:
        param_errors.extend(parameters.missing_required_params(merged, param_schema))
    if param_errors:
        raise NfclawError(ErrorCode.PARAMS_INVALID,
                          "Parameters failed validation (fix before running).",
                          fix="Use parameter names and allowed values from reference.md.",
                          details={"issues": param_errors})

    composed_profile = nextflow_command.compose_profile(profile, demo=demo)
    issues = preflight.check_environment(profile=composed_profile, output_dir=outdir,
                                         submodule=st, repo_root=repo_root, resume=resume,
                                         work_dir=work_dir, allow_spaces=allow_spaces,
                                         check_only=check_only)
    if issues:
        raise NfclawError(ErrorCode.ENVIRONMENT, "Preflight checks failed.",
                          details={"issues": issues})

    # Advisory only: preflight has confirmed nextflow is on PATH, so compare the installed
    # engine to the pipeline's declared requirement. Non-blocking — Nextflow is the authority
    # and enforces this itself at launch; we just surface it earlier with a clear message.
    warnings = engine_version.check(st.path, nxf_ver=nxf_overlay.get("NXF_VER"))
    # Same contract: advisory, never blocking. Explains a warning the pinned release will emit for a
    # reason that is invisible in its log, so it is not mistaken for a fault in the run or in nfclaw.
    warnings += plugin_compat.check(st.path)

    # Where the files nfclaw generates for the run (params file, resource-limits config) are staged.
    # A real run stages them in its own provenance bundle. `--check` must not: it validates and
    # prints the command *without launching*, so it has to leave `--outdir` exactly as it found it —
    # creating it, or dropping a provenance/ directory in it, makes the next real run fail the
    # "--outdir is not empty" guard against a directory that holds no results at all. The staged
    # files are still written (to a temp directory that outlives the process), so the command
    # `--check` prints stays runnable as printed.
    if check_only:
        staging = Path(tempfile.mkdtemp(prefix="nfclaw-check-"))
    else:
        outdir.mkdir(parents=True, exist_ok=True)
        staging = outdir / "provenance"
    resolved = parameters.resolve_path_params(merged, param_schema)
    params_file_out = parameters.write_params_file(resolved, staging / "params.json")

    # A resource ceiling (--limit-cpus/--limit-memory/--limit-time) becomes a generated Nextflow
    # config passed with `-c`, exactly as nf-core's configuration docs prescribe. It goes *first*
    # so an explicit `--config` the caller passed still wins, and it lives in the provenance bundle
    # so `commands.sh` — which carries the same absolute `-c` path — replays the same ceiling.
    if limits is not None and not limits.is_empty():
        extra_configs.insert(0, resources.write_config(
            limits, staging / "resource_limits.config"))

    # Pass the work dir explicitly so it stays off the outdir (shared, content-hashed — fine),
    # and any extra `-c` configs. nfclaw launches Nextflow from the outdir (below) so each run
    # gets its own .nextflow/ state, but the work dir must not move into the results.
    cmd, cmd_str = nextflow_command.build(upstream=st.path, profile=composed_profile,
                                          params_file=params_file_out, resume=resume,
                                          work_dir=work_dir, extra_configs=tuple(extra_configs))
    if check_only:
        return RunResult(command=cmd_str, outdir=outdir, checked_only=True,
                         outputs_report=None, warnings=warnings)

    refs = param_schema.reference_path_params()
    prov_inputs = [Path(v) for k, v in resolved.items()
                   if k in refs and k != "outdir" and isinstance(v, str) and "://" not in v]

    def record(outcome: str) -> None:
        provenance.write(outdir=outdir, pipeline=name, command_str=cmd_str, submodule=st,
                         input_paths=prov_inputs, env_extra=nxf_overlay, outcome=outcome)

    # Launch from the outdir so each run owns its `.nextflow/` history and cache: `-resume` then
    # resumes THIS run, never another pipeline's session. Paths in the command are absolute, so
    # the cwd only decides where the engine state lands.
    try:
        execution.run(cmd, cwd=outdir, logs_dir=outdir / "provenance" / "logs",
                      timeout_seconds=timeout_seconds, env_extra=nxf_overlay)
    except BaseException:
        # A failed run is exactly when the bundle is needed most: `commands.sh` is what replays the
        # run once the cause is fixed, and the checksums record what it did manage to produce. Write
        # it, then re-raise — a provenance error must never replace the real failure as the cause.
        if write_provenance:
            try:
                record("failed")
            except Exception:                         # best effort; must not mask the real failure
                pass
        raise
    report = outputs.collect(outdir)
    if write_provenance:
        record("success")
    return RunResult(command=cmd_str, outdir=outdir, checked_only=False,
                     outputs_report=report, warnings=warnings)
