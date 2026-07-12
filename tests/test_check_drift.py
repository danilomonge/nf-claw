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


def test_drift_reports_incomplete_submodule_without_traceback(tmp_path):
    pdir = tmp_path / "pipelines"
    (pdir / "empty" / "upstream").mkdir(parents=True)
    drift = check_drift.check(pdir)
    assert (
        "empty/upstream is incomplete (missing main.nf, nextflow.config, nextflow_schema.json; "
        "run `git submodule update --init pipelines/empty/upstream`)"
    ) in drift


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


def test_drift_reports_manifest_set_and_remote_mismatches(tmp_path):
    pdir = _seed(tmp_path, "mini")
    write_skill.generate("mini", pipelines_dir=pdir)
    write_catalog.generate(pipelines_dir=pdir,
                           out_md=tmp_path / "catalog.md", out_json=tmp_path / "catalog.json")
    (tmp_path / "sources.tsv").write_text(
        "mini\thttps://github.com/nf-core/wrong.git\tlatest-release\n"
        "extra\thttps://github.com/nf-core/extra.git\tlatest-release\n"
    )
    (tmp_path / ".gitmodules").write_text(
        '[submodule "pipelines/mini/upstream"]\n'
        "\tpath = pipelines/mini/upstream\n"
        "\turl = https://github.com/nf-core/mini.git\n"
    )
    drift = check_drift.check(pdir)
    assert "sources.tsv has unknown pipelines: extra" in drift
    assert any(item.startswith("mini remote differs:") for item in drift)
