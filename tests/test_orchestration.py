import shutil
from pathlib import Path

from runner import orchestration, submodule


def _make_pipeline(tmp_path, name):
    up = tmp_path / "pipelines" / name / "upstream"
    up.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config"):
        (up / f).write_text("x")
    fix = Path(__file__).parent / "fixtures" / name / "nextflow_schema.json"
    shutil.copy(fix, up / "nextflow_schema.json")
    (tmp_path / "pipelines" / name / "skill.md").write_text(f"---\nname: {name}\n---\n")
    return tmp_path


def test_check_only_returns_command(tmp_path, monkeypatch):
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    assert res.checked_only and "nextflow" in res.command
    assert (tmp_path / "out" / "provenance" / "params.json").exists()


def test_full_run_invokes_execution(tmp_path, monkeypatch):
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    called = {}
    monkeypatch.setattr(orchestration.execution, "run",
                        lambda *a, **k: called.setdefault("ran", True))
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=False, write_provenance=True, timeout_seconds=10)
    assert called.get("ran") and not res.checked_only


def test_pipeline_version_routed_through_versions_ensure(tmp_path, monkeypatch):
    # A requested version is resolved/materialized via versions.ensure; everything downstream
    # (schema, validation, command) then targets whatever tree it returns.
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    captured = {}

    def fake_ensure(name, version, *, pipelines_dir, repo_root):
        captured["version"] = version
        return submodule.resolve_at(name, pipelines_dir / name / "upstream")

    monkeypatch.setattr(orchestration.versions, "ensure", fake_ensure)
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10,
        pipeline_version="1.2.0")
    assert captured["version"] == "1.2.0"
    assert "nextflow" in res.command


def test_default_run_uses_no_version(tmp_path, monkeypatch):
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    captured = {}

    def fake_ensure(name, version, *, pipelines_dir, repo_root):
        captured["version"] = version
        return submodule.resolve_at(name, pipelines_dir / name / "upstream")

    monkeypatch.setattr(orchestration.versions, "ensure", fake_ensure)
    orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    assert captured["version"] is None                          # default = pinned latest


def test_invalid_param_rejected_before_execution(tmp_path, monkeypatch):
    import pytest
    from runner.errors import ErrorCode, NfclawError
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    ran: dict = {}
    monkeypatch.setattr(orchestration.execution, "run", lambda *a, **k: ran.setdefault("x", True))
    with pytest.raises(NfclawError) as exc:
        orchestration.run_pipeline(
            "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
            profile="docker", params_file=None, cli_overrides={"aligner": "bowtie"},  # not in enum
            resume=False, demo=True, check_only=False, write_provenance=False, timeout_seconds=10)
    assert exc.value.code == ErrorCode.PARAMS_INVALID
    assert "x" not in ran                                         # never reached execution
    assert any("must be one of" in i for i in exc.value.details["issues"])
