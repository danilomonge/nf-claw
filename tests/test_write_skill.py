import shutil
from pathlib import Path

from librarian import write_skill
from runner.schema import Param, ParamSchema
from runner.submodule import SubmoduleStatus

FIX = Path(__file__).parent / "fixtures"


def _seed(tmp_path, name):
    up = tmp_path / name / "upstream"
    up.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config"):
        (up / f).write_text("x")
    shutil.copy(FIX / name / "nextflow_schema.json", up / "nextflow_schema.json")
    src_in = FIX / name / "assets" / "schema_input.json"
    if src_in.exists():
        (up / "assets").mkdir(exist_ok=True)
        shutil.copy(src_in, up / "assets" / "schema_input.json")
    return tmp_path


def test_skill_md_has_fixed_sections(tmp_path):
    pdir = _seed(tmp_path, "mini")
    skill, ref = write_skill.generate("mini", pipelines_dir=pdir)
    text = skill.read_text()
    for header in ("# mini", "## Run it", "## Inputs", "## Required parameters",
                   "## Other parameters", "## Outputs", "## Demo", "## Full reference"):
        assert header in text
    assert "Do not edit by hand" in text


def test_deterministic_idempotent(tmp_path):
    pdir = _seed(tmp_path, "mini")
    s1, r1 = write_skill.generate("mini", pipelines_dir=pdir)
    a, b = s1.read_text(), r1.read_text()
    write_skill.generate("mini", pipelines_dir=pdir)
    assert s1.read_text() == a and r1.read_text() == b


def test_reference_covers_all_params(tmp_path):
    from runner import schema
    pdir = _seed(tmp_path, "mini")
    _, ref = write_skill.generate("mini", pipelines_dir=pdir)
    ps = schema.load_param_schema(pdir / "mini" / "upstream")
    text = ref.read_text()
    for name in list(ps.known_params())[:25]:
        assert f"`{name}`" in text or f"--{name.replace('_', '-')}" in text


def test_no_samplesheet_graceful(tmp_path):
    pdir = _seed(tmp_path, "mini_no_input")
    skill, _ = write_skill.generate("mini_no_input", pipelines_dir=pdir)
    text = skill.read_text()
    assert "does not use a samplesheet" in text
    assert "has_samplesheet: false" in text
    assert "input: parameters (no samplesheet)" in text


def test_input_summary_from_schema():
    from runner.schema import Column, InputSchema
    assert write_skill._input_summary(None) == "parameters (no samplesheet)"
    cols = InputSchema(columns=(
        Column("sample", "string", True, None),
        Column("fastq_1", "string", True, None),
    ))
    assert write_skill._input_summary(cols) == "samplesheet (sample, fastq_1)"
    idlist = InputSchema(columns=(Column("", "string", True, r"^\S+$"),))
    assert write_skill._input_summary(idlist) == "id list (one value per line)"


def test_multiqc_detection_and_output_summary(tmp_path):
    up = tmp_path / "upstream"
    (up / "modules" / "nf-core" / "multiqc").mkdir(parents=True)
    assert write_skill._produces_multiqc(up) is True
    assert "MultiQC report" in write_skill._output_summary(up)
    bare = tmp_path / "bare"
    bare.mkdir()
    assert write_skill._produces_multiqc(bare) is False
    out = write_skill._output_summary(bare)
    assert "pipeline_info/" in out and "MultiQC" not in out


def test_skill_frontmatter_has_input_output(tmp_path):
    pdir = _seed(tmp_path, "mini")
    skill, _ = write_skill.generate("mini", pipelines_dir=pdir)
    fm = skill.read_text().split("---")[1]
    assert "input:" in fm and "output:" in fm


def test_required_params_only(tmp_path):
    # skill.md lists ONLY schema-required params (a fact) — no heuristic "importance" guess.
    ps = ParamSchema(title="t", description="d", params={
        "input": Param("input", "string", None, None, "samplesheet", None, True, "io"),
        "step": Param("step", "string", "mapping", ("mapping", "markduplicates"), "start step", None, True, "main"),
        "aligner": Param("aligner", "string", "star", ("star", "hisat2"), "aligner", None, False, "ref"),
        "email": Param("email", "string", None, None, "boilerplate", None, False, "generic", True),
    })
    out = write_skill._required_params(ps)
    assert "--input" in out and "--step" in out          # required → shown
    assert "mapping, markduplicates" in out              # allowed values rendered for required enum
    assert "aligner" not in out and "email" not in out   # optional → not shown


# --- tools: parsed from the authors' own `## Pipeline tools` section of CITATIONS.md ---
def test_pipeline_tools_parses_citations(tmp_path):
    up = tmp_path / "upstream"
    up.mkdir()
    (up / "CITATIONS.md").write_text(
        "# x: Citations\n\n"
        "## [nf-core](url)\n> ref\n\n"
        "## [Nextflow](url)\n> ref\n\n"
        "## Pipeline tools\n\n"
        "- [FastQC](u1)\n\n"
        "- [STAR](u2)\n  > extra reference line\n\n"
        "- [Salmon](u3)\n\n"
        "## Software packaging/containerisation tools\n\n"
        "- [Docker](ud)\n")
    # only the curated Pipeline-tools section; packaging tools are excluded
    assert write_skill._pipeline_tools(up) == ["FastQC", "STAR", "Salmon"]


def test_pipeline_tools_graceful_when_absent(tmp_path):
    up = tmp_path / "upstream"
    up.mkdir()
    assert write_skill._pipeline_tools(up) == []                 # no CITATIONS.md
    (up / "CITATIONS.md").write_text("# x\n\n## Pipeline tools\n\n")
    assert write_skill._pipeline_tools(up) == []                 # section present but empty
    (up / "CITATIONS.md").write_text("# x\n\n## Other\n\n- [Z](u)\n")
    assert write_skill._pipeline_tools(up) == []                 # no tools section


def test_skill_surfaces_tools_when_citations_present(tmp_path):
    pdir = _seed(tmp_path, "mini")
    (pdir / "mini" / "upstream" / "CITATIONS.md").write_text(
        "# mini\n\n## Pipeline tools\n\n- [FastQC](u)\n- [STAR](u)\n")
    skill, _ = write_skill.generate("mini", pipelines_dir=pdir)
    text = skill.read_text()
    assert "## Tools this pipeline runs" in text
    assert "FastQC" in text and "STAR" in text
    assert "tools: FastQC, STAR" in text.split("---")[1]          # frontmatter (for the catalog)


# --- _cell: free text is collapsed to one line and pipe-escaped so tables never break ---
def test_cell_collapses_whitespace_and_escapes_pipes():
    assert write_skill._cell("a\n\nb") == "a b"
    assert write_skill._cell("x  |  y") == "x \\| y"
    assert write_skill._cell("p\tq\nr") == "p q r"


def test_reference_row_is_single_line_and_pipe_safe():
    st = SubmoduleStatus("t", Path("/x"), True, True, "1.0.0", "abc", ())
    desc = "First sentence.\n\nSecond with a | pipe."
    ps = ParamSchema(title="t", description="d", params={
        "weird": Param("weird", "string", None, None, desc, None, False, "g"),
    })
    out = write_skill._render_reference("t", st, ps, None)
    rows = [ln for ln in out.splitlines() if ln.startswith("| `--weird`")]
    assert len(rows) == 1                                       # newlines didn't split the row
    assert "First sentence. Second with a \\| pipe." in rows[0]  # collapsed + pipe escaped
