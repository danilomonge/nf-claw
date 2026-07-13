import pytest

from runner import resources
from runner.errors import NfclawError


def test_config_is_a_nextflow_resource_limits_block():
    text = resources.parse(4, "15.GB", "1.h").config_text()
    assert "process {" in text and "resourceLimits = [" in text
    assert "cpus: 4," in text                       # an int, unquoted — Nextflow expects a number
    assert "memory: '15.GB'," in text               # a quoted MemoryUnit string
    assert "time: '1.h'" in text                    # last entry: no trailing comma (Groovy list)


def _limits_block(text: str) -> str:
    """Just the resourceLimits entries — the comment header names all three flags."""
    return text.split("resourceLimits = [", 1)[1].split("]", 1)[0]


def test_only_the_limits_given_are_written():
    # A ceiling on one dimension must not silently invent one for the others.
    block = _limits_block(resources.parse(None, "15.GB", None).config_text())
    assert "memory: '15.GB'" in block
    assert "cpus" not in block and "time" not in block


def test_empty_when_nothing_is_capped():
    assert resources.parse(None, None, None).is_empty()


@pytest.mark.parametrize("value", ["15.GB", "15 GB", "16GB", "512.MB", "1.5.TB", "100.B"])
def test_accepts_nextflow_memory_spellings(value):
    assert resources.parse(None, value, None).memory == value


@pytest.mark.parametrize("value", ["1.h", "90.min", "2.d", "30 s", "1h", "24.hours"])
def test_accepts_nextflow_duration_spellings(value):
    assert resources.parse(None, None, value).time == value


@pytest.mark.parametrize("value", ["15 gigs", "lots", "15", "GB", "15.GB; rm -rf /"])
def test_rejects_a_value_nextflow_could_not_parse(value):
    # Fail fast, naming the flag — better than the engine dying at the first task. This also means
    # no unvalidated text can reach the generated Groovy config.
    with pytest.raises(NfclawError, match="--limit-memory"):
        resources.parse(None, value, None)


@pytest.mark.parametrize("value", ["1 fortnight", "soon", "1.hh", "h"])
def test_rejects_a_duration_nextflow_could_not_parse(value):
    with pytest.raises(NfclawError, match="--limit-time"):
        resources.parse(None, None, value)


def test_rejects_a_non_positive_cpu_count():
    with pytest.raises(NfclawError, match="--limit-cpus"):
        resources.parse(0, None, None)


def test_write_config_creates_the_file_and_parent(tmp_path):
    dest = tmp_path / "provenance" / "resource_limits.config"
    written = resources.write_config(resources.parse(4, "15.GB", "1.h"), dest)
    assert written == dest and "resourceLimits" in dest.read_text()
