"""Check that the independent demo FastQC oracle detects changed scientific statistics."""
import gzip
import importlib.util
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_demo_fastqc_metrics.py"
spec = importlib.util.spec_from_file_location("demo_metric_oracle", SCRIPT)
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


def _report(tmp_path, *, reads="2", length="3-5", gc="71", filtered="0"):
    source = tmp_path / "reads.gz"
    with gzip.open(source, "wt") as handle:
        handle.write("@one\nAACGN\n+\n!!!!!\n@two\nGGG\n+\n!!!\n")
    report = tmp_path / "reads_fastqc.zip"
    content = ("##FastQC\t0.12.1\n>>Basic Statistics\tpass\n"
               f"Filename\treads.gz\nTotal Sequences\t{reads}\nSequence length\t{length}\n"
               f"%GC\t{gc}\nSequences flagged as poor quality\t{filtered}\n>>END_MODULE\n")
    with zipfile.ZipFile(report, "w") as archive:
        archive.writestr("reads_fastqc/fastqc_data.txt", content)
    return report


def test_oracle_counts_reads_lengths_and_gc_excluding_ambiguous_bases(tmp_path):
    record = oracle.check_report(_report(tmp_path))
    assert record["expected"] == {"reads": 2, "total_bases": 8,
                                   "length": "3-5", "gc_percent": 71}
    assert record["matches"] is True


@pytest.mark.parametrize("changed", [{"reads": "3"}, {"length": "3-6"}, {"gc": "72"}])
def test_oracle_refuses_changed_scientific_statistics(tmp_path, changed):
    with pytest.raises(ValueError, match="observed .* expected"):
        oracle.check_report(_report(tmp_path, **changed))


@pytest.mark.parametrize("content", ["", "@r\nACGT\n", "@r\nACGT\n+\n###\n",
                                     "@r\nacgt\n+\n!!!!\n"])
def test_oracle_refuses_empty_malformed_or_unsupported_fastq(tmp_path, content):
    source = tmp_path / "bad.gz"
    with gzip.open(source, "wt") as handle:
        handle.write(content)
    with pytest.raises(ValueError):
        oracle.read_metrics(source)


def test_oracle_refuses_unvalidated_filtered_read_mode(tmp_path):
    with pytest.raises(ValueError, match="filtered reads require a different oracle"):
        oracle.check_report(_report(tmp_path, filtered="1"))


def test_comparison_ignores_archive_timestamps_but_checks_full_data_tables(tmp_path):
    row = oracle.check_report(_report(tmp_path))
    oracle.compare_metrics([{**row, "report_sha256": "changed ZIP timestamp bytes"}], [row])
    with pytest.raises(ValueError, match="replay changed data_sha256"):
        oracle.compare_metrics([{**row, "data_sha256": "changed other QC module"}], [row])


def test_comparison_refuses_missing_or_duplicate_report_identities(tmp_path):
    row = oracle.check_report(_report(tmp_path))
    with pytest.raises(ValueError, match="inventory changed"):
        oracle.compare_metrics([], [row])
    with pytest.raises(ValueError, match="duplicate report identities"):
        oracle.compare_metrics([row, row], [row])
