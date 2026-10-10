"""The scientific oracle must detect missing, duplicated or swapped fixture reads."""
import gzip
import json

import pytest

from scripts.check_fastqrepair_pairs import EXPECTED, READS, check_run, write_fixture


def _run(tmp_path):
    run = tmp_path / "run"
    (run / "repaired").mkdir(parents=True)
    (run / "pipeline_info").mkdir()
    (run / "provenance").mkdir()
    (run / "provenance/run_manifest.json").write_text(json.dumps(
        {"pipeline": "fastqrepair", "version": "1.1.1",
         "nextflow": "nextflow version 25.10.4", "outcome": "success"}))
    (run / "pipeline_info/execution_trace.txt").write_text(
        "name\tstatus\texit\nNFCORE_FASTQREPAIR:FASTQREPAIR:BBMAP_REPAIR (paired_probe)\tCOMPLETED\t0\n")
    for name, ids in EXPECTED.items():
        _write(run / "repaired" / name, ids)
    reports = run / "repaired/reports/paired_probe"
    reports.mkdir(parents=True)
    for mate in ("left", "right"):
        (reports / f"{mate}.report").write_text("Total lines: 12\nClean reads: 3\n")
    (run / "repaired/paired_probe.repair.sh.log").write_text("paired and singleton diagnostics\n")
    return run


def _write(path, ids):
    with gzip.open(path, "wt", encoding="ascii") as handle:
        for key in ids:
            sequence, quality = READS[key]
            handle.write(f"@{key}\n{sequence}\n+\n{quality}\n")


def test_fixture_and_valid_outputs_preserve_all_six_input_reads(tmp_path):
    write_fixture(tmp_path / "source")
    assert (tmp_path / "source/left.fastq").read_text().count("\n@") == 2
    assert sum(check_run(_run(tmp_path)).values()) == 6


@pytest.mark.parametrize("problem", ["swapped", "missing", "duplicate", "mutated", "skipped", "wrong_engine",
                                     "overwritten_report", "wrong_count", "empty_log"])
def test_pair_oracle_refuses_false_scientific_success(tmp_path, problem):
    run = _run(tmp_path)
    first = run / "repaired/paired_probe_1.fastq.gz"
    if problem == "swapped":
        _write(first, ["pairA/2", "pairB/2"])
    elif problem == "missing":
        _write(first, ["pairA/1"])
    elif problem == "duplicate":
        _write(first, ["pairA/1", "pairA/1", "pairB/1"])
    elif problem == "mutated":
        with gzip.open(first, "wt") as handle:
            handle.write("@pairA/1\nAAAA\n+\nIIII\n")
    elif problem == "wrong_engine":
        (run / "provenance/run_manifest.json").write_text("{}")
    elif problem == "overwritten_report":
        (run / "repaired/reports/paired_probe/left.report").unlink()
    elif problem == "wrong_count":
        (run / "repaired/reports/paired_probe/left.report").write_text("Total lines: 13\nClean reads: 2\n")
    elif problem == "empty_log":
        (run / "repaired/paired_probe.repair.sh.log").write_text("")
    else:
        (run / "pipeline_info/execution_trace.txt").write_text("name\tstatus\texit\n")
    with pytest.raises(ValueError):
        check_run(run)
