"""Replay dependency guards and failure-safe provenance publication."""
import hashlib
import json
import subprocess

import pytest

from runner import provenance
from runner.schema import Column, InputSchema
from runner.submodule import SubmoduleStatus


def _write(outdir, *, command_str="echo REPLAY_RAN", submodule=None, **kwargs):
    return provenance.write(
        outdir=outdir, pipeline="mini", command_str=command_str,
        submodule=submodule or SubmoduleStatus("mini", outdir.parent / "up", True, True,
                                               "1.0.0", "deadbeef", ()), **kwargs)


@pytest.fixture(autouse=True)
def _no_engine_probe(monkeypatch):
    # No engine is launched in these dependency/bundle tests.
    monkeypatch.setattr(provenance, "_nextflow_version", lambda env_extra=None: "test engine")


@pytest.mark.parametrize("prior_bundle", [False, True])
def test_checksum_failure_cannot_leave_a_success_manifest(tmp_path, monkeypatch, prior_bundle):
    out = tmp_path / "out"
    if prior_bundle:
        _write(out, input_paths=[])

    def fail(_outdir):
        raise PermissionError("unreadable result")

    monkeypatch.setattr(provenance, "output_checksums", fail)
    with pytest.raises(PermissionError):
        _write(out, input_paths=[])
    manifest = out / "provenance" / "run_manifest.json"
    assert not manifest.exists() or json.loads(manifest.read_text())["outcome"] != "success"
    if prior_bundle:
        result = subprocess.run([str(out / "provenance" / "commands.sh"), str(tmp_path / "fresh")],
                                capture_output=True, text=True)
        assert result.returncode != 0 and "REPLAY_RAN" not in result.stdout


def test_replay_refuses_changed_external_config_before_launch(tmp_path):
    config = tmp_path / "analysis.config"
    config.write_text("params.threshold = 0.01\n")
    prov = _write(tmp_path / "out", input_paths=[], config_paths=(config,))
    config.write_text("params.threshold = 0.99\n")
    result = subprocess.run([str(prov / "commands.sh"), str(tmp_path / "fresh")],
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert "REPLAY_RAN" not in result.stdout
    assert "analysis.config" in result.stderr


def test_prelaunch_input_hash_is_preserved_if_input_changes_during_run(tmp_path):
    reads = tmp_path / "reads.fastq"
    original = b"@r\nACGT\n+\nIIII\n"
    reads.write_bytes(original)
    snapshot = {str(reads): hashlib.sha256(original).hexdigest()}
    reads.write_bytes(b"@r\nTTTT\n+\nIIII\n")
    prov = _write(tmp_path / "out", input_paths=[reads], input_checksums=snapshot)
    assert (prov / "inputs.sha256").read_text() == (
        "386b5921e18396f227d1c7cca34b80fa323518ef1b9d29db0bb1d27dc42f3535" + f"  {reads}\n")
    result = subprocess.run([str(prov / "commands.sh"), str(tmp_path / "fresh")],
                            capture_output=True, text=True)
    assert result.returncode != 0 and "REPLAY_RAN" not in result.stdout


def test_directory_input_new_files_invalidate_replay(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "sample.dat").write_text("original")
    prov = _write(tmp_path / "out", input_paths=[data])
    (data / "new-sample.dat").write_text("extra data")
    result = subprocess.run([str(prov / "commands.sh"), str(tmp_path / "fresh")],
                            capture_output=True, text=True)
    assert result.returncode != 0 and "REPLAY_RAN" not in result.stdout
    assert "new-sample.dat" in result.stderr


def test_directory_and_glob_inputs_have_content_checksums(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "a.txt").write_bytes(b"a")
    (data / "nested").mkdir()
    (data / "nested" / "b.txt").write_bytes(b"b")
    snapshot = provenance.hash_inputs([data, data / "*.txt"])
    assert snapshot == {
        str(data / "a.txt"): "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",
        str(data / "nested" / "b.txt"): "3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d",
    }


@pytest.mark.parametrize("pattern", ["sample_{1,2}.txt", "**.txt"])
def test_nextflow_glob_variants_preserve_their_input_files(tmp_path, pattern):
    data = tmp_path / "data"
    data.mkdir()
    first = data / "sample_1.txt"
    first.write_bytes(b"a")
    second = data / "sample_2.txt"
    second.write_bytes(b"b")
    if pattern == "**.txt":
        (data / "nested").mkdir()
        second.rename(data / "nested" / second.name)
        second = data / "nested" / second.name
    assert provenance.hash_inputs([data / pattern]) == {
        str(first): "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",
        str(second): "3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d",
    }


def test_samplesheet_data_paths_are_part_of_input_identity(tmp_path):
    sheet = tmp_path / "samples.csv"
    reads = tmp_path / "reads.fastq"
    reads.write_bytes(b"reads")
    sheet.write_text(f"sample,fastq,remote\nA,{reads},s3://bucket/remote.fastq\n")
    schema = InputSchema(columns=(
        Column("sample", "string", True, None),
        Column("fastq", "string", True, None, fmt="file-path"),
        Column("remote", "string", False, None, fmt="file-path"),
    ))
    assert provenance.samplesheet_input_paths(sheet, schema) == [reads]


def test_unchanged_dependencies_allow_replay(tmp_path):
    reads = tmp_path / "reads.fastq"
    reads.write_bytes(b"reads")
    config = tmp_path / "analysis.config"
    config.write_text("params.threshold = 0.01\n")
    prov = _write(tmp_path / "out", input_paths=[reads], config_paths=(config,))
    result = subprocess.run([str(prov / "commands.sh"), str(tmp_path / "fresh")],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "REPLAY_RAN" in result.stdout


def test_recorded_params_file_is_a_guarded_replay_dependency(tmp_path):
    out = tmp_path / "out"
    (out / "provenance").mkdir(parents=True)
    params = out / "provenance" / "params.json"
    params.write_text('{"threshold": 0.01}\n')
    prov = _write(out, input_paths=[])
    params.write_text('{"threshold": 0.99}\n')
    result = subprocess.run([str(prov / "commands.sh"), str(tmp_path / "fresh")],
                            capture_output=True, text=True)
    assert result.returncode != 0 and "REPLAY_RAN" not in result.stdout
    assert "params.json" in result.stderr


def _git_pipeline(tmp_path):
    path = tmp_path / "up"
    path.mkdir()
    (path / "main.nf").write_text("original workflow\n")
    for args in (("init", "-q"), ("add", "main.nf"),
                 ("-c", "user.name=Test", "-c", "user.email=test@example.com",
                  "commit", "-qm", "original")):
        subprocess.run(["git", "-C", str(path), *args], check=True, capture_output=True)
    commit = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"],
                            check=True, capture_output=True, text=True).stdout.strip()
    return SubmoduleStatus("mini", path, True, True, "1.0.0", commit, ())


@pytest.mark.parametrize("change", ["tracked_bytes", "head", "tracked_inventory"])
def test_pipeline_changes_cannot_silently_change_replay(tmp_path, change):
    st = _git_pipeline(tmp_path)
    prov = _write(tmp_path / "out", input_paths=[], submodule=st)
    if change == "tracked_bytes":
        (st.path / "main.nf").write_text("different scientific algorithm\n")
    elif change == "tracked_inventory":
        (st.path / "new.nf").write_text("new module\n")
        subprocess.run(["git", "-C", str(st.path), "add", "new.nf"], check=True)
    else:
        subprocess.run(["git", "-C", str(st.path), "-c", "user.name=Test",
                        "-c", "user.email=test@example.com", "commit", "--allow-empty",
                        "-qm", "new revision"], check=True)
    result = subprocess.run([str(prov / "commands.sh"), str(tmp_path / "fresh")],
                            capture_output=True, text=True)
    assert result.returncode != 0 and "REPLAY_RAN" not in result.stdout
    assert "pipeline" in result.stderr.lower()


def test_prelaunch_pipeline_snapshot_preserves_original_dirty_bytes(tmp_path):
    st = _git_pipeline(tmp_path)
    (st.path / "main.nf").write_bytes(b"a")
    snapshot = provenance.hash_pipeline(st.path)
    (st.path / "main.nf").write_bytes(b"b")
    prov = _write(tmp_path / "out", input_paths=[], submodule=st, pipeline_checksums=snapshot)
    assert (prov / "pipeline.sha256").read_text() == (
        "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb  main.nf\n")
    result = subprocess.run([str(prov / "commands.sh"), str(tmp_path / "fresh")],
                            capture_output=True, text=True)
    assert result.returncode != 0 and "REPLAY_RAN" not in result.stdout


def test_default_engine_is_pinned_for_replay_without_falsifying_recorded_environment(tmp_path, monkeypatch):
    monkeypatch.delenv("NXF_VER", raising=False)
    monkeypatch.setattr(provenance, "_nextflow_version", lambda env_extra=None: "nextflow version 25.10.4 build 11033")
    prov = _write(tmp_path / "out", input_paths=[],
                  command_str="sh -c 'printf %s \"$NXF_VER\"'")
    manifest = json.loads((prov / "run_manifest.json").read_text())
    assert "NXF_VER" not in manifest["nextflow_env"]
    result = subprocess.run([str(prov / "commands.sh"), str(tmp_path / "fresh")],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert result.stdout == "25.10.4"


def test_commands_sh_resolves_dynamically_when_run_bundle_is_relocated(tmp_path):
    prov = _write(tmp_path / "out", input_paths=[])
    script = (prov / "commands.sh").read_text()
    assert "_script_dir" in script
    assert "replay_guard.py" in script
