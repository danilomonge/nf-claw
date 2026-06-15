"""Regression tests for issues found in the exhaustive audit (F6, F7, F10)."""
import shutil
from pathlib import Path

from librarian import check_drift, write_catalog, write_skill
from runner.schema import Param, ParamSchema

FIX = Path(__file__).parent / "fixtures"


# --- F10: key params follow schema order (important flags surface), not alphabetical ---
def test_key_params_preserve_schema_order_not_alpha():
    # zzz_important is defined BEFORE aaa_minor in schema order; both have no default.
    ps = ParamSchema(title="t", description="d", params={
        "zzz_important": Param("zzz_important", "string", None, None, "key flag", None, False, "main"),
        "aaa_minor": Param("aaa_minor", "string", None, None, "minor flag", None, False, "advanced"),
    })
    out = write_skill._key_params(ps)
    # schema order keeps the important one first; an alphabetical sort would invert this.
    assert out.index("zzz-important") < out.index("aaa-minor")


def test_key_params_required_first():
    ps = ParamSchema(title="t", description="d", params={
        "optional_x": Param("optional_x", "string", None, None, "opt", None, False, "g"),
        "req_y": Param("req_y", "string", None, None, "req", None, True, "g"),
    })
    out = write_skill._key_params(ps)
    assert out.index("req-y") < out.index("optional-x")


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
