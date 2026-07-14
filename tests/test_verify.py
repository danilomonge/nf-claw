import pytest

from runner import verify
from runner.errors import NfclawError


def _bundle(root, name, entries):
    """A run directory with a provenance bundle listing {path: hash}."""
    out = root / name
    (out / "provenance").mkdir(parents=True)
    (out / "provenance" / "outputs.sha256").write_text(
        "".join(f"{digest}  {path}\n" for path, digest in entries.items()))
    return out


def test_a_faithful_replay_is_structurally_equal(tmp_path):
    orig = _bundle(tmp_path, "orig", {"a.txt": "aaa", "b.bam": "bbb"})
    replay = _bundle(tmp_path, "replay", {"a.txt": "aaa", "b.bam": "bbb"})
    cmp = verify.compare(orig, replay)
    assert cmp.structurally_equal
    assert cmp.identical == ["a.txt", "b.bam"] and not cmp.changed


def test_a_changed_file_is_counted_once_not_as_a_missing_plus_an_extra(tmp_path):
    # The trap this command exists to avoid. Diffing the raw `hash  path` lines makes one file whose
    # content changed look like a file that vanished AND a file that appeared, so a run where every
    # report merely carries a new timestamp reads as hundreds of missing and extra files.
    orig = _bundle(tmp_path, "orig", {"report.html": "aaa", "data.txt": "ccc"})
    replay = _bundle(tmp_path, "replay", {"report.html": "zzz", "data.txt": "ccc"})
    cmp = verify.compare(orig, replay)
    assert cmp.changed == ["report.html"]
    assert cmp.missing == [] and cmp.extra == []
    assert cmp.identical == ["data.txt"]
    assert cmp.structurally_equal          # same files produced — only their bytes differ


def test_a_file_the_replay_never_made_is_a_real_failure(tmp_path):
    orig = _bundle(tmp_path, "orig", {"a.txt": "aaa", "gone.vcf": "bbb"})
    replay = _bundle(tmp_path, "replay", {"a.txt": "aaa", "new.vcf": "ccc"})
    cmp = verify.compare(orig, replay)
    assert cmp.missing == ["gone.vcf"] and cmp.extra == ["new.vcf"]
    assert not cmp.structurally_equal      # the replay did different work


def test_report_explains_why_bytes_differ_but_flags_a_structural_difference(tmp_path):
    orig = _bundle(tmp_path, "orig", {"report.html": "aaa"})
    replay = _bundle(tmp_path, "replay", {"report.html": "zzz"})
    text = verify.report(verify.compare(orig, replay))
    assert "changed   : 1" in text
    assert "same set of files" in text and "embed timestamps" in text

    orig2 = _bundle(tmp_path, "orig2", {"a.txt": "aaa"})
    replay2 = _bundle(tmp_path, "replay2", {})
    text2 = verify.report(verify.compare(orig2, replay2))
    assert "did NOT produce the same set of files" in text2


def test_a_directory_without_a_bundle_is_named_clearly(tmp_path):
    orig = _bundle(tmp_path, "orig", {"a.txt": "aaa"})
    (tmp_path / "empty").mkdir()
    with pytest.raises(NfclawError, match="no provenance bundle"):
        verify.compare(orig, tmp_path / "empty")
