import pathlib
import re
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


def _staged_params(res):
    """The params file the run's command actually names.

    `--check` stages it outside --outdir (a dry run must leave the output directory alone), so
    tests read it from the command rather than assuming a location.
    """
    import json
    return json.loads(pathlib.Path(
        re.search(r"-params-file (\S+)", res.command).group(1)).read_text())


def test_check_only_returns_command(tmp_path, monkeypatch):
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    assert res.checked_only and "nextflow" in res.command
    # The params file the printed command names must exist, so the command runs as printed...
    params = re.search(r"-params-file (\S+)", res.command).group(1)
    assert pathlib.Path(params).is_file()
    # ...but it must NOT be staged inside --outdir: `--check` launches nothing, so it has to leave
    # the output directory exactly as it found it. Creating it, or dropping a provenance/ directory
    # in it, made the next real run fail the "--outdir is not empty" guard over an empty result set.
    assert not (tmp_path / "out").exists()


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


def test_failed_run_still_writes_the_provenance_bundle(tmp_path, monkeypatch):
    # The replay script matters most after a failure — that is when the run gets fixed and retried.
    import json

    import pytest

    from runner.errors import ErrorCode, NfclawError

    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])

    def boom(*a, **k):
        raise NfclawError(ErrorCode.EXECUTION_FAILED, "Nextflow exited 1")

    monkeypatch.setattr(orchestration.execution, "run", boom)
    with pytest.raises(NfclawError, match="Nextflow exited 1"):   # the real cause still surfaces
        orchestration.run_pipeline(
            "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
            profile="docker", params_file=None, cli_overrides={}, resume=False,
            demo=True, check_only=False, write_provenance=True, timeout_seconds=10)
    prov = tmp_path / "out" / "provenance"
    assert (prov / "commands.sh").exists()                       # replayable once the cause is fixed
    assert json.loads((prov / "run_manifest.json").read_text())["outcome"] == "failed"


def test_provenance_failure_never_masks_the_run_failure(tmp_path, monkeypatch):
    import pytest

    from runner.errors import ErrorCode, NfclawError

    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])

    def boom(*a, **k):
        raise NfclawError(ErrorCode.EXECUTION_FAILED, "Nextflow exited 1")

    def prov_boom(*a, **k):
        raise OSError("disk full")

    monkeypatch.setattr(orchestration.execution, "run", boom)
    monkeypatch.setattr(orchestration.provenance, "write", prov_boom)
    with pytest.raises(NfclawError, match="Nextflow exited 1"):
        orchestration.run_pipeline(
            "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
            profile="docker", params_file=None, cli_overrides={}, resume=False,
            demo=True, check_only=False, write_provenance=True, timeout_seconds=10)


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


def test_relative_nxf_work_is_resolved_before_nextflow_changes_cwd(tmp_path, monkeypatch):
    root = _make_pipeline(tmp_path / "repo", "mini")
    caller = tmp_path / "caller"
    caller.mkdir()
    monkeypatch.chdir(caller)
    seen = {}
    monkeypatch.setattr(orchestration.preflight, "check_environment",
                        lambda **k: seen.update(k) or [])
    result = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10,
        nxf_env={"NXF_WORK": "scratch/work"})
    expected = (caller / "scratch/work").resolve()
    assert seen["work_dir"] == expected
    assert f"-work-dir {expected}" in result.command


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
            "mini", repo_root=root, input_path="https://example.test/samplesheet.csv",
            outdir=tmp_path / "out",
            profile="singularity", params_file=None, cli_overrides={}, resume=False,
            demo=False, check_only=True, write_provenance=False, timeout_seconds=10)
    assert exc.value.code == ErrorCode.ENVIRONMENT
    assert any("space" in i for i in exc.value.details["issues"])


def _healthy_env(monkeypatch):
    # real preflight, but tools present and docker daemon healthy, so only the rule under test fires
    monkeypatch.setattr(orchestration.preflight.shutil, "which", lambda x: "/usr/bin/" + x)
    monkeypatch.setattr(orchestration.preflight.subprocess, "run",
                        lambda *a, **k: type("R", (), {"returncode": 0, "stdout": "", "stderr": ""})())


def test_check_only_allows_nonempty_outdir(tmp_path, monkeypatch):
    # --check validates without launching, so an existing (non-empty) results dir must not block it.
    root = _make_pipeline(tmp_path / "repo", "mini")
    _healthy_env(monkeypatch)
    out = tmp_path / "out"                                    # outside the repo
    out.mkdir()
    (out / "prev.txt").write_text("a previous run's results")
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=out,
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    assert res.checked_only and "nextflow" in res.command


def test_full_run_still_blocks_nonempty_outdir(tmp_path, monkeypatch):
    # The guard is intact for an actual run: a non-empty outdir without --resume is rejected.
    import pytest
    from runner.errors import ErrorCode, NfclawError
    root = _make_pipeline(tmp_path / "repo", "mini")
    _healthy_env(monkeypatch)
    out = tmp_path / "out"
    out.mkdir()
    (out / "prev.txt").write_text("a previous run's results")
    with pytest.raises(NfclawError) as exc:
        orchestration.run_pipeline(
            "mini", repo_root=root, input_path=None, outdir=out,
            profile="docker", params_file=None, cli_overrides={}, resume=False,
            demo=True, check_only=False, write_provenance=False, timeout_seconds=10)
    assert exc.value.code == ErrorCode.ENVIRONMENT
    assert any("not empty" in i for i in exc.value.details["issues"])


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


def test_obsolete_validation_param_injects_ignoreparams_config(tmp_path, monkeypatch):
    # A pinned release that declares nf-schema 2.x but still sets an nf-validation 1.x param gets a
    # generated `-c` config that neutralises the inert "not a valid parameter" warning — without
    # editing the release tree. The staged file lists the param under validation.ignoreParams.
    root = _make_pipeline(tmp_path, "mini")
    up = root / "pipelines" / "mini" / "upstream"
    (up / "nextflow.config").write_text("plugins { id 'nf-schema@2.5.1' }\n")
    (up / "conf").mkdir()
    (up / "conf" / "test.config").write_text(
        "params {\n    validationSchemaIgnoreParams = 'genomes'\n}\n")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    m = re.search(r"-c (\S+nf_schema_compat\.config)", res.command)
    assert m, res.command
    assert "validationSchemaIgnoreParams" in Path(m.group(1)).read_text()


def test_clean_release_injects_no_compat_config(tmp_path, monkeypatch):
    # The default fixture declares no such plugin/param, so no compat `-c` is added — the injection
    # is confined to the actual nf-schema-2.x-plus-1.x-param defect.
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    assert "nf_schema_compat.config" not in res.command


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


def test_url_input_skips_local_validation_and_is_forwarded(tmp_path, monkeypatch):
    # A remote --input (URL) can't be read locally, so it must skip the samplesheet pre-check and be
    # forwarded to Nextflow unchanged (nf-schema stages + validates it). Mirrors nf-core behavior.
    import json
    from runner.schema import Column, InputSchema
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    # Force a non-None input schema so the ONLY thing that skips the pre-check is the URL (str) type.
    monkeypatch.setattr(orchestration.schema_mod, "load_input_schema",
                        lambda repo: InputSchema(columns=(Column("sample", "string", True, None, None),)))
    called = {}
    monkeypatch.setattr(orchestration.samplesheet, "validate",
                        lambda *a, **k: called.setdefault("validated", True) or [])
    url = "https://raw.githubusercontent.com/nf-core/x/samplesheet.csv"
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=url, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=False, check_only=True, write_provenance=False, timeout_seconds=10)
    assert "validated" not in called                          # local pre-check skipped for a URL
    params = _staged_params(res)
    assert params["input"] == url                             # forwarded unchanged, not mangled


def test_missing_params_file_fails_fast(tmp_path, monkeypatch):
    # A --params-file the user named but that doesn't exist must fail fast, not be silently
    # dropped (which would run with none of its values). Mirrors the --config contract.
    import pytest
    from runner.errors import ErrorCode, NfclawError
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    ran: dict = {}
    monkeypatch.setattr(orchestration.execution, "run", lambda *a, **k: ran.setdefault("x", True))
    with pytest.raises(NfclawError) as exc:
        orchestration.run_pipeline(
            "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
            profile="docker", params_file=Path("/no/such/params.json"), cli_overrides={},
            resume=False, demo=True, check_only=False, write_provenance=False, timeout_seconds=10)
    assert exc.value.code == ErrorCode.PARAMS_INVALID and "params-file" in str(exc.value).lower()
    assert "x" not in ran                                         # never reached execution


def test_existing_params_file_is_used(tmp_path, monkeypatch):
    # The happy path still works: an existing params-file is read and its values reach the run.
    import json
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    pf = tmp_path / "p.json"
    pf.write_text('{"aligner": "hisat2"}')
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=pf, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    params = _staged_params(res)
    assert params["aligner"] == "hisat2"


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
    res = orchestration.run_pipeline(
        "boolp", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={"skip_busco": "true"},
        resume=False, demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    params = _staged_params(res)
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


def test_missing_required_param_rejected_before_preflight(tmp_path, monkeypatch):
    import pytest
    from runner.errors import ErrorCode, NfclawError
    root = _make_pipeline(tmp_path, "mini")
    reached_preflight = {}
    monkeypatch.setattr(orchestration.preflight, "check_environment",
                        lambda **k: reached_preflight.setdefault("x", True) or [])
    with pytest.raises(NfclawError) as exc:
        orchestration.run_pipeline(
            "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
            profile="docker", params_file=None, cli_overrides={}, resume=False,
            demo=False, check_only=True, write_provenance=False, timeout_seconds=10)
    assert exc.value.code == ErrorCode.PARAMS_INVALID
    assert "missing required parameter '--input'" in str(exc.value)
    assert "x" not in reached_preflight


def test_demo_allows_required_input_to_come_from_test_profile(tmp_path, monkeypatch):
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    assert res.checked_only and "-profile test,docker" in res.command


def _pipeline_with_report_suffix(tmp_path, name="mini"):
    """`mini`, plus the nf-core template's trace_report_suffix parameter."""
    import json

    root = _make_pipeline(tmp_path, name)
    schema_path = root / "pipelines" / name / "upstream" / "nextflow_schema.json"
    data = json.loads(schema_path.read_text())
    data["definitions"]["generic_options"] = {
        "title": "Generic options",
        "properties": {"trace_report_suffix": {"type": "string", "hidden": True}},
    }
    schema_path.write_text(json.dumps(data))
    return root


def test_resource_limits_become_a_config_passed_to_nextflow(tmp_path, monkeypatch):
    # nf-core's documented ceiling: a process.resourceLimits config handed to Nextflow with -c.
    from runner import resources

    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10,
        limits=resources.parse(4, "15.GB", "1.h"))
    cfg = pathlib.Path(re.search(r"-c (\S+)", res.command).group(1))
    assert cfg.name == "resource_limits.config"
    assert cfg.is_file() and "resourceLimits" in cfg.read_text()
    assert cfg.parent == pathlib.Path(
        re.search(r"-params-file (\S+)", res.command).group(1)).parent   # staged with the params


def test_no_config_is_generated_when_no_limit_is_given(tmp_path, monkeypatch):
    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    assert "-c " not in res.command
    assert not (tmp_path / "out").exists()             # --check stages nothing in the outdir


def test_an_explicit_config_still_overrides_the_generated_ceiling(tmp_path, monkeypatch):
    # Nextflow lets a later -c win, so the user's own file must come after the generated one.
    from runner import resources

    root = _make_pipeline(tmp_path, "mini")
    mine = tmp_path / "mine.config"
    mine.write_text("process { resourceLimits = [ cpus: 2 ] }\n")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10,
        configs=[str(mine)], limits=resources.parse(4, None, None))
    generated = re.search(r"-c (\S*resource_limits\.config)", res.command).group(1)
    assert res.command.index(generated) < res.command.index(str(mine))


def test_report_suffix_is_pinned_so_the_replay_reproduces_the_run(tmp_path, monkeypatch):
    # Without this the pipeline re-evaluates `now()` on every launch and the replay writes a second,
    # differently-named set of reports rather than reproducing the original run's outputs.
    import json

    root = _pipeline_with_report_suffix(tmp_path)
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    monkeypatch.setattr(orchestration.execution, "run", lambda *a, **k: None)
    orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=False, write_provenance=True, timeout_seconds=10)
    params = json.loads((tmp_path / "out" / "provenance" / "params.json").read_text())
    suffix = params["trace_report_suffix"]
    assert suffix and suffix != ""
    # commands.sh replays through the same params file, so the replay reuses this exact suffix.
    replay = (tmp_path / "out" / "provenance" / "commands.sh").read_text()
    assert str(tmp_path / "out" / "provenance" / "params.json") in replay


def test_a_release_without_the_report_suffix_param_is_untouched(tmp_path, monkeypatch):
    # Older releases predate the parameter — passing it would fail nf-schema validation.
    import json

    root = _make_pipeline(tmp_path, "mini")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    res = orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=tmp_path / "out",
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    assert "trace_report_suffix" not in _staged_params(res)


def test_check_leaves_an_existing_outdir_untouched(tmp_path, monkeypatch):
    # The reported failure in full: --check against a results directory must not add anything to it.
    root = _make_pipeline(tmp_path, "mini")
    out = tmp_path / "out"
    out.mkdir()
    (out / "results.txt").write_text("a previous run")
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=out,
        profile="docker", params_file=None, cli_overrides={}, resume=False,
        demo=True, check_only=True, write_provenance=False, timeout_seconds=10)
    assert [p.name for p in out.iterdir()] == ["results.txt"]      # nothing added


def test_a_real_run_after_a_check_is_not_blocked_as_non_empty(tmp_path, monkeypatch):
    # The end-to-end regression, asserted against the REAL preflight guard: after a --check, the
    # output directory must still look untouched to it, so the next real run is not refused.
    from runner import preflight

    root = _make_pipeline(tmp_path, "mini")
    out = tmp_path / "out"                       # outside the repo root, as a real --outdir is
    monkeypatch.setattr(orchestration.preflight, "check_environment", lambda **k: [])
    orchestration.run_pipeline(
        "mini", repo_root=root, input_path=None, outdir=out, profile="docker",
        params_file=None, cli_overrides={}, resume=False, demo=True, check_only=True,
        write_provenance=False, timeout_seconds=10)
    st = submodule.resolve("mini", root / "pipelines")
    issues = preflight.check_environment(
        profile="docker", output_dir=out, submodule=st, repo_root=tmp_path / "repo",
        resume=False, check_only=False, allow_spaces=True)
    assert not any("not empty" in i for i in issues), issues
