"""The shipped handoff rules (handoffs/): they parse, name library pipelines, and fit the pinned
schemas. The fit needs initialized submodules; the drift gate (CI) has them."""
from pathlib import Path
import csv
import json

import pytest

from runner import handoff, schema, submodule

ROOT = Path(__file__).resolve().parent.parent
RULES = handoff.load_registry(ROOT)


def _tree(name):
    st = submodule.resolve(name, ROOT / "pipelines")
    if not st.complete:
        pytest.skip(f"{name} submodule not initialized")
    return st.path


def test_registry_parses_and_names_library_pipelines():
    assert ("fetchngs", "rnaseq") in RULES
    names = {d.name for d in (ROOT / "pipelines").iterdir() if d.is_dir()}
    for up, down in RULES:
        assert up in names and down in names, f"handoffs/{up}/{down}.json names an unknown pipeline"
        assert RULES[(up, down)].description, f"handoffs/{up}/{down}.json has no description"


@pytest.mark.parametrize("edge", sorted(RULES), ids=lambda e: f"{e[0]}->{e[1]}")
def test_every_rule_fits_the_pinned_schemas(edge):
    up, down = (_tree(n) for n in edge)
    assert handoff.check_rule(RULES[edge], up, down) == []


def test_fetchngs_rules_set_their_own_target_from_fetchngs_enum():
    # The direct handoffs rely on fetchngs's --nf-core-pipeline; its schema enum is the authority.
    enum = schema.load_param_schema(_tree("fetchngs")).params["nf_core_pipeline"].enum
    targets = [down for (up, down) in RULES if up == "fetchngs"]
    assert targets
    for down in targets:
        assert RULES[("fetchngs", down)].upstream_params == {"nf_core_pipeline": down}
        assert down in enum


@pytest.mark.parametrize("upstream", ["fetchngs", "detaxizer"])
def test_mag_handoff_keeps_different_samples_separate(library, finished_run, tmp_path, upstream):
    """Grouping all samples together would silently enable pooled binning in MAG."""
    root = library("mini")
    down = root / "pipelines/mini/upstream"
    schema_path = down / "assets/schema_input.json"
    sheet_schema = json.loads(schema_path.read_text())
    sheet_schema["items"]["properties"] = {
        "sample": {"type": "string"}, "group": {"type": ["string", "integer"]},
        "run": {"type": "string"},
        "short_reads_1": {"type": "string", "format": "file-path"},
        "short_reads_2": {"type": "string", "format": "file-path"},
        "short_reads_platform": {"type": "string"},
        "long_reads": {"type": "string", "format": "file-path"},
        "long_reads_platform": {"type": "string"},
    }
    sheet_schema["items"]["required"] = ["sample", "group", "short_reads_1"]
    schema_path.write_text(json.dumps(sheet_schema))
    rule = RULES[(upstream, "mag")]
    source = rule.params["input"].spec["samplesheet"]
    if upstream == "fetchngs":
        text = ("sample,fastq_1,fastq_2,group,short_reads_platform,run_accession\n"
                "A,{outdir}/A_1.fastq.gz,,0,ILLUMINA,run1\n"
                "A,{outdir}/A_2.fastq.gz,,0,ILLUMINA,run2\n"
                "B,{outdir}/B_1.fastq.gz,,0,ILLUMINA,run3\n")
    else:
        text = ("sample,run,group,short_reads_1,short_reads_2,long_reads\n"
                "A,run1,,{outdir}/A_1.fastq.gz,,\n"
                "A,run2,,{outdir}/A_2.fastq.gz,,\n"
                "B,run3,,{outdir}/B_1.fastq.gz,,\n")
    up = finished_run(tmp_path / "up", {source: text, "A_1.fastq.gz": "a1",
                                       "A_2.fastq.gz": "a2", "B_1.fastq.gz": "b1"})
    result = handoff.materialize(rule, upstream_outdir=up, downstream_tree=down,
                                dest=tmp_path / "handoff")
    with Path(result.params["input"]).open() as fh:
        rows = list(csv.DictReader(fh))
    assert [(row["sample"], row["group"]) for row in rows] == [("A", "A"), ("A", "A"), ("B", "B")]
