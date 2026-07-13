import json

from runner import provenance
from runner.submodule import SubmoduleStatus


def _st(path):
    return SubmoduleStatus("mini", path, True, True, "1.0.0", "deadbeef", ())


def test_writes_manifest_and_checksums(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "result.txt").write_text("data")
    inp = tmp_path / "ss.csv"
    inp.write_text("sample\nA\n")
    prov = provenance.write(outdir=out, pipeline="mini", command_str="nextflow run x",
                            submodule=_st(tmp_path / "up"), input_paths=[inp])
    manifest = json.loads((prov / "run_manifest.json").read_text())
    assert manifest["commit"] == "deadbeef" and manifest["version"] == "1.0.0"
    assert "result.txt" in (prov / "outputs.sha256").read_text()
    assert (prov / "commands.sh").exists()


def test_defensive_without_pipeline_info(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    prov = provenance.write(outdir=out, pipeline="mini", command_str="x",
                            submodule=_st(tmp_path / "up"), input_paths=[])
    assert (prov / "run_manifest.json").exists()


def test_excludes_nextflow_internals(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "result.txt").write_text("data")
    (out / ".nextflow").mkdir()
    (out / ".nextflow" / "history").write_text("h")
    (out / ".nextflow.log").write_text("log")
    prov = provenance.write(outdir=out, pipeline="mini", command_str="nextflow run x",
                            submodule=_st(tmp_path / "up"), input_paths=[])
    sha = (prov / "outputs.sha256").read_text()
    assert "result.txt" in sha and ".nextflow" not in sha          # internals not checksummed


def test_replay_reproduces_into_a_fresh_outdir_not_the_original(tmp_path):
    # An nf-core pipeline publishes into --outdir and cannot re-publish over a previous run's files:
    # Nextflow will not overwrite pipeline_info/execution_trace_*.txt, and sarek's BCO manifest
    # collides outright. Replaying in place therefore failed on contact. --outdir on the command
    # line overrides the params file, so the whole run is redirected by one argument.
    out = tmp_path / "out"
    out.mkdir()
    prov = provenance.write(outdir=out, pipeline="mini", command_str="nextflow run x",
                            submodule=_st(tmp_path / "up"), input_paths=[])
    script = (prov / "commands.sh").read_text()
    assert f"default_target='{out}.replay'" in script or f"default_target={out}.replay" in script
    assert 'cd -- "$target"' in script                  # engine state lands beside the new results
    assert script.rstrip().endswith('--outdir "$target"')
    assert f"cd {out}\n" not in script                  # never the original directory


def test_replay_refuses_a_target_that_already_holds_results(tmp_path):
    # Executed, not just string-matched: the guard is the whole point of the script.
    import subprocess

    out = tmp_path / "out"
    out.mkdir()
    prov = provenance.write(outdir=out, pipeline="mini", command_str="true",
                            submodule=_st(tmp_path / "up"), input_paths=[])
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "results.txt").write_text("a previous run")
    r = subprocess.run([str(prov / "commands.sh"), str(occupied)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "not empty" in r.stderr
    assert (occupied / "results.txt").read_text() == "a previous run"      # left untouched


def test_replay_runs_in_the_target_directory(tmp_path):
    # The replay must launch from the target, so `.nextflow/` state never lands in the original run.
    import subprocess

    out = tmp_path / "out"
    out.mkdir()
    prov = provenance.write(outdir=out, pipeline="mini", command_str="pwd >pwd.txt; echo",
                            submodule=_st(tmp_path / "up"), input_paths=[])
    target = tmp_path / "fresh"
    r = subprocess.run([str(prov / "commands.sh"), str(target)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert (target / "pwd.txt").read_text().strip() == str(target)


def test_records_nextflow_env_and_probes_version_with_it(tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    seen = {}
    monkeypatch.setattr(provenance, "_nextflow_version",
                        lambda env_extra=None: seen.setdefault("env", env_extra) or "ver 25.10.2")
    overlay = {"NXF_VER": "25.10.2", "NXF_JVM_ARGS": "-Dx=y"}
    prov = provenance.write(outdir=out, pipeline="mini", command_str="x",
                            submodule=_st(tmp_path / "up"), input_paths=[], env_extra=overlay)
    manifest = json.loads((prov / "run_manifest.json").read_text())
    assert manifest["nextflow_env"] == overlay          # the overlay nfclaw applied is recorded
    assert seen["env"] == overlay                        # version probed with the overlay (reports the pin)


def test_nextflow_env_empty_by_default(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    prov = provenance.write(outdir=out, pipeline="mini", command_str="x",
                            submodule=_st(tmp_path / "up"), input_paths=[])
    assert json.loads((prov / "run_manifest.json").read_text())["nextflow_env"] == {}


def test_commands_sh_reexports_nxf_env_for_faithful_replay(tmp_path):
    # The manifest records the NXF_* overrides, but the *replay script* must apply them too — a run
    # that only works with a pinned engine or an IPv6/offline flag would not reproduce otherwise.
    out = tmp_path / "out"
    out.mkdir()
    overlay = {"NXF_VER": "25.10.2", "NXF_JVM_ARGS": "-Djava.net.preferIPv6Addresses=true"}
    prov = provenance.write(outdir=out, pipeline="mini", command_str="nextflow run x",
                            submodule=_st(tmp_path / "up"), input_paths=[], env_extra=overlay)
    lines = (prov / "commands.sh").read_text().splitlines()
    # Deterministic order (sorted), exported before the command, then the command itself.
    assert "export NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true" in lines
    assert "export NXF_VER=25.10.2" in lines
    run_line = next(i for i, line in enumerate(lines) if line.startswith("nextflow run x"))
    assert lines.index("export NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true") \
        < lines.index("export NXF_VER=25.10.2") < run_line


def test_commands_sh_quotes_env_values_with_spaces(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    prov = provenance.write(outdir=out, pipeline="mini", command_str="nextflow run x",
                            submodule=_st(tmp_path / "up"), input_paths=[],
                            env_extra={"NXF_JVM_ARGS": "-Dx=y -Dz=w"})
    assert "export NXF_JVM_ARGS='-Dx=y -Dz=w'" in (prov / "commands.sh").read_text()


def test_sensitive_nxf_env_is_redacted_and_omitted_from_replay(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    overlay = {
        "NXF_GITHUB_TOKEN": "top-secret-token",
        "NXF_JVM_ARGS": "-DproxyPassword=hunter2",
        "NXF_VER": "25.10.2",
    }
    prov = provenance.write(outdir=out, pipeline="mini", command_str="nextflow run x",
                            submodule=_st(tmp_path / "up"), input_paths=[], env_extra=overlay)
    manifest = json.loads((prov / "run_manifest.json").read_text())
    assert manifest["nextflow_env"] == {
        "NXF_GITHUB_TOKEN": "<redacted>",
        "NXF_JVM_ARGS": "<redacted>",
        "NXF_VER": "25.10.2",
    }
    assert manifest["redacted_nextflow_env"] == ["NXF_GITHUB_TOKEN", "NXF_JVM_ARGS"]
    replay = (prov / "commands.sh").read_text()
    assert "top-secret-token" not in replay and "hunter2" not in replay
    assert "export NXF_VER=25.10.2" in replay
    assert "Export these before replay: NXF_GITHUB_TOKEN NXF_JVM_ARGS" in replay


def test_commands_sh_has_no_exports_without_env(tmp_path):
    # No env overlay → no stray export lines (keeps the replay script byte-stable).
    out = tmp_path / "out"
    out.mkdir()
    prov = provenance.write(outdir=out, pipeline="mini", command_str="nextflow run x",
                            submodule=_st(tmp_path / "up"), input_paths=[])
    assert "export " not in (prov / "commands.sh").read_text()


def test_inherited_nxf_env_is_recorded_and_replayed(tmp_path, monkeypatch):
    # NXF_OFFLINE exported in the shell (not via --nxf-env) still shapes the run, so the bundle must
    # carry it: replaying elsewhere without it would try to reach the network and fail.
    monkeypatch.setenv("NXF_OFFLINE", "true")
    out = tmp_path / "out"
    out.mkdir()
    prov = provenance.write(outdir=out, pipeline="mini", command_str="nextflow run x",
                            submodule=_st(tmp_path / "up"), input_paths=[])
    assert json.loads((prov / "run_manifest.json").read_text())["nextflow_env"] == {
        "NXF_OFFLINE": "true"}
    assert "export NXF_OFFLINE=true" in (prov / "commands.sh").read_text()


def test_overlay_wins_over_inherited_nxf_env(tmp_path, monkeypatch):
    # --nxf-ver overrides an exported NXF_VER at launch, so provenance must record the pin that
    # actually ran, not the shell's value.
    monkeypatch.setenv("NXF_VER", "24.04.0")
    out = tmp_path / "out"
    out.mkdir()
    prov = provenance.write(outdir=out, pipeline="mini", command_str="x",
                            submodule=_st(tmp_path / "up"), input_paths=[],
                            env_extra={"NXF_VER": "25.10.2"})
    assert json.loads((prov / "run_manifest.json").read_text())["nextflow_env"] == {
        "NXF_VER": "25.10.2"}
    assert "export NXF_VER=25.10.2" in (prov / "commands.sh").read_text()


def test_inherited_sensitive_nxf_env_is_redacted(tmp_path, monkeypatch):
    # The shell is a far larger surface than the overlay, so redaction has to cover it too.
    monkeypatch.setenv("NXF_GITHUB_TOKEN", "top-secret-token")
    out = tmp_path / "out"
    out.mkdir()
    prov = provenance.write(outdir=out, pipeline="mini", command_str="x",
                            submodule=_st(tmp_path / "up"), input_paths=[])
    manifest = json.loads((prov / "run_manifest.json").read_text())
    assert manifest["nextflow_env"] == {"NXF_GITHUB_TOKEN": "<redacted>"}
    assert "top-secret-token" not in (prov / "commands.sh").read_text()


def test_outcome_is_recorded(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    prov = provenance.write(outdir=out, pipeline="mini", command_str="x",
                            submodule=_st(tmp_path / "up"), input_paths=[])
    assert json.loads((prov / "run_manifest.json").read_text())["outcome"] == "success"
    prov = provenance.write(outdir=out, pipeline="mini", command_str="x",
                            submodule=_st(tmp_path / "up"), input_paths=[], outcome="failed")
    assert json.loads((prov / "run_manifest.json").read_text())["outcome"] == "failed"


def test_commands_sh_is_executable(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    prov = provenance.write(outdir=out, pipeline="mini", command_str="nextflow run x",
                            submodule=_st(tmp_path / "up"), input_paths=[])
    assert (prov / "commands.sh").stat().st_mode & 0o111        # user/group/other execute bit set
