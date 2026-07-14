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


def test_render_status_uses_status_path_and_version(tmp_path):
    # render_status renders from an explicit status (any version's tree), reusing the same logic.
    up = tmp_path / "anytree" / "upstream"
    up.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config"):
        (up / f).write_text("x")
    shutil.copy(FIX / "mini" / "nextflow_schema.json", up / "nextflow_schema.json")
    st = SubmoduleStatus("mini", up, True, True, "1.2.0", "deadbeef", ())
    skill, ref = write_skill.render_status(st)
    assert "version: 1.2.0" in skill and "commit: deadbeef" in skill
    assert "# mini" in skill and "mini" in ref


def test_versioned_render_threads_pipeline_version_into_commands(tmp_path):
    # A version-specific skill.md must tell the agent to run THAT version, and its raw
    # equivalent must point at the materialized version tree — not the pinned default.
    up = tmp_path / "anytree" / "upstream"
    up.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config"):
        (up / f).write_text("x")
    shutil.copy(FIX / "mini" / "nextflow_schema.json", up / "nextflow_schema.json")
    st = SubmoduleStatus("mini", up, True, True, "1.2.0", "deadbeef", ())
    versioned, _ = write_skill.render_status(st, pipeline_version="1.2.0")
    assert "--pipeline-version 1.2.0" in versioned
    assert "pipelines/mini/.versions/1.2.0/upstream" in versioned
    # the default (pinned) run/demo COMMANDS must NOT carry a version flag — keeps the default run latest
    pinned, _ = write_skill.render_status(st)
    for line in pinned.splitlines():
        if line.startswith("nfclaw run"):
            assert "--pipeline-version" not in line
    assert "pipelines/mini/upstream" in pinned


def test_skill_surfaces_other_versions_for_discovery(tmp_path):
    # The committed (pinned) skill.md nudges the agent that other releases are runnable, so it can
    # discover them without grepping a file that only knows the pin.
    pdir = _seed(tmp_path, "mini")
    skill, _ = write_skill.generate("mini", pipelines_dir=pdir)
    text = skill.read_text()
    assert "nfclaw versions mini" in text
    assert "--pipeline-version" in text                       # the discoverability nudge (prose, not the run cmd)


def test_versioned_skill_omits_discovery_note(tmp_path):
    # A version-specific doc already explains the default in its Run-it comment; no extra nudge needed.
    up = tmp_path / "anytree" / "upstream"
    up.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config"):
        (up / f).write_text("x")
    shutil.copy(FIX / "mini" / "nextflow_schema.json", up / "nextflow_schema.json")
    st = SubmoduleStatus("mini", up, True, True, "1.2.0", "deadbeef", ())
    versioned, _ = write_skill.render_status(st, pipeline_version="1.2.0")
    assert "nfclaw versions" not in versioned


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


# --- tools: parsed from the software sections of the authors' own CITATIONS.md ---
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


def test_pipeline_tools_handles_asterisk_bullets(tmp_path):
    # Older nf-core releases (e.g. bactmap 1.0.0) use `* [Tool]` instead of `- [Tool]`.
    up = tmp_path / "upstream"
    up.mkdir()
    (up / "CITATIONS.md").write_text(
        "# x\n\n## Pipeline tools\n\n"
        "* [bcftools](u1)\n  > ref\n\n"
        "* [BWA](u2)\n\n"
        "+ [fastp](u3)\n")
    assert write_skill._pipeline_tools(up) == ["bcftools", "BWA", "fastp"]


def test_pipeline_tools_graceful_when_absent(tmp_path):
    up = tmp_path / "upstream"
    up.mkdir()
    assert write_skill._pipeline_tools(up) == []                 # no CITATIONS.md
    (up / "CITATIONS.md").write_text("# x\n\n## Pipeline tools\n\n")
    assert write_skill._pipeline_tools(up) == []                 # section present but empty
    (up / "CITATIONS.md").write_text("# x\n\n## [SomePaper](url)\n\n- [Z](u)\n")
    assert write_skill._pipeline_tools(up) == []                 # citation-link section, not software


def test_pipeline_tools_merges_software_sections(tmp_path):
    # Some pipelines (e.g. differentialabundance, detaxizer) split their software across
    # `## Pipeline tools` plus `## R packages` / `## Python`. All are tools the pipeline runs;
    # citation-link headers, packaging/containerisation infra and test-data/archive sections are not.
    up = tmp_path / "upstream"
    up.mkdir()
    (up / "CITATIONS.md").write_text(
        "# x: Citations\n\n"
        "## [nf-core](url)\n> ref\n\n"
        "## Pipeline tools\n\n- [GSEA](u1)\n\n"
        "## R packages\n\n- [DESeq2](u2)\n- [Limma](u3)\n\n"
        "## Python\n\n- [biopython](u4)\n\n"
        "## Data\n\n- [Full-size test data](u5)\n\n"
        "## Pipeline resources\n\n- [SRA](u6)\n\n"
        "## Software packaging/containerisation tools\n\n- [Docker](u7)\n")
    assert write_skill._pipeline_tools(up) == ["GSEA", "DESeq2", "Limma", "biopython"]


def test_skill_surfaces_tools_when_citations_present(tmp_path):
    pdir = _seed(tmp_path, "mini")
    (pdir / "mini" / "upstream" / "CITATIONS.md").write_text(
        "# mini\n\n## Pipeline tools\n\n- [FastQC](u)\n- [STAR](u)\n")
    skill, _ = write_skill.generate("mini", pipelines_dir=pdir)
    text = skill.read_text()
    assert "## Tools this pipeline runs" in text
    assert "FastQC" in text and "STAR" in text
    assert "tools: FastQC, STAR" in text.split("---")[1]          # frontmatter (for the catalog)


# --- summary: the authors' own one-paragraph description from the README `## Introduction` ---
def test_summary_extracts_first_prose_paragraph(tmp_path):
    up = tmp_path / "upstream"
    up.mkdir()
    (up / "README.md").write_text(
        "# nf-core/x\n\n## Introduction\n\n"
        "**nf-core/x** is a bioinformatics pipeline that analyses [RNA-seq](http://u) data "
        "and produces a gene matrix.\n\n"
        "![metro map](docs/map.svg)\n\n"
        "1. Step one\n2. Step two\n")
    assert write_skill._summary(up) == (
        "nf-core/x is a bioinformatics pipeline that analyses RNA-seq data and produces a gene matrix.")


def test_summary_skips_leading_image_and_heading(tmp_path):
    # drugresponseeval leads its Introduction with an image wrapped in a heading.
    up = tmp_path / "upstream"
    up.mkdir()
    (up / "README.md").write_text(
        "## Introduction\n\n"
        "# ![summary](assets/summary.svg)\n\n"
        "**DrEval** is a bioinformatics framework that evaluates drug response prediction models.\n")
    assert write_skill._summary(up) == (
        "DrEval is a bioinformatics framework that evaluates drug response prediction models.")


def test_summary_flattens_reference_style_links(tmp_path):
    up = tmp_path / "upstream"
    up.mkdir()
    (up / "README.md").write_text(
        "## Introduction\n\n"
        "nf-core/q implements the [fgbio Best Practices Pipeline][fgbio-ref] for consensus calling.\n")
    assert write_skill._summary(up) == (
        "nf-core/q implements the fgbio Best Practices Pipeline for consensus calling.")


def test_summary_graceful_when_absent(tmp_path):
    up = tmp_path / "upstream"
    up.mkdir()
    assert write_skill._summary(up) == ""                       # no README.md
    (up / "README.md").write_text("# x\n\n## Usage\n\nrun it\n")
    assert write_skill._summary(up) == ""                       # no Introduction section
    (up / "README.md").write_text("## Introduction\n\n![only an image](i.svg)\n")
    assert write_skill._summary(up) == ""                       # no prose paragraph


def test_skill_surfaces_summary_with_fallback(tmp_path):
    pdir = _seed(tmp_path, "mini")
    (pdir / "mini" / "upstream" / "README.md").write_text(
        "## Introduction\n\nnf-core/mini is a pipeline that does a specific scientific thing well.\n")
    skill, _ = write_skill.generate("mini", pipelines_dir=pdir)
    text = skill.read_text()
    assert "summary: nf-core/mini is a pipeline that does a specific scientific thing well." in text.split("---")[1]
    assert "nf-core/mini is a pipeline that does a specific scientific thing well." in text  # body too


def test_skill_summary_falls_back_to_description(tmp_path):
    # mini fixture has no README -> summary frontmatter falls back to the terse description.
    pdir = _seed(tmp_path, "mini")
    skill, _ = write_skill.generate("mini", pipelines_dir=pdir)
    fm = skill.read_text().split("---")[1]
    assert "summary:" in fm and "description:" in fm


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


def test_samplesheet_header_carries_only_the_required_columns(tmp_path):
    # The header must be a samplesheet that is always valid. A pipeline can declare optional columns
    # that only apply to one aligner/mode, and emitting every column produces a header with fields an
    # agent then has to fill or blank out. Optional columns are named below it, so nothing is lost.
    pdir = _seed(tmp_path, "mini")
    skill, _ = write_skill.generate("mini", pipelines_dir=pdir)
    text = skill.read_text()
    header = text.split("```csv\n", 1)[1].split("\n", 1)[0]
    assert header == "sample,fastq_1"                 # fastq_2 is optional in the mini fixture
    assert "may be appended to the header" in text and "`fastq_2`" in text


def test_mandatory_group_params_are_surfaced_even_though_they_have_defaults(tmp_path):
    # nf-core marks required-ness in two places that disagree: the JSON-schema `required` list and
    # the group title. A param with a default is never in `required` (nf-schema cannot fail it), yet
    # the pipeline may still reject the default at runtime — nf-core/scrnaseq's `--protocol` aborts
    # the run on its own default for every aligner but cellranger. Reading only `required` hides it.
    import json

    up = tmp_path / "mand" / "upstream"
    up.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config"):
        (up / f).write_text("x")
    (up / "nextflow_schema.json").write_text(json.dumps({
        "title": "nf-core/mand",
        "definitions": {
            "input_output_options": {
                "title": "Input/output options",
                "properties": {"outdir": {"type": "string", "format": "directory-path"}},
                "required": ["outdir"],
            },
            "mandatory_arguments": {
                "title": "Mandatory arguments",
                "properties": {"protocol": {"type": "string", "default": "auto",
                                            "description": "The protocol used."}},
            },
        },
    }))
    skill, _ = write_skill.generate("mand", pipelines_dir=tmp_path)
    text = skill.read_text()
    assert "## Mandatory arguments" in text
    assert "`--protocol`" in text                       # the flag itself, with its default
    assert "the pipeline itself can reject the default at runtime" in text


def test_no_mandatory_section_when_the_schema_has_no_such_group(tmp_path):
    pdir = _seed(tmp_path, "mini")
    skill, _ = write_skill.generate("mini", pipelines_dir=pdir)
    assert "## Mandatory arguments" not in skill.read_text()


def test_resources_section_documents_the_nf_core_resource_ceiling(tmp_path):
    # The stock nf-core process labels are sized for a server; on a workstation a real run dies at
    # the first big step. resourceLimits is the mechanism nf-core documents for capping it.
    pdir = _seed(tmp_path, "mini")
    skill, _ = write_skill.generate("mini", pipelines_dir=pdir)
    text = skill.read_text()
    assert "## Resources" in text
    assert "--limit-cpus 4 --limit-memory 15.GB --limit-time 1.h" in text
    assert "process.resourceLimits" in text
    assert "nf-co.re/docs/running/configuration/nextflow-for-your-system" in text


def test_group_list_uses_the_schemas_own_titles(tmp_path):
    pdir = _seed(tmp_path, "mini")
    skill, _ = write_skill.generate("mini", pipelines_dir=pdir)
    assert "**Input/output options** (`input_output_options`)" in skill.read_text()


def test_skill_names_the_engine_the_release_declares(tmp_path):
    # The engine is not a neutral detail: a newer Nextflow major changes the config parser.
    pdir = _seed(tmp_path, "mini")
    (pdir / "mini" / "upstream" / "nextflow.config").write_text(
        "manifest {\n    nextflowVersion = '!>=25.10.4'\n}\n")
    skill, _ = write_skill.generate("mini", pipelines_dir=pdir)
    text = skill.read_text()
    assert "## Nextflow engine" in text
    assert "!>=25.10.4" in text
    assert "--nxf-ver 25.10.4" in text                 # the exact flag to pin it


def test_no_engine_section_when_the_release_declares_nothing(tmp_path):
    pdir = _seed(tmp_path, "mini")                     # seeded nextflow.config has no manifest
    skill, _ = write_skill.generate("mini", pipelines_dir=pdir)
    assert "## Nextflow engine" not in skill.read_text()


def _seed_with_schema(tmp_path, name, schema):
    import json

    up = tmp_path / name / "upstream"
    up.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config"):
        (up / f).write_text("x")
    (up / "nextflow_schema.json").write_text(json.dumps(schema))
    return tmp_path


def test_warns_when_the_release_resolves_a_reference_from_s3_by_default(tmp_path):
    # sarek defaults --genome to GATK.GRCh38, resolved through AWS iGenomes at s3://ngi-igenomes/.
    # A run passing no reference of its own silently reads from S3 — it fails on a host without
    # access to that bucket. The basic recipe looked runnable when it was not.
    pdir = _seed_with_schema(tmp_path, "refs", {
        "title": "nf-core/refs",
        "definitions": {"reference_genome_options": {
            "title": "Reference genome options",
            "properties": {
                "genome": {"type": "string", "default": "GATK.GRCh38"},
                "igenomes_base": {"type": "string", "default": "s3://ngi-igenomes/igenomes/"},
                "igenomes_ignore": {"type": "boolean"},
            }}}})
    text = write_skill.generate("refs", pipelines_dir=pdir)[0].read_text()
    assert "## Reference genome" in text
    assert "resolves a reference genome remotely by default" in text
    assert "GATK.GRCh38" in text and "s3://ngi-igenomes/igenomes/" in text
    assert "--igenomes-ignore true" in text            # the documented way to switch it off


def test_states_that_no_reference_is_set_when_the_default_is_null(tmp_path):
    # rnaseq/scrnaseq: --genome has no default, so nothing is fetched behind the caller's back.
    pdir = _seed_with_schema(tmp_path, "norefs", {
        "title": "nf-core/norefs",
        "definitions": {"reference_genome_options": {
            "title": "Reference genome options",
            "properties": {
                "genome": {"type": "string"},
                "igenomes_base": {"type": "string", "default": "s3://ngi-igenomes/igenomes/"},
            }}}})
    text = write_skill.generate("norefs", pipelines_dir=pdir)[0].read_text()
    assert "No reference genome is set by default" in text
    assert "resolves a reference genome remotely by default" not in text


def test_no_reference_section_when_the_pipeline_has_no_genome_params(tmp_path):
    pdir = _seed(tmp_path, "mini")
    assert "## Reference genome" not in write_skill.generate(
        "mini", pipelines_dir=pdir)[0].read_text()
