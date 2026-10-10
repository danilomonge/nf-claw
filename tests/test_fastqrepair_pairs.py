"""The scientific oracle must detect missing, duplicated or swapped fixture reads."""
import gzip
import json

import pytest

from scripts.check_fastqrepair_pairs import EXPECTED, READS, check_run, write_fixture


def _run(tmp_path, *, compressed=False):
    run = tmp_path / "run"
    (run / "repaired").mkdir(parents=True)
    (run / "pipeline_info").mkdir()
    (run / "provenance").mkdir()
    (run / "provenance/run_manifest.json").write_text(json.dumps(
        {"pipeline": "fastqrepair", "version": "1.1.1",
         "commit": "70a38209407b9367a9ff7ab8b26d84cb1983ea18", "outdir": str(run),
         "nextflow": "nextflow version 25.10.4", "outcome": "success"}))
    (run / "pipeline_info/execution_trace.txt").write_text(
        "name\tstatus\texit\nNFCORE_FASTQREPAIR:FASTQREPAIR:BBMAP_REPAIR (paired_probe)\tCOMPLETED\t0\n")
    for name, ids in EXPECTED.items():
        _write(run / "repaired" / name, ids)
    reports = run / "repaired/reports/paired_probe"
    reports.mkdir(parents=True)
    for mate in (("paired_probe_recovered_1", "paired_probe_recovered_2") if compressed else ("left", "right")):
        (reports / f"{mate}.report").write_text("Total lines: 12\nClean reads: 3\n")
    (run / "repaired/paired_probe.repair.sh.log").write_text("paired and singleton diagnostics\n")
    return run


def test_gzip_fixture_contains_the_exact_known_source_records(tmp_path):
    from scripts.check_fastqrepair_pairs import read_fastq
    source = tmp_path / "source"
    write_fixture(source, compressed=True)
    recovered = {}
    for path in source.glob("*.fastq.gz"):
        recovered.update(read_fastq(path))
    assert recovered == READS
    assert str(source / "left.fastq.gz") in (source / "samples.csv").read_text()


@pytest.mark.parametrize("status", ["COMPLETED", "CACHED", "FAILED", "missing"])
def test_gzip_oracle_requires_actual_successful_recovery_and_conserves_every_read(tmp_path, status):
    run = _run(tmp_path, compressed=True)
    trace = run / "pipeline_info/execution_trace.txt"
    if status != "missing":
        with trace.open("a") as handle:
            handle.write(f"NFCORE_FASTQREPAIR:FASTQREPAIR:GZRT (paired_probe)\t{status}\t0\n")
    if status == "COMPLETED":
        assert sum(check_run(run, compressed=True).values()) == 6
    else:
        with pytest.raises(ValueError, match="GZRT"):
            check_run(run, compressed=True)


@pytest.mark.parametrize("problem", [None, "relocated", "failed", "wrong_engine", "wrong_origin"])
def test_replay_uses_validated_source_identity_and_its_own_observed_outcome(tmp_path, problem):
    import shutil
    source = _run(tmp_path)
    if problem == "relocated":
        archive = tmp_path / "archive"
        source.rename(archive)
        source = archive
    replay = tmp_path / "replay"
    shutil.copytree(source, replay)
    (replay / "provenance/run_manifest.json").unlink()
    logs = replay / "provenance/logs"
    logs.mkdir()
    origin = source if problem != "wrong_origin" else tmp_path / "other"
    outcome = "success" if problem != "failed" else "failed (exit status 1)"
    (logs / "run.log").write_text(
        "==> nfclaw replay started 2026-10-10T19:35:43+00:00\n"
        f"    replay of: {origin}\n"
        f"==> nfclaw replay finished 2026-10-10T19:36:06+00:00: {outcome}\n")
    engine = "25.10.4" if problem != "wrong_engine" else "26.04.0"
    (replay / ".nextflow.log").write_text(f"INFO nextflow.cli.CmdRun - N E X T F L O W  ~  version {engine}\n")
    if problem in (None, "relocated"):
        assert sum(check_run(replay, source_run=source).values()) == 6
    else:
        with pytest.raises(ValueError):
            check_run(replay, source_run=source)


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
