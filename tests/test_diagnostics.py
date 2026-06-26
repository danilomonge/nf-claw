from pathlib import Path

from runner import diagnostics as dx


def test_network_signature_suggests_ipv6():
    hints = dx.diagnose("Caused by: java.net.SocketException: Network is unreachable\n"
                        "  downloading https://raw.githubusercontent.com/nf-core/configs/.../nfcore_custom.config")
    assert len(hints) == 1
    assert "NXF_JVM_ARGS" in hints[0] and "preferIPv6Addresses" in hints[0]


def test_parser_signature_suggests_nxf_ver():
    hints = dx.diagnose("ERROR ~ Unexpected input: ':' @ line 35, column 12")
    assert any("--nxf-ver" in h for h in hints)


def test_busco_download_signature_suggests_skip():
    hints = dx.diagnose("Could not reach busco-data.ezlab.org/file_versions.tsv after 5 retries")
    assert any("skip-busco" in h.lower() for h in hints)


def test_faidx_empty_signature_suggests_reference():
    hints = dx.diagnose("Process `SAMTOOLS_FAIDX ([])` terminated with an error exit status (1)")
    assert any("--fasta" in h or "genome" in h.lower() for h in hints)


def test_unicycler_py312_signature_suggests_megahit():
    hints = dx.diagnose("SyntaxWarning: invalid escape sequence '\\d' in unicycler/support.py:488")
    assert any("megahit" in h.lower() for h in hints)


def test_space_in_paths_suggests_space_free_workdir():
    hints = dx.diagnose("any output", paths=[Path("/vol/draft 2/up"), Path("/clean/out")])
    assert len(hints) == 1 and "space" in hints[0].lower() and "NXF_WORK" in hints[0]
    assert "/vol/draft 2/up" in hints[0] and "/clean/out" not in hints[0]   # only the spaced path named


def test_no_signature_and_clean_paths_returns_empty():
    assert dx.diagnose("a generic pipeline error with no known cause", paths=[Path("/clean/x")]) == []


def test_multiple_signatures_each_contribute_a_hint():
    hints = dx.diagnose("java.net.SocketException: Network is unreachable\nUnexpected input: ':'",
                        paths=[Path("/a b/up")])
    assert len(hints) == 3                                    # network + parser + space
