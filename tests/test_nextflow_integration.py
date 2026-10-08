"""Real-engine validation using a deterministic, local fixture with an independent oracle.

This exercises nfclaw's execution contract; it makes no claim about biological algorithms.
"""
import hashlib
import json
import shutil
import subprocess

import pytest

from runner import chain, orchestration, resources, runlog, verify


@pytest.mark.skipif(shutil.which("nextflow") is None, reason="requires a real Nextflow engine")
def test_real_run_relocated_replay_and_mutated_input_guard(tmp_path, tmp_path_factory):
    root = tmp_path / "library"
    upstream = root / "pipelines/fixture/upstream"
    upstream.mkdir(parents=True)
    (upstream.parent / "skill.md").write_text("---\nname: fixture\n---\n")
    (upstream / "nextflow_schema.json").write_text(json.dumps({"properties": {
        "input": {"type": "string", "format": "file-path", "exists": True},
        "outdir": {"type": "string", "format": "directory-path"}}}))
    (upstream / "nextflow.config").write_text(
        "nextflow.enable.dsl=2\nprofiles { standard { process.executor = 'local' } }\n")
    (upstream / "main.nf").write_text('''process DIGEST {
    publishDir params.outdir, mode: 'copy'
    input:
    path data
    output:
    path 'result'
    script:
    """
    mkdir result
    shasum -a 256 ${data} > result/digest.txt
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
    assert (out / "result/digest.txt").read_text() == expected
    assert result.outputs_report.files == ("result/digest.txt",)
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
    assert comparison.identical == ["result/digest.txt"]
    data.write_bytes(b"changed scientific input\n")
    refused = subprocess.run(["bash", script, "refused"], cwd=relocated.parent,
                             capture_output=True, text=True, timeout=15)
    assert refused.returncode != 0
    assert "dependency check failed" in refused.stderr
    assert not (relocated.parent / "refused/result/digest.txt").exists()
    spec = chain.parse_spec({"profile": "standard", "nxf_ver": "25.10.4", "stages": [
        {"pipeline": "fixture", "input": str(data)},
        {"pipeline": "fixture", "id": "second",
         "handoff": {"params": {"input": {"file": "result/digest.txt"}}}}]})
    chain_out = relocated.parent / "chain"
    result = chain.run_chain(spec, repo_root=root, outdir=chain_out, timeout_seconds=120)
    assert result.outcome == "success"
    first_digest = hashlib.sha256(data.read_bytes()).hexdigest() + "  data.txt\n"
    expected_second = hashlib.sha256(first_digest.encode()).hexdigest() + "  digest.txt\n"
    assert (chain_out / "02-second/result/digest.txt").read_text() == expected_second
    state, problems = chain.status(chain_out)
    assert problems == [] and chain.status_exit_code(state, problems) == 0
    (chain_out / "01-fixture/result/digest.txt").write_bytes(b"changed upstream result\n")
    state, problems = chain.status(chain_out)
    assert problems and chain.status_exit_code(state, problems) == 1
