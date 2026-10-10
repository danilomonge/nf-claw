"""Preserve complete original reads and record exact runtime corrections."""
import gzip
import subprocess

import pytest

from runner import fastqrepair_compat as compat


def _decode(path):
    return gzip.open(path, "rb").read() if path.suffix == ".gz" else path.read_bytes()


@pytest.mark.parametrize("compressed", [False, True])
@pytest.mark.parametrize("count,splits", [(3, 2), (1, 4), (5, 3), (12, 5), (1001, 1001)])
def test_record_splitting_preserves_every_byte_and_all_frame_boundaries(tmp_path, compressed, count, splits):
    content = b"".join(f"@read{i}\nACGT\n+\n@@@@\n".encode() for i in range(count))
    source = tmp_path / ("reads.fastq.gz" if compressed else "reads.fastq")
    if compressed:
        with gzip.open(source, "wb") as handle:
            handle.write(content)
    else:
        source.write_bytes(content)
    files = compat.scatter(source, splits, "source", tmp_path / "chunks")
    assert len(files) == min(count, splits)
    assert b"".join(_decode(path) for path in sorted(files)) == content
    for path in files:
        lines = _decode(path).splitlines()
        assert len(lines) % 4 == 0
        assert all(lines[i].startswith(b"@read") and lines[i + 2] == b"+" for i in range(0, len(lines), 4))


@pytest.mark.parametrize("content", [b"noise\n@r\nACGT\n+\nIIII\n", b"@r\nACGT\n+\nIII\n",
                                     b"@r\nACGT\n+\n", b"", b"@r\nACGT\n+\nIIII"])
def test_ambiguous_or_incomplete_input_is_not_discarded_by_splitting(tmp_path, content):
    source = tmp_path / "damaged.fastq"
    source.write_bytes(content)
    files = compat.scatter(source, 4, "source", tmp_path / "chunks")
    assert b"".join(_decode(path) for path in files) == content
    assert len(files) == 1


def test_changed_source_cannot_claim_a_successful_split(tmp_path, monkeypatch):
    source = tmp_path / "reads.fastq"
    source.write_bytes(b"@A\nACGT\n+\nIIII\n")
    scan = compat._scan

    def changed_after_scan(path):
        result = scan(path)
        path.write_bytes(b"@A\nTGCA\n+\nHHHH\n")
        return result

    monkeypatch.setattr(compat, "_scan", changed_after_scan)
    with pytest.raises(ValueError, match="changed"):
        compat.scatter(source, 2, "source", tmp_path / "chunks")


def test_repair_quality_offset_and_log_redirection_reach_the_actual_command(tmp_path):
    fake = tmp_path / "repair.sh"
    fake.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
    fake.chmod(0o755)
    script = tmp_path / ".command.sh"
    script.write_text('#!/bin/bash -eu\nrepair.sh \\\n    threads=1\n    qin=64 \\\n    &> repair.log\n')
    compat.patch_task("repair", script)
    import os
    result = subprocess.run(["bash", str(script)], cwd=tmp_path,
                            env={**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}"},
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "repair.log").read_text().splitlines() == ["threads=1", "qin=64"]


def test_unrecognized_task_is_refused_without_modifying_its_recipe(tmp_path):
    path = tmp_path / ".command.sh"
    path.write_text("echo unexpected upstream recipe\n")
    for operation in ("scatter", "repair"):
        with pytest.raises(ValueError, match="unrecognized"):
            compat.patch_task(operation, path)
        assert path.read_text() == "echo unexpected upstream recipe\n"


def test_recorded_helper_executes_without_installed_runner_modules(tmp_path):
    import json
    source = tmp_path / "reads.fastq"
    source.write_bytes(b"@A\nACGT\n+\nIIII\n@B\nTGCA\n+\nHHHH\n@C\nAAAA\n+\n@@@@\n")
    script = tmp_path / ".command.sh"
    script.write_text('wipertools \\\n    fastqscatter \\\n    -f reads.fastq -n 2 -p source -o chunks\n'
                      'echo "wipertools fastqscatter: $(wipertools fastqscatter --version)"\n')
    compat.patch_task("scatter", script)
    result = subprocess.run(["bash", str(script)], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert compat.recipe_digest() in result.stdout
    assert b"".join(_decode(path) for path in sorted((tmp_path / "chunks").iterdir())) == source.read_bytes()
    config = compat.write_config(tmp_path / "recorded.config").read_text()
    assert compat.recipe_digest()[:16] in config
    assert "import runner" not in config
    assert json.dumps(compat._command() + " patch repair .command.sh") in config
