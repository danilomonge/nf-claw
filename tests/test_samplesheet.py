from runner.schema import Column, InputSchema
from runner import samplesheet

SCH = InputSchema(columns=(
    Column("sample", "string", True, None, None),
    Column("fastq_1", "string", True, None, "file-path"),
))

def test_missing_required_column(tmp_path):
    ss = tmp_path / "ss.csv"
    ss.write_text("sample\nA\n")
    issues = samplesheet.validate(ss, SCH)
    assert any("fastq_1" in i for i in issues)

def test_missing_input_file(tmp_path):
    ss = tmp_path / "ss.csv"
    ss.write_text("sample,fastq_1\nA,missing_R1.fastq.gz\n")
    issues = samplesheet.validate(ss, SCH)
    assert any("file not found" in i for i in issues)

def test_directory_as_samplesheet_is_flagged_not_crashed(tmp_path):
    # --input pointing at a directory must return a clear issue, not raise IsADirectoryError.
    d = tmp_path / "adir"
    d.mkdir()
    issues = samplesheet.validate(d, SCH)
    assert issues and "not a file" in issues[0]


def test_valid_sheet(tmp_path):
    (tmp_path / "r1.fq.gz").write_text("x")
    ss = tmp_path / "ss.csv"
    ss.write_text("sample,fastq_1\nA,r1.fq.gz\n")
    assert samplesheet.validate(ss, SCH) == []


# TSV samplesheets (e.g. nf-core/airrflow requires a strictly `.tsv` input): the validator must
# split on TAB by file extension, not read the whole comma-delimited header as one column (which
# reported every required column missing).
def test_tsv_delimiter_detected(tmp_path):
    (tmp_path / "r1.fq.gz").write_text("x")
    ss = tmp_path / "ss.tsv"
    ss.write_text("sample\tfastq_1\nA\tr1.fq.gz\n")
    assert samplesheet.validate(ss, SCH) == []

def test_tsv_missing_column_still_detected(tmp_path):
    ss = tmp_path / "ss.tsv"
    ss.write_text("sample\nA\n")               # tab-parsed header has only 'sample'
    issues = samplesheet.validate(ss, SCH)
    assert any("fastq_1" in i for i in issues)


# A UTF-8 BOM (common in spreadsheet-exported CSVs) must not make the first required column read
# as missing: the validator reads utf-8-sig so a leading BOM is stripped before header parsing.
def test_utf8_bom_header_is_stripped(tmp_path):
    (tmp_path / "r1.fq.gz").write_text("x")
    ss = tmp_path / "ss.csv"
    ss.write_bytes(b"\xef\xbb\xbf" + b"sample,fastq_1\nA,r1.fq.gz\n")   # leading BOM
    assert samplesheet.validate(ss, SCH) == []                          # was "missing column 'sample'"

def test_bom_does_not_mask_a_genuinely_missing_column(tmp_path):
    ss = tmp_path / "ss.csv"
    ss.write_bytes(b"\xef\xbb\xbf" + b"sample\nA\n")                     # BOM + fastq_1 truly absent
    assert any("fastq_1" in i for i in samplesheet.validate(ss, SCH))


# Headerless single-column input (nf-core/fetchngs id list): DictReader must NOT eat line 1.
UNNAMED = InputSchema(columns=(Column("", "string", False, "^SRR", None),))

def test_unnamed_single_column_accepts_one_value(tmp_path):
    f = tmp_path / "ids.txt"
    f.write_text("SRR123456\n")
    assert samplesheet.validate(f, UNNAMED) == []          # was wrongly "no data rows"

def test_unnamed_single_column_rejects_empty(tmp_path):
    f = tmp_path / "ids.txt"
    f.write_text("\n   \n")
    assert samplesheet.validate(f, UNNAMED) == ["input file has no values"]
