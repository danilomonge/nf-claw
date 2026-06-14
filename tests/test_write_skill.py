import shutil
from pathlib import Path

from librarian import write_skill

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
    for header in ("# mini", "## Run it", "## Inputs", "## Key parameters",
                   "## Outputs", "## Demo", "## Full reference"):
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
