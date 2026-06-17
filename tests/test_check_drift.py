import shutil
from pathlib import Path

from librarian import write_skill, write_catalog, check_drift

FIX = Path(__file__).parent / "fixtures"


def _seed(tmp_path, name):
    up = tmp_path / "pipelines" / name / "upstream"
    up.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config"):
        (up / f).write_text("x")
    shutil.copy(FIX / name / "nextflow_schema.json", up / "nextflow_schema.json")
    return tmp_path / "pipelines"


def test_no_drift_when_freshly_generated(tmp_path):
    pdir = _seed(tmp_path, "mini")
    write_skill.generate("mini", pipelines_dir=pdir)
    write_catalog.generate(pipelines_dir=pdir,
                           out_md=tmp_path / "catalog.md", out_json=tmp_path / "catalog.json")
    assert check_drift.check(pdir) == []


def test_drift_when_skill_edited(tmp_path):
    pdir = _seed(tmp_path, "mini")
    write_skill.generate("mini", pipelines_dir=pdir)
    (pdir / "mini" / "skill.md").write_text("hand-edited\n")
    assert any("stale" in d for d in check_drift.check(pdir))


def test_check_drift_never_writes(tmp_path, monkeypatch):
    # The gate compares in memory via render(); it must never call the writing path.
    pdir = _seed(tmp_path, "mini")
    write_skill.generate("mini", pipelines_dir=pdir)
    write_catalog.generate(pipelines_dir=pdir,
                           out_md=tmp_path / "catalog.md", out_json=tmp_path / "catalog.json")

    def _boom(*a, **k):
        raise AssertionError("check_drift must not write files")
    monkeypatch.setattr(write_skill, "generate", _boom)
    assert check_drift.check(pdir) == []
