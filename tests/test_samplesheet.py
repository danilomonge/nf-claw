from runner.schema import Column, InputSchema
from runner import samplesheet
import pytest

SCH = InputSchema(columns=(
    Column("sample", "string", True, None, None),
    Column("fastq_1", "string", True, None, "file-path"),
))


@pytest.mark.parametrize("extension,delimiter", [("csv", ","), ("tsv", "\t")])
def test_incomplete_quoted_record_cannot_silently_change_sample_metadata(tmp_path, extension, delimiter):
    schema = InputSchema(columns=(Column("sample", "string", True, None, None),
                                  Column("description", "string", False, None, None)))
    sheet = tmp_path / f"samples.{extension}"
    sheet.write_text(f'sample{delimiter}description\nA{delimiter}"unfinished\nB{delimiter}other\n')
    assert any("not parseable" in issue for issue in samplesheet.validate(sheet, schema))


def test_valid_quoted_multiline_field_remains_supported(tmp_path):
    schema = InputSchema(columns=(Column("sample", "string", True, None, None),
                                  Column("description", "string", False, None, None)))
    sheet = tmp_path / "samples.csv"
    sheet.write_text('sample,description\nA,"two\nlines"\nB,"quoted ""word"""\n')
    assert samplesheet.validate(sheet, schema) == []

def test_missing_required_column(tmp_path):
    ss = tmp_path / "ss.csv"
    ss.write_text("sample\nA\n")
    issues = samplesheet.validate(ss, SCH)
    assert any("fastq_1" in i for i in issues)

def test_missing_input_file(tmp_path):
    ss = tmp_path / "ss.csv"
    ss.write_text(f"sample,fastq_1\nA,{tmp_path / 'missing_R1.fastq.gz'}\n")
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
    ss.write_text(f"sample,fastq_1\nA,{tmp_path / 'r1.fq.gz'}\n")
    assert samplesheet.validate(ss, SCH) == []


# TSV samplesheets (e.g. nf-core/airrflow requires a strictly `.tsv` input): the validator must
# split on TAB by file extension, not read the whole comma-delimited header as one column (which
# reported every required column missing).
def test_tsv_delimiter_detected(tmp_path):
    (tmp_path / "r1.fq.gz").write_text("x")
    ss = tmp_path / "ss.tsv"
    ss.write_text(f"sample\tfastq_1\nA\t{tmp_path / 'r1.fq.gz'}\n")
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
    ss.write_text(f"patient,sample,lane,bam\nP1,S1,1,{tmp_path / 'reads.bam'}\n")
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
                  f"bad sample,{tmp_path / 'r1.fq.gz'},sideways,101\n")
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
    ss.write_bytes(b"\xef\xbb\xbf" + f"sample,fastq_1\nA,{tmp_path / 'r1.fq.gz'}\n".encode())  # BOM
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


# nf-schema resolves a relative samplesheet path against Nextflow's launch directory — which nfclaw
# sets to --outdir — not against the samplesheet's own folder. A relative path that exists next to
# the samplesheet therefore passed this check and then failed at runtime ("does not exist"), after
# --outdir and the provenance bundle had already been created. Reject it up front instead.
def test_relative_path_is_rejected_even_when_it_exists_next_to_the_samplesheet(tmp_path):
    (tmp_path / "r1.fq.gz").write_text("x")
    ss = tmp_path / "ss.csv"
    ss.write_text("sample,fastq_1\nA,r1.fq.gz\n")
    issues = samplesheet.validate(ss, SCH)
    assert len(issues) == 1
    assert "relative path" in issues[0] and "absolute" in issues[0] and "--outdir" in issues[0]


def test_tilde_path_is_relative_to_nextflow(tmp_path):
    # nf-schema does not expand `~` in samplesheet values (verified with nf-schema 2.6.1).
    ss = tmp_path / "ss.csv"
    ss.write_text("sample,fastq_1\nA,~/r1.fq.gz\n")
    assert any("relative path" in i for i in samplesheet.validate(ss, SCH))


def test_remote_paths_are_not_checked_locally(tmp_path):
    ss = tmp_path / "ss.csv"
    ss.write_text("sample,fastq_1\nA,s3://bucket/r1.fq.gz\n")
    assert samplesheet.validate(ss, SCH) == []


def test_path_format_columns_are_checked_too(tmp_path):
    # nf-schema's `path` format (a file or a directory; e.g. mhcquant's ReplicateFileName, sopa's
    # data_path) resolves exactly like `file-path`.
    sch = InputSchema(columns=(Column("sample", "string", True, None, None),
                               Column("data", "string", True, None, "path")))
    ss = tmp_path / "ss.csv"
    ss.write_text(f"sample,data\nA,data_dir\nB,{tmp_path / 'absent'}\n")
    issues = samplesheet.validate(ss, sch)
    assert any("row 2" in i and "relative path" in i for i in issues)
    assert any("row 3" in i and "file not found" in i for i in issues)


def test_unbalanced_quote_in_a_large_sheet_is_flagged_not_crashed(tmp_path):
    # One stray quote turns the rest of the file into a single field; past the csv module's field
    # size limit that raised a raw csv.Error traceback instead of a samplesheet issue.
    p = tmp_path / "ss.csv"
    p.write_text('sample\n"A\n' + "B\n" * 70000)
    issues = samplesheet.validate(p, SCH)
    assert len(issues) == 1 and "not parseable as CSV" in issues[0] and "quote" in issues[0]
    t = tmp_path / "ss.tsv"
    t.write_text('sample\n"A\n' + "B\n" * 70000)
    assert "not parseable as TSV" in samplesheet.validate(t, SCH)[0]


def test_unreadable_sheet_is_flagged_not_crashed(tmp_path, monkeypatch):
    # A sheet that exists but cannot be read (another user's file) raised a raw PermissionError.
    import pathlib
    ss = tmp_path / "ss.csv"
    ss.write_text("sample,fastq_1\n")
    real_open = pathlib.Path.open

    def deny(self, *a, **k):
        if self == ss:
            raise PermissionError(13, "Permission denied", str(self))
        return real_open(self, *a, **k)

    monkeypatch.setattr(pathlib.Path, "open", deny)
    assert samplesheet.validate(ss, SCH) == [f"samplesheet cannot be read: Permission denied: {ss}"]


# --- header_issues: the column-level half of validate, for a sheet that does not exist yet ---

_HEADER_SCH = InputSchema(
    columns=(Column("sample", "string", True, None),
             Column("fastq_1", "string", True, None, fmt="file-path"),
             Column("fastq_2", "string", False, None, fmt="file-path"),
             Column("lane", "string", False, None)),
    dependent_required=(("fastq_2", ("fastq_1",)),),
    any_of_dependent_required=((("lane", ("fastq_1",)),),),
)


def test_delimiter_follows_the_extension():
    from pathlib import Path
    assert samplesheet.delimiter_for(Path("a.tsv")) == "\t"
    assert samplesheet.delimiter_for(Path("a.TSV")) == "\t"
    assert samplesheet.delimiter_for(Path("a.csv")) == ","


def test_header_issues_accepts_a_header_that_can_satisfy_the_schema():
    assert samplesheet.header_issues(["sample", "fastq_1", "fastq_2", "extra"], _HEADER_SCH) == []


def test_header_issues_reports_missing_required_and_dependent_columns():
    issues = samplesheet.header_issues(["sample", "fastq_2"], _HEADER_SCH)
    assert "missing required column 'fastq_1'" in issues
    assert "'fastq_2' requires 'fastq_1'" in issues


def test_header_issues_requires_one_column_group():
    sheet = InputSchema(columns=(), one_of=(("sampleID", "forwardReads"), ("sample", "fastq_1")))
    assert samplesheet.header_issues(["sample", "fastq_1"], sheet) == []
    assert samplesheet.header_issues(["sample"], sheet) == [
        "needs one of these column sets: sampleID, forwardReads; sample, fastq_1"]
