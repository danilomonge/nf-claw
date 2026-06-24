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
