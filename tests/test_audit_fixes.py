"""Regression tests for the exhaustive audit (F6-F13) and the schema-surfacing pass.

The surfacing pass guarantees every fact the loader captures is rendered downstream:
`hidden`, column `pattern`, the path-format marker and the schema `title`. It also makes
`Column.fmt` symmetric with `Param.fmt` (both carry file-path/directory-path), so a
samplesheet directory column is no longer silently flattened to a plain string.
"""
import shutil
from pathlib import Path

from librarian import check_drift, write_catalog, write_skill
from runner.schema import Column, InputSchema, Param, ParamSchema

FIX = Path(__file__).parent / "fixtures"


# --- F10 (revised): skill.md is deterministic — ONLY schema-required params + a group map.
#     The earlier heuristic (required-or-no-default, schema order, cap 20) was removed: for
#     scientific use the agent must not rely on a guessed "importance" subset. ---
def test_required_params_lists_only_required_in_schema_order():
    ps = ParamSchema(title="t", description="d", params={
        "input": Param("input", "string", None, None, "ss", None, True, "io"),
        "outdir": Param("outdir", "string", None, None, "out", None, True, "io"),
        "aligner": Param("aligner", "string", "star", None, "no default but optional", None, False, "ref"),
    })
    out = write_skill._required_params(ps)
    assert "--input" in out and "--outdir" in out          # required → shown
    assert "aligner" not in out                            # optional (even no-default) → not shown
    assert out.index("--input") < out.index("--outdir")    # schema order preserved


def test_param_groups_maps_every_group_with_counts():
    ps = ParamSchema(title="t", description="d", params={
        "a": Param("a", "string", None, None, "x", None, True, "input_output"),
        "b": Param("b", "string", "d", None, "y", None, False, "advanced"),
        "c": Param("c", "string", "d", None, "z", None, False, "advanced"),
    })
    out = write_skill._param_groups(ps)
    assert "`input_output` (1 parameters)" in out
    assert "`advanced` (2 parameters)" in out


# --- F6: catalog.md escapes pipes in the description cell ---
def test_catalog_md_escapes_pipes(tmp_path):
    d = tmp_path / "pX"
    (d / "upstream").mkdir(parents=True)
    (d / "skill.md").write_text("---\nname: pX\nversion: 1.0.0\ndescription: does A | B things\n---\n")
    out_md, out_json = tmp_path / "catalog.md", tmp_path / "catalog.json"
    write_catalog.generate(pipelines_dir=tmp_path, out_md=out_md, out_json=out_json)
    md = out_md.read_text()
    assert "A \\| B" in md
    row = next(line for line in md.splitlines() if line.startswith("| `pX`"))
    # 4 unescaped pipes = exactly 3 columns (bookends + 2 separators); no extra column from the desc
    assert row.count("|") - row.count("\\|") == 4


# --- F7: the drift gate now covers catalog.{md,json} ---
def test_check_drift_detects_stale_catalog(tmp_path):
    repo = tmp_path
    pdir = repo / "pipelines"
    up = pdir / "pY" / "upstream"
    up.mkdir(parents=True)
    shutil.copy(FIX / "mini" / "nextflow_schema.json", up / "nextflow_schema.json")
    write_skill.generate("pY", pipelines_dir=pdir)          # correct skill.md + reference.md
    (repo / "catalog.md").write_text("STALE\n")
    (repo / "catalog.json").write_text("[]\n")
    drift = check_drift.check(pdir)
    assert any("catalog.md" in d for d in drift)
    assert not any("pY/skill.md" in d for d in drift)        # skill.md itself is in sync


# --- F11: unnamed-column input schema (e.g. fetchngs id list) renders cleanly ---
def test_inputs_section_handles_unnamed_single_column():
    insch = InputSchema(columns=(Column("", "string", False, "^SRR", None),))
    out = write_skill._inputs_section(insch)
    assert "one value per line" in out
    assert "| `` |" not in out          # no broken empty-named table cell


def test_inputs_section_named_columns_still_render_table():
    insch = InputSchema(columns=(
        Column("sample", "string", True, None, None),
        Column("fastq_1", "string", True, None, "file-path"),
    ))
    out = write_skill._inputs_section(insch)
    assert "| `sample` |" in out and "| `fastq_1` |" in out


# --- F12: update_pipelines honours the sources.tsv policy column ---
def test_update_pipelines_respects_policy(tmp_path, monkeypatch):
    from librarian import update_pipelines
    src = tmp_path / "sources.tsv"
    src.write_text("a\thttps://x/a.git\tlatest-release\nb\thttps://x/b.git\tpinned\n")
    bumped: list[str] = []
    monkeypatch.setattr(update_pipelines, "bump",
                        lambda name, url, root: (bumped.append(name), "1.0.0")[1])
    update_pipelines.main(["--sources", str(src), "--repo-root", str(tmp_path)])
    assert bumped == ["a"]   # only the latest-release pipeline is bumped; pinned 'b' is skipped


# --- F13: samplesheet inputs are schema-faithful — allowed values shown, NO fabricated values ---
def test_inputs_section_shows_enum_and_no_fabricated_values():
    insch = InputSchema(columns=(
        Column("sample", "string", True, None, None),
        Column("sex", "string", False, None, None, enum=("XX", "XY", "NA")),
        Column("fastq_1", "string", False, None, "file-path"),
    ))
    out = write_skill._inputs_section(insch)
    assert "XX, XY, NA" in out                                   # enum → allowed values (a fact)
    assert "string (file path)" in out                          # file-path columns marked
    assert "data/sample1_" not in out and "sample1" not in out  # no invented values
    csv = out.split("```csv\n")[1].split("```")[0].strip()
    assert csv == "sample,sex,fastq_1"                           # csv block is the real header only


def test_load_input_schema_captures_column_enum(tmp_path):
    from runner import schema
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "schema_input.json").write_text(
        '{"items": {"properties": {"status": {"type": "integer", "enum": [0, 1]}}, '
        '"required": ["status"]}}')
    insch = schema.load_input_schema(tmp_path)
    col = insch.columns[0]
    assert col.name == "status" and col.enum == ("0", "1")      # ints rendered as strings


# --- Surfacing pass: every fact the loader captures is rendered; Param.fmt and Column.fmt
#     are symmetric (both file-path AND directory-path); hidden/pattern/title all reach docs. ---
def test_type_with_fmt_marks_only_path_formats():
    assert write_skill._type_with_fmt("string", "file-path") == "string (file path)"
    assert write_skill._type_with_fmt("string", "directory-path") == "string (directory path)"
    assert write_skill._type_with_fmt("integer", None) == "integer"
    assert write_skill._type_with_fmt("string", "email") == "string"   # non-path format → unchanged


def test_column_fmt_is_symmetric_with_param_and_drives_is_path(tmp_path):
    from runner import schema
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "schema_input.json").write_text(
        '{"items": {"properties": {'
        '"reads": {"type": "string", "format": "file-path"}, '
        '"refdir": {"type": "string", "format": "directory-path"}, '
        '"name": {"type": "string"}}}}')
    cols = {c.name: c for c in schema.load_input_schema(tmp_path).columns}
    assert cols["reads"].fmt == "file-path" and cols["reads"].is_path is True
    assert cols["refdir"].fmt == "directory-path" and cols["refdir"].is_path is True   # not flattened
    assert cols["name"].fmt is None and cols["name"].is_path is False


def test_inputs_section_surfaces_pattern_and_directory_path():
    insch = InputSchema(columns=(
        Column("sample", "string", True, r"^\S+$", None),
        Column("reads", "string", False, r"^\S+\.fq\.gz$", "file-path"),
        Column("refdir", "string", False, None, "directory-path"),
    ))
    out = write_skill._inputs_section(insch)
    assert "| pattern |" in out                       # pattern column header present
    assert r"^\S+\.fq\.gz$" in out                     # a real column pattern rendered (a fact)
    assert "string (file path)" in out                 # file-path marker
    assert "string (directory path)" in out            # directory-path marker (was lost before)


def test_load_param_schema_captures_hidden(tmp_path):
    from runner import schema
    (tmp_path / "nextflow_schema.json").write_text(
        '{"title": "t", "definitions": {"g": {"properties": {'
        '"email": {"type": "string", "hidden": true}, '
        '"input": {"type": "string"}}}}}')
    ps = schema.load_param_schema(tmp_path)
    assert ps.params["email"].hidden is True
    assert ps.params["input"].hidden is False


def test_reference_surfaces_hidden_fmt_and_title():
    from runner.submodule import SubmoduleStatus
    st = SubmoduleStatus(name="pZ", path=Path("/x"), initialized=True, complete=True,
                         version="1.0.0", commit="abc1234", missing_files=())
    ps = ParamSchema(title="nf-core/pZ parameters", description="d", params={
        "input": Param("input", "string", None, None, "samplesheet", "file-path", True, "io"),
        "outdir": Param("outdir", "string", None, None, "results", "directory-path", True, "io"),
        "email": Param("email", "string", None, None, "notify", None, False, "generic", hidden=True),
    })
    out = write_skill._render_reference("pZ", st, ps, None)
    assert "nf-core/pZ parameters" in out               # schema title surfaced in the intro
    assert "| hidden |" in out                           # hidden column present
    assert "string (file path)" in out                   # Param.fmt surfaced
    assert "string (directory path)" in out              # directory-path Param.fmt surfaced
    email_row = next(l for l in out.splitlines() if l.startswith("| `--email`"))
    assert email_row.split("|")[4].strip() == "yes"      # hidden cell = yes for hidden param
    input_row = next(l for l in out.splitlines() if l.startswith("| `--input`"))
    assert input_row.split("|")[4].strip() == ""         # non-hidden → blank hidden cell


def test_required_params_marks_path_formats():
    ps = ParamSchema(title="t", description="d", params={
        "input": Param("input", "string", None, None, "ss", "file-path", True, "io"),
        "outdir": Param("outdir", "string", None, None, "out", "directory-path", True, "io"),
    })
    out = write_skill._required_params(ps)
    assert "string (file path)" in out
    assert "string (directory path)" in out
