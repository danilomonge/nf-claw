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


def test_passes_effective_work_dir_and_allow_spaces_to_preflight(tmp_path, monkeypatch):
    from pathlib import Path
    root = _make_pipeline(tmp_path, "mini")
    seen = {}
    monkeypatch.setattr(orchestration.preflight, "check_environment",
                        lambda **k: seen.update(k) or [])
    monkeypatch.setattr(orchestration.execution, "run", lambda *a, **k: None)
    orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=False, write_provenance=False, timeout_seconds=10,
        nxf_env={"NXF_WORK": "/scratch/work"}, allow_spaces=True)
    assert seen["work_dir"] == Path("/scratch/work")          # NXF_WORK overlay wins
    assert seen["allow_spaces"] is True


def test_work_dir_defaults_under_repo_when_no_nxf_work(tmp_path, monkeypatch):
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.delenv("NXF_WORK", raising=False)
    seen = {}
    monkeypatch.setattr(orchestration.preflight, "check_environment",
                        lambda **k: seen.update(k) or [])
    monkeypatch.setattr(orchestration.execution, "run", lambda *a, **k: None)
    orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    assert seen["work_dir"] == root / "work"                  # Nextflow default: <cwd>/work


def test_space_in_repo_path_blocks_the_run(tmp_path, monkeypatch):
    import pytest
    from runner.errors import ErrorCode, NfclawError
    root = _make_pipeline(tmp_path / "draft 2", "mini")        # repo path has a space
    # real preflight, but isolate from tool/daemon checks so only the space rule can fire
    monkeypatch.setattr(orchestration.preflight.shutil, "which", lambda x: "/usr/bin/" + x)
    monkeypatch.setattr(orchestration.preflight.subprocess, "run",
                        lambda *a, **k: type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    with pytest.raises(NfclawError) as exc:
        orchestration.run_pipeline(
            "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
            profile="singularity", params_file=None, cli_overrides={}, resume=False,
            demo=False, check_only=True, write_provenance=False, timeout_seconds=10)
    assert exc.value.code == ErrorCode.ENVIRONMENT
    assert any("space" in i for i in exc.value.details["issues"])


def test_configs_passed_to_build_as_extra_configs(tmp_path, monkeypatch):
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    cfg = tmp_path / "extra.config"
    cfg.write_text("docker { runOptions = '--network host' }\n")
    seen = {}
    real_build = orchestration.nextflow_command.build
    monkeypatch.setattr(orchestration.nextflow_command, "build",
                        lambda **k: (seen.update(k), real_build(**k))[1])
    orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10,
        configs=[str(cfg)])
    assert seen["extra_configs"] == (cfg.resolve(),)              # resolved to absolute, passed as -c


def test_missing_config_fails_fast(tmp_path, monkeypatch):
    import pytest
    from runner.errors import ErrorCode, NfclawError
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    with pytest.raises(NfclawError) as exc:
        orchestration.run_pipeline(
            "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
            profile="docker", params_file=None, cli_overrides={}, resume=False,
            demo=True, check_only=True, write_provenance=False, timeout_seconds=10,
            configs=["/no/such/file.config"])
    assert exc.value.code == ErrorCode.ENVIRONMENT and "config" in str(exc.value).lower()


def test_runs_from_outdir_with_shared_work_dir(tmp_path, monkeypatch):
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    monkeypatch.delenv("NXF_WORK", raising=False)
    eseen, bseen = {}, {}
    monkeypatch.setattr(orchestration.execution, "run", lambda *a, **k: eseen.update(k))
    real_build = orchestration.nextflow_command.build
    monkeypatch.setattr(orchestration.nextflow_command, "build",
                        lambda **k: (bseen.update(k), real_build(**k))[1])
    orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=False, write_provenance=False, timeout_seconds=10)
    assert eseen["cwd"] == tmp_path / "out"                       # isolates .nextflow/ per run
    assert bseen["work_dir"] == root / "work"                    # work stays shared, off the outdir


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


def test_nxf_overlay_flows_to_execution_and_provenance(tmp_path, monkeypatch):
    import json
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    seen = {}
    monkeypatch.setattr(orchestration.execution, "run",
                        lambda *a, **k: seen.update({"exec_env": k.get("env_extra")}))
    # stub the version probe so the provenance step doesn't invoke real `nextflow -version` with
    # NXF_VER set (which would try to fetch that engine — execution.run is mocked here).
    monkeypatch.setattr(orchestration.provenance, "_nextflow_version", lambda env_extra=None: "stub")
    orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=False, write_provenance=True, timeout_seconds=10,
        nxf_ver="25.10.2", nxf_env={"NXF_JVM_ARGS": "-Dx=y"})
    overlay = {"NXF_JVM_ARGS": "-Dx=y", "NXF_VER": "25.10.2"}
    assert seen["exec_env"] == overlay                                    # applied to the nextflow subprocess
    manifest = json.loads((tmp_path / "out" / "provenance" / "run_manifest.json").read_text())
    assert manifest["nextflow_env"] == overlay                           # and recorded for reproducibility


def test_nxf_ver_makes_engine_check_judge_the_pin(tmp_path, monkeypatch):
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    monkeypatch.setattr(orchestration.execution, "run", lambda *a, **k: None)
    seen = {}

    def fake_check(upstream, **k):
        seen["nxf_ver"] = k.get("nxf_ver")
        return []                                             # check() always returns list[str]

    monkeypatch.setattr(orchestration.engine_version, "check", fake_check)
    orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=False, write_provenance=False, timeout_seconds=10,
        nxf_ver="25.10.2")
    assert seen["nxf_ver"] == "25.10.2"


def _make_pipeline_with_bool(tmp_path, name="boolp"):
    import json
    up = tmp_path / "pipelines" / name / "upstream"
    up.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config"):
        (up / f).write_text("x")
    (up / "nextflow_schema.json").write_text(json.dumps({"definitions": {"io": {"properties": {
        "outdir": {"type": "string", "format": "directory-path"},
        "skip_busco": {"type": "boolean"}}}}}))
    (tmp_path / "pipelines" / name / "skill.md").write_text(f"---\nname: {name}\n---\n")
    return tmp_path


def test_boolean_cli_string_is_coerced_in_params_file(tmp_path, monkeypatch):
    import json
    root = _make_pipeline_with_bool(tmp_path)
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    orchestration.run_pipeline(
        "boolp", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={"skip_busco": "true"},
        resume=False, demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    params = json.loads((tmp_path / "out" / "provenance" / "params.json").read_text())
    assert params["skip_busco"] is True                       # CLI "true" → real boolean for nf-schema


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
