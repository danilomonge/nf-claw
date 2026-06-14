from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from runner import (discovery, execution, nextflow_command, outputs,
                    parameters, preflight, provenance, samplesheet)
from runner import schema as schema_mod
from runner import submodule as submod
from runner.errors import ErrorCode, NfclawError


@dataclass
class RunResult:
    command: str
    outdir: Path
    checked_only: bool
    outputs_report: "outputs.OutputsReport | None"


def run_pipeline(name: str, *, repo_root: Path, input_path: Path | None,
                 outdir: Path, profile: str, params_file: Path | None,
                 cli_overrides: dict, resume: bool, demo: bool,
                 check_only: bool, write_provenance: bool,
                 timeout_seconds: int) -> RunResult:
    pipelines_dir = repo_root / "pipelines"
    discovery.find(name, pipelines_dir)                       # 404 if unknown
    st = submod.ensure_initialized(name, pipelines_dir, repo_root)
    param_schema = schema_mod.load_param_schema(st.path)
    input_schema = schema_mod.load_input_schema(st.path)

    if input_path is not None and input_schema is not None:
        problems = samplesheet.validate(input_path, input_schema)
        if problems:
            raise NfclawError(ErrorCode.SAMPLESHEET_INVALID,
                              "Samplesheet failed validation.",
                              details={"issues": problems})

    for warning in parameters.typo_warnings(cli_overrides, param_schema):
        print(f"WARNING: {warning}")

    composed_profile = nextflow_command.compose_profile(profile, demo=demo)
    issues = preflight.check_environment(profile=composed_profile, output_dir=outdir,
                                         submodule=st, repo_root=repo_root, resume=resume)
    if issues:
        raise NfclawError(ErrorCode.ENVIRONMENT, "Preflight checks failed.",
                          details={"issues": issues})

    outdir.mkdir(parents=True, exist_ok=True)
    params_file_out = parameters.compose(
        cli_overrides=cli_overrides, params_file=params_file, schema=param_schema,
        outdir=outdir, input_path=input_path, dest=outdir / "provenance" / "params.json")

    cmd, cmd_str = nextflow_command.build(upstream=st.path, profile=composed_profile,
                                          params_file=params_file_out, resume=resume)
    if check_only:
        return RunResult(command=cmd_str, outdir=outdir, checked_only=True,
                         outputs_report=None)

    execution.run(cmd, cwd=repo_root, logs_dir=outdir / "provenance" / "logs",
                  timeout_seconds=timeout_seconds)
    report = outputs.collect(outdir)
    if write_provenance:
        provenance.write(outdir=outdir, pipeline=name, command_str=cmd_str, submodule=st,
                         input_paths=[p for p in (input_path,) if p], schema=param_schema)
    return RunResult(command=cmd_str, outdir=outdir, checked_only=False,
                     outputs_report=report)
