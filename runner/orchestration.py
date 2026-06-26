from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from runner import (discovery, engine_version, execution, nextflow_command,
                    outputs, parameters, preflight, provenance, samplesheet, versions)
from runner import schema as schema_mod
from runner.errors import ErrorCode, NfclawError


@dataclass
class RunResult:
    command: str
    outdir: Path
    checked_only: bool
    outputs_report: "outputs.OutputsReport | None"
    warnings: list[str] = field(default_factory=list)


def run_pipeline(name: str, *, repo_root: Path, input_path: Path | None,
                 outdir: Path, profile: str, params_file: Path | None,
                 cli_overrides: dict, resume: bool, demo: bool,
                 check_only: bool, write_provenance: bool,
                 timeout_seconds: int, pipeline_version: str | None = None,
                 nxf_ver: str | None = None,
                 nxf_env: dict[str, str] | None = None,
                 allow_spaces: bool = False,
                 configs: tuple[str, ...] | list[str] = ()) -> RunResult:
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
    # else Nextflow's default of <cwd>/work — cwd is the repo root. Used by the space check.
    work_dir = Path(nxf_overlay.get("NXF_WORK") or os.environ.get("NXF_WORK")
                    or repo_root / "work")
    param_schema = schema_mod.load_param_schema(st.path)
    input_schema = schema_mod.load_input_schema(st.path)

    if input_path is not None and input_schema is not None:
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
    param_errors = parameters.validate_params(merged, param_schema)
    if param_errors:
        raise NfclawError(ErrorCode.PARAMS_INVALID,
                          "Parameters failed validation (fix before running).",
                          fix="Use parameter names and allowed values from reference.md.",
                          details={"issues": param_errors})

    composed_profile = nextflow_command.compose_profile(profile, demo=demo)
    issues = preflight.check_environment(profile=composed_profile, output_dir=outdir,
                                         submodule=st, repo_root=repo_root, resume=resume,
                                         work_dir=work_dir, allow_spaces=allow_spaces)
    if issues:
        raise NfclawError(ErrorCode.ENVIRONMENT, "Preflight checks failed.",
                          details={"issues": issues})

    # Advisory only: preflight has confirmed nextflow is on PATH, so compare the installed
    # engine to the pipeline's declared requirement. Non-blocking — Nextflow is the authority
    # and enforces this itself at launch; we just surface it earlier with a clear message.
    warnings = engine_version.check(st.path, nxf_ver=nxf_overlay.get("NXF_VER"))

    outdir.mkdir(parents=True, exist_ok=True)
    resolved = parameters.resolve_path_params(merged, param_schema)
    params_file_out = parameters.write_params_file(resolved, outdir / "provenance" / "params.json")

    # Pass the work dir explicitly so it stays off the outdir (shared, content-hashed — fine),
    # and any extra `-c` configs. nfclaw launches Nextflow from the outdir (below) so each run
    # gets its own .nextflow/ state, but the work dir must not move into the results.
    cmd, cmd_str = nextflow_command.build(upstream=st.path, profile=composed_profile,
                                          params_file=params_file_out, resume=resume,
                                          work_dir=work_dir, extra_configs=tuple(extra_configs))
    if check_only:
        return RunResult(command=cmd_str, outdir=outdir, checked_only=True,
                         outputs_report=None, warnings=warnings)

    # Launch from the outdir so each run owns its `.nextflow/` history and cache: `-resume` then
    # resumes THIS run, never another pipeline's session. Paths in the command are absolute, so
    # the cwd only decides where the engine state lands.
    execution.run(cmd, cwd=outdir, logs_dir=outdir / "provenance" / "logs",
                  timeout_seconds=timeout_seconds, env_extra=nxf_overlay)
    report = outputs.collect(outdir)
    if write_provenance:
        refs = param_schema.reference_path_params()
        prov_inputs = [Path(v) for k, v in resolved.items()
                       if k in refs and k != "outdir" and isinstance(v, str) and "://" not in v]
        provenance.write(outdir=outdir, pipeline=name, command_str=cmd_str, submodule=st,
                         input_paths=prov_inputs, env_extra=nxf_overlay)
    return RunResult(command=cmd_str, outdir=outdir, checked_only=False,
                     outputs_report=report, warnings=warnings)
