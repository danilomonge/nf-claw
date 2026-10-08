"""Real-engine validation using a deterministic, local fixture with an independent oracle.

This exercises nfclaw's execution contract; it makes no claim about biological algorithms.
"""
import hashlib
import json
import shutil
import subprocess

import pytest

from runner import orchestration, resources, runlog, verify


@pytest.mark.skipif(shutil.which("nextflow") is None, reason="requires a real Nextflow engine")
def test_real_run_relocated_replay_and_mutated_input_guard(tmp_path, tmp_path_factory):
    root = tmp_path / "library"
    upstream = root / "pipelines/fixture/upstream"
    upstream.mkdir(parents=True)
    (upstream.parent / "skill.md").write_text("---\nname: fixture\n---\n")
    (upstream / "nextflow_schema.json").write_text(json.dumps({"properties": {
        "input": {"type": "string", "format": "file-path", "exists": True},
        "outdir": {"type": "string", "format": "directory-path"}}}))
    (upstream / "nextflow.config").write_text("nextflow.enable.dsl=2\n")
    (upstream / "main.nf").write_text('''process DIGEST {
    publishDir params.outdir, mode: 'copy'
    input:
    path data
    output:
    path 'digest.txt'
    script:
    """
    shasum -a 256 ${data} > digest.txt
    """
}
workflow {
    DIGEST(Channel.fromPath(params.input))
}
''')
    data = tmp_path / "data.txt"
    data.write_bytes(b"known deterministic input\n")
    out = tmp_path_factory.mktemp("real-run") / "results"
    result = orchestration.run_pipeline(
        "fixture", repo_root=root, input_path=data, outdir=out, profile="",
        params_file=None, cli_overrides={}, resume=False, demo=False, check_only=False,
        write_provenance=True, timeout_seconds=90, nxf_ver="25.10.4",
        limits=resources.parse(1, None, None))
    expected = hashlib.sha256(data.read_bytes()).hexdigest() + "  data.txt\n"
    assert (out / "digest.txt").read_text() == expected
    assert result.outputs_report.files == ("digest.txt",)
    assert runlog.read_state(out / "provenance/logs/run.log").state == "success"
    relocated = out.with_name("archive")
    out.rename(relocated)
    # Relative script path plus a relocated bundle exercise both path-resolution boundaries.
    script = "archive/provenance/commands.sh"
    replay = subprocess.run(["bash", script, "replay"], cwd=relocated.parent,
                            capture_output=True, text=True, timeout=90)
    assert replay.returncode == 0, replay.stdout + replay.stderr
    comparison = verify.compare(relocated, relocated.parent / "replay")
    assert comparison.byte_identical
    assert comparison.identical == ["digest.txt"]
    data.write_bytes(b"changed scientific input\n")
    refused = subprocess.run(["bash", script, "refused"], cwd=relocated.parent,
                             capture_output=True, text=True, timeout=15)
    assert refused.returncode != 0
    assert "dependency check failed" in refused.stderr
    assert not (relocated.parent / "refused/digest.txt").exists()
