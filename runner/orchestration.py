from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from runner import (discovery, engine_version, execution, inputs, nextflow_command,
                    outputs, parameters, plugin_compat, preflight, provenance,
                    resources, runlog, samplesheet, versions)
from runner import schema as schema_mod
from runner.errors import ErrorCode, NfclawError
from runner.submodule import SubmoduleStatus


def _resume_advisory(outdir: Path, st: SubmoduleStatus) -> list[str]:
    """Advise when `--resume` continues a run that executed different pipeline code.

    Resuming re-launches whatever the request resolves to *now*. For a release that is the code the
    earlier run used, but `dev` moves: the run being resumed may have executed an older commit.
    Nextflow's cache stays correct either way (it reuses only tasks whose code and inputs are
    unchanged), so this is advisory — it explains why some tasks re-run and that the results now
    mix two commits. The earlier commit comes from that run's provenance manifest, if it wrote one."""
    try:
        prev = json.loads((outdir / "provenance" / "run_manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    prev_commit = prev.get("commit") if isinstance(prev, dict) else None
    if not isinstance(prev_commit, str) or not prev_commit or prev_commit == st.commit:
        return []
    return [f"--resume continues a run that executed {prev.get('version') or '?'} "
            f"(commit {prev_commit[:12]}); this launch executes {st.version} (commit "
            f"{st.commit[:12]}). Nextflow reuses only tasks whose code and inputs are unchanged, "
            "so tasks touched by the change re-run and the results combine both commits."]


@dataclass
class RunResult:
    command: str
    outdir: Path
    checked_only: bool
    outputs_report: "outputs.OutputsReport | None"
    warnings: list[str] = field(default_factory=list)
    log_path: Path | None = None            # the run log; None for --check, which launches nothing


def run_pipeline(name: str, *, repo_root: Path, input_path: "Path | str | None",
                 outdir: Path, profile: str, params_file: Path | None,
                 cli_overrides: dict, resume: bool, demo: bool,
                 check_only: bool, write_provenance: bool,
                 timeout_seconds: int | None, pipeline_version: str | None = None,
                 nxf_ver: str | None = None,
                 nxf_env: dict[str, str] | None = None,
                 allow_spaces: bool = False,
                 configs: tuple[str, ...] | list[str] = (),
                 limits: "resources.ResourceLimits | None" = None,
                 on_warning: Callable[[str], None] | None = None) -> RunResult:
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

    # Read the params file once; it is merged below, and it may be what supplies `input`.
    file_params = parameters.load_params_file(params_file) if params_file is not None else {}

    # What --input is comes from the pipeline's own schema, not an assumption: a samplesheet, another
    # local path (a directory, an SDRF file), or a plain value (a PRIDE accession, a URL, `false`).
    # Only a local samplesheet gets the deterministic pre-check; a remote one is staged by Nextflow and
    # validated by nf-schema at runtime, and a plain value is forwarded unchanged. The flag wins over
    # the params file's `input` (as in the merge below), and whichever supplies the value, it is
    # interpreted the same way — a params-file `input: false` or relative samplesheet means exactly
    # what `--input false` or `--input sheet.csv` does.
    raw_input = input_path if input_path is not None else file_params.get("input")
    resolved_input = inputs.resolve(raw_input, st.path)
    if resolved_input is not None and resolved_input.local_path is not None:
        input_schema = (schema_mod.load_input_schema(st.path, resolved_input.samplesheet_schema)
                        if resolved_input.samplesheet_schema else None)
        if input_schema is not None:
            problems = samplesheet.validate(resolved_input.local_path, input_schema)
            if problems:
                raise NfclawError(ErrorCode.SAMPLESHEET_INVALID,
                                  "Samplesheet failed validation.",
                                  details={"issues": problems})
        elif resolved_input.must_exist and not resolved_input.local_path.exists():
            raise NfclawError(ErrorCode.PARAMS_INVALID,
                              f"--input not found: {resolved_input.local_path}",
                              fix="Pass an existing file or directory (see Inputs in skill.md).")

    # Merge params-file + --input/--outdir + CLI first, then validate the WHOLE map — a typo
    # or bad enum in the params-file must fail fast too, not only CLI flags.
    merged = parameters.merge(cli_overrides=cli_overrides, params_file=file_params,
                              input_path=resolved_input.value if resolved_input else None,
                              outdir=outdir)
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

    # First, how the tree itself was resolved: running unreleased `dev` code (and, offline, a
    # possibly stale `dev` head) is said up front, so it is never mistaken for a release run.
    warnings = list(st.notes)
    warnings += _resume_advisory(outdir, st) if resume else []
    # Advisory only: preflight has confirmed nextflow is on PATH, so compare the installed
    # engine to the pipeline's declared requirement. Non-blocking — Nextflow is the authority
    # and enforces this itself at launch; we just surface it earlier with a clear message.
    warnings += engine_version.check(st.path, nxf_ver=nxf_overlay.get("NXF_VER"))
    # Same contract: advisory, never blocking. Explains a warning the pinned release will emit for a
    # reason that is invisible in its log, so it is not mistaken for a fault in the run or in nfclaw.
    warnings += plugin_compat.check(st.path)
    # Also advisory: a pinned plugin version with a known, inert bug (e.g. nf-core-utils@0.4.0's
    # spurious "positional argument `nextflow`" logged on every sarek run). Surfaced up front so the
    # log message arrives explained rather than re-investigated as a wrapper or samplesheet fault.
    warnings += plugin_compat.known_plugin_warnings(st.path)
    # Say them now, before Nextflow starts: a run can take hours, and one that fails never returns
    # its RunResult — an advisory that only arrives with the result arrives too late, or not at all.
    if on_warning is not None:
        for w in warnings:
            on_warning(w)

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
        try:
            outdir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:            # preflight judged writability; this is the authority
            raise NfclawError(ErrorCode.ENVIRONMENT,
                              f"--outdir could not be created: {exc.strerror or exc} "
                              f"({exc.filename or outdir})",
                              fix="Pass an --outdir in a directory you can write to.") from exc
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

    # If the pinned release still sets an nf-validation 1.x param that nf-schema 2.x removed (the
    # `plugin_compat` advisory above), add those names to nf-schema's `validation.ignoreParams` via a
    # generated `-c` config, so its inert "not a valid parameter" warning does not clutter the run.
    # The release tree stays byte-identical (drift-check green) and results are unaffected. Inserted
    # before any user `--config` so the caller can still override, and staged like the ceiling above
    # so `commands.sh` replays it. Harmless when the param is absent (e.g. a real run that loads no
    # test profile): ignoring a name that is never set is a no-op.
    compat_params = plugin_compat.removed_params_in_use(st.path)
    if compat_params:
        extra_configs.insert(0, plugin_compat.write_ignore_params_config(
            compat_params, staging / "nf_schema_compat.config"))

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
    # A local --input is an input whatever its declared format (mhcquant's carries none).
    if resolved_input is not None and resolved_input.local_path is not None:
        prov_inputs = list(dict.fromkeys([resolved_input.local_path, *prov_inputs]))

    def record(outcome: str) -> None:
        provenance.write(outdir=outdir, pipeline=name, command_str=cmd_str, submodule=st,
                         input_paths=prov_inputs, env_extra=nxf_overlay, outcome=outcome)

    # Launch from the outdir so each run owns its `.nextflow/` history and cache: `-resume` then
    # resumes THIS run, never another pipeline's session. Paths in the command are absolute, so
    # the cwd only decides where the engine state lands — including Nextflow's own log.
    # The run is recorded at a fixed place, `<outdir>/provenance/logs/run.log` (see runner.runlog):
    # nobody launching it, in the foreground or the background, has to redirect it or be told where.
    # Its last line states the outcome and is written last of all — after the bundle — because it
    # is what a background run is polled on.
    logs_dir = outdir / "provenance" / "logs"
    run_log = runlog.RunLog.open(logs_dir, command=cmd, launch_dir=outdir,
                                 nextflow_log=runlog.nextflow_log_path(outdir, nxf_overlay),
                                 notes=warnings)
    try:
        try:
            execution.run(cmd, cwd=outdir, logs_dir=logs_dir,
                          timeout_seconds=timeout_seconds, env_extra=nxf_overlay,
                          run_log=run_log)
        except BaseException:
            # A failed run is exactly when the bundle is needed most: `commands.sh` is what replays
            # the run once the cause is fixed, and the checksums record what it did manage to
            # produce. Write it, then re-raise — a provenance error must never replace the real
            # failure as the cause.
            if write_provenance:
                try:
                    record("failed")
                except Exception:                     # best effort; must not mask the real failure
                    pass
            raise
        run_log.outcome = "success"
        try:
            report = outputs.collect(outdir)
            if write_provenance:
                record("success")
        except BaseException as exc:
            # Nextflow succeeded but nfclaw could not finish (a full disk while hashing outputs, an
            # interrupt): the log's last line must not claim a success the bundle does not back.
            what = "interrupted" if isinstance(exc, KeyboardInterrupt) else "failed"
            run_log.fail(f"{what} after Nextflow succeeded ({type(exc).__name__}: {exc})",
                         f"nfclaw: {type(exc).__name__}: {exc}")
            if isinstance(exc, OSError):
                # Summarising the outputs and writing the bundle reads every result and writes
                # beside them: a full disk or an unreadable file is a clear error that says the
                # results exist, not a traceback that reads like the run itself crashed.
                raise NfclawError(
                    ErrorCode.ENVIRONMENT,
                    f"The run succeeded, but its provenance bundle could not be written: "
                    f"{exc.strerror or exc}" + (f" ({exc.filename})" if exc.filename else ""),
                    fix=f"The results are in {outdir}. Free disk space or fix the permission, then "
                        "rerun the same command with --resume: every task is reused from the cache "
                        "and the bundle is written.") from exc
            raise
    finally:
        run_log.finish()
    return RunResult(command=cmd_str, outdir=outdir, checked_only=False,
                     outputs_report=report, warnings=warnings,
                     log_path=logs_dir / runlog.RUN_LOG_NAME)
