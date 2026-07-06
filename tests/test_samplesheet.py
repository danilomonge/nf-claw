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

def test_binary_samplesheet_is_flagged_not_crashed(tmp_path):
    # A non-text file (e.g. an .xlsx handed in as a .csv) must return a clear issue, not raise
    # UnicodeDecodeError. Covers both the named-column and headerless branches.
    ss = tmp_path / "book.csv"
    ss.write_bytes(bytes([0x50, 0x4b, 0x03, 0x04]) + bytes(range(200, 256)))   # not UTF-8
    named = samplesheet.validate(ss, SCH)
    assert named and "not valid UTF-8" in named[0]
    unnamed = samplesheet.validate(ss, InputSchema(columns=(Column("", "string", False, None, None),)))
    assert unnamed and "not valid UTF-8" in unnamed[0]


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


def test_non_tabular_named_input_is_deferred_to_nf_schema(tmp_path):
    # nf-core/sarek accepts YAML/JSON inputs even though it ships schema_input.json for tabular
    # samplesheets. The local pre-check must not parse those files as CSV and reject them before
    # Nextflow/nf-schema gets the format-specific validation.
    ss = tmp_path / "samples.json"
    ss.write_text('[{"patient": "P1", "sample": "S1"}]\n')
    assert samplesheet.validate(ss, SCH) == []


SAREK_LIKE = InputSchema(
    columns=(
        Column("patient", "string", True, None, None),
        Column("sample", "string", True, None, None),
        Column("lane", "integer or string", False, r"^\S+$", None),
        Column("fastq_1", "string", False, None, "file-path"),
        Column("fastq_2", "string", False, None, "file-path"),
        Column("spring_1", "string", False, None, "file-path"),
        Column("bam", "string", False, None, "file-path"),
    ),
    dependent_required=(("fastq_2", ("fastq_1",)),),
    any_of_dependent_required=(
        (("lane", ("fastq_1",)),),
        (("lane", ("spring_1",)),),
        (("lane", ("bam",)),),
    ),
)


def test_dependent_required_column_rule_is_reported(tmp_path):
    ss = tmp_path / "ss.csv"
    ss.write_text("patient,sample,fastq_2\nP1,S1,R2.fastq.gz\n")
    issues = samplesheet.validate(ss, SAREK_LIKE)
    assert "row 2: 'fastq_2' requires 'fastq_1'" in issues


def test_anyof_dependent_required_column_rule_is_reported(tmp_path):
    ss = tmp_path / "ss.csv"
    ss.write_text("patient,sample,lane\nP1,S1,1\n")
    issues = samplesheet.validate(ss, SAREK_LIKE)
    assert any("when 'lane' is set" in i and "fastq_1" in i and "bam" in i for i in issues)


def test_anyof_dependent_required_accepts_one_valid_branch(tmp_path):
    (tmp_path / "reads.bam").write_text("x")
    ss = tmp_path / "ss.csv"
    ss.write_text("patient,sample,lane,bam\nP1,S1,1,reads.bam\n")
    assert samplesheet.validate(ss, SAREK_LIKE) == []


def test_column_enum_pattern_and_range_rules_are_reported(tmp_path):
    (tmp_path / "r1.fq.gz").write_text("x")
    sch = InputSchema(columns=(
        Column("sample", "string", True, r"^\S+$", None),
        Column("fastq_1", "string", True, r".+\.f(ast)?q\.gz$", "file-path"),
        Column("strandedness", "string", True, None, None,
               enum=("forward", "reverse", "unstranded", "auto")),
        Column("percent_mapped", "number", False, None, None, minimum=0, maximum=100),
    ))
    ss = tmp_path / "ss.csv"
    ss.write_text("sample,fastq_1,strandedness,percent_mapped\n"
                  "bad sample,r1.fq.gz,sideways,101\n")
    issues = samplesheet.validate(ss, sch)
    assert any("sample" in i and "must match" in i for i in issues)
    assert any("strandedness" in i and "must be one of" in i for i in issues)
    assert any("percent_mapped" in i and "<= 100" in i for i in issues)


def test_column_integer_type_rule_is_reported(tmp_path):
    sch = InputSchema(columns=(
        Column("patient", "string", True, None, None),
        Column("sample", "string", True, None, None),
        Column("status", "integer", False, None, None, enum=("0", "1")),
    ))
    ss = tmp_path / "ss.csv"
    ss.write_text("patient,sample,status\nP1,S1,tumor\n")
    issues = samplesheet.validate(ss, sch)
    assert any("status" in i and "integer" in i for i in issues)


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
