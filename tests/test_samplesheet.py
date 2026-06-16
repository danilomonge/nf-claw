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

def test_valid_sheet(tmp_path):
    (tmp_path / "r1.fq.gz").write_text("x")
    ss = tmp_path / "ss.csv"
    ss.write_text("sample,fastq_1\nA,r1.fq.gz\n")
    assert samplesheet.validate(ss, SCH) == []
