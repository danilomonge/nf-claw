import json
from pathlib import Path

from librarian import write_catalog


def _seed(tmp_path):
    for name, ver in (("sarek", "3.8.1"), ("rnaseq", "3.14.0")):
        d = tmp_path / name
        (d / "upstream").mkdir(parents=True)
        d.joinpath("skill.md").write_text(
            f"---\nname: {name}\nversion: {ver}\ndescription: does {name}\n---\n")
    return tmp_path


def test_catalog_lists_all_sorted(tmp_path):
    pdir = _seed(tmp_path)
    out_md, out_json = tmp_path / "catalog.md", tmp_path / "catalog.json"
    write_catalog.generate(pipelines_dir=pdir, out_md=out_md, out_json=out_json)
    rows = json.loads(out_json.read_text())
    assert [r["name"] for r in rows] == ["rnaseq", "sarek"]
    assert "`sarek`" in out_md.read_text()


def test_catalog_deterministic(tmp_path):
    pdir = _seed(tmp_path)
    out_md, out_json = tmp_path / "c.md", tmp_path / "c.json"
    write_catalog.generate(pipelines_dir=pdir, out_md=out_md, out_json=out_json)
    a, b = out_md.read_text(), out_json.read_text()
    write_catalog.generate(pipelines_dir=pdir, out_md=out_md, out_json=out_json)
    assert out_md.read_text() == a and out_json.read_text() == b
