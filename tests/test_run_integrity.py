import json
import hashlib

import pytest

from runner import cli, orchestration, resources
from runner.errors import ErrorCode, NfclawError


def test_overlapping_resume_cannot_overwrite_active_run(library, tmp_path, monkeypatch):
    root = library("mini")
    outdir = tmp_path / "results"
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **kwargs: [])
    monkeypatch.setattr(orchestration.engine_version, "check", lambda *args, **kwargs: [])
    entered = []

    def launch(*args, **kwargs):
        entered.append(True)
        if len(entered) == 1:
            with pytest.raises(NfclawError, match="another nfclaw run") as exc:
                orchestration.run_pipeline(
                    "mini", repo_root=root, input_path=None, outdir=outdir,
                    profile="docker", params_file=None, cli_overrides={"aligner": "hisat2"},
                    resume=True, demo=True, check_only=False, write_provenance=False,
                    timeout_seconds=None)
            assert exc.value.code == ErrorCode.ENVIRONMENT

    monkeypatch.setattr(orchestration.execution, "run", launch)
    orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=outdir,
        profile="docker", params_file=None, cli_overrides={"aligner": "star"},
        resume=False, demo=True, check_only=False, write_provenance=False,
        timeout_seconds=None)
    assert len(entered) == 1
    assert json.loads((outdir / "provenance" / "params.json").read_text())["aligner"] == "star"


@pytest.mark.parametrize("value", ["0.GB", "0.0 MB"])
def test_zero_memory_limit_is_refused(value):
    with pytest.raises(NfclawError, match="--limit-memory"):
        resources.parse(None, value, None)


@pytest.mark.parametrize("value", ["0.h", "0.0 ms"])
def test_zero_time_limit_is_refused(value):
    with pytest.raises(NfclawError, match="--limit-time"):
        resources.parse(None, None, value)


def test_environment_nul_is_refused_before_subprocess_launch():
    with pytest.raises(NfclawError, match="NXF_JVM_ARGS"):
        resources.parse_nxf_env({"NXF_JVM_ARGS": "value\x00broken"})


def test_strict_verification_rejects_changed_scientific_result(tmp_path, monkeypatch):
    original, replay = tmp_path / "original", tmp_path / "replay"
    for out, text in ((original, "chr1\t10\tA\tG\n"), (replay, "chr1\t10\tA\tT\n")):
        out.mkdir()
        (out / "calls.tsv").write_text(text)
    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)
    assert cli.main(["verify", str(replay), "--against", str(original), "--strict"]) == 1


def test_provenance_snapshots_sheet_data_and_config_before_execution(library, tmp_path, monkeypatch):
    root = library("mini")
    data = tmp_path / "reads.fastq.gz"
    data.write_bytes(b"original reads")
    sheet = tmp_path / "samples.csv"
    sheet.write_text(f"sample,fastq_1\nsample1,{data}\n")
    config = tmp_path / "analysis.config"
    original_config = b"params.aligner = 'star'\n"
    config.write_bytes(original_config)
    outdir = tmp_path / "results"
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **kwargs: [])
    monkeypatch.setattr(orchestration.engine_version, "check", lambda *args, **kwargs: [])
    monkeypatch.setattr(orchestration.provenance, "_nextflow_version", lambda *args: "test")

    def launch(*args, **kwargs):
        data.write_bytes(b"changed reads")
        config.write_bytes(b"params.aligner = 'hisat2'\n")

    monkeypatch.setattr(orchestration.execution, "run", launch)
    orchestration.run_pipeline(
        "mini", repo_root=root, input_path=sheet, outdir=outdir,
        profile="docker", params_file=None, cli_overrides={}, configs=[str(config)],
        resume=False, demo=False, check_only=False, write_provenance=True,
        timeout_seconds=None)
    assert f"{hashlib.sha256(b'original reads').hexdigest()}  {data}" in (
        outdir / "provenance" / "inputs.sha256").read_text()
    assert f"{hashlib.sha256(original_config).hexdigest()}  {config}" in (
        outdir / "provenance" / "configs.sha256").read_text()


def test_planned_pipeline_tree_is_reused_for_check(library, tmp_path, monkeypatch):
    root = library("mini")
    planned = orchestration.versions.ensure(
        "mini", None, pipelines_dir=root / "pipelines", repo_root=root)

    def unexpected_resolution(*args, **kwargs):
        pytest.fail("a frozen chain must not resolve its pipeline version a second time")

    monkeypatch.setattr(orchestration.versions, "ensure", unexpected_resolution)
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **kwargs: [])
    monkeypatch.setattr(orchestration.engine_version, "check", lambda *args, **kwargs: [])
    result = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "results",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False,
        timeout_seconds=None, resolved_tree=planned)
    assert str(planned.path) in result.command
