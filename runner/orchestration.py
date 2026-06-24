from __future__ import annotations

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
                 timeout_seconds: int, pipeline_version: str | None = None) -> RunResult:
    pipelines_dir = repo_root / "pipelines"
    discovery.find(name, pipelines_dir)                       # 404 if unknown
    # None → pinned latest (unchanged); a tag → that release, validated + materialized.
    # Everything downstream consumes `st`/`st.path`, so it all targets the chosen version.
    st = versions.ensure(name, pipeline_version, pipelines_dir=pipelines_dir,
                         repo_root=repo_root)
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
    param_errors = parameters.validate_params(merged, param_schema)
    if param_errors:
        raise NfclawError(ErrorCode.PARAMS_INVALID,
                          "Parameters failed validation (fix before running).",
                          fix="Use parameter names and allowed values from reference.md.",
                          details={"issues": param_errors})

    composed_profile = nextflow_command.compose_profile(profile, demo=demo)
    issues = preflight.check_environment(profile=composed_profile, output_dir=outdir,
                                         submodule=st, repo_root=repo_root, resume=resume)
    if issues:
        raise NfclawError(ErrorCode.ENVIRONMENT, "Preflight checks failed.",
                          details={"issues": issues})

    # Advisory only: preflight has confirmed nextflow is on PATH, so compare the installed
    # engine to the pipeline's declared requirement. Non-blocking — Nextflow is the authority
    # and enforces this itself at launch; we just surface it earlier with a clear message.
    warnings = engine_version.check(st.path)

    outdir.mkdir(parents=True, exist_ok=True)
    resolved = parameters.resolve_path_params(merged, param_schema)
    params_file_out = parameters.write_params_file(resolved, outdir / "provenance" / "params.json")

    cmd, cmd_str = nextflow_command.build(upstream=st.path, profile=composed_profile,
                                          params_file=params_file_out, resume=resume)
    if check_only:
        return RunResult(command=cmd_str, outdir=outdir, checked_only=True,
                         outputs_report=None, warnings=warnings)

    execution.run(cmd, cwd=repo_root, logs_dir=outdir / "provenance" / "logs",
                  timeout_seconds=timeout_seconds)
    report = outputs.collect(outdir)
    if write_provenance:
        refs = param_schema.reference_path_params()
        prov_inputs = [Path(v) for k, v in resolved.items()
                       if k in refs and k != "outdir" and isinstance(v, str) and "://" not in v]
        provenance.write(outdir=outdir, pipeline=name, command_str=cmd_str, submodule=st,
                         input_paths=prov_inputs)
    return RunResult(command=cmd_str, outdir=outdir, checked_only=False,
                     outputs_report=report, warnings=warnings)
