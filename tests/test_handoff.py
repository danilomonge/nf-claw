"""Handoff rules: their shape, their fit with two pipelines' schemas, and producing a handoff from a
finished upstream run. `mini_up` and `mini` are synthetic fixture pipelines; `mini` takes a samplesheet
(sample, fastq_1, fastq_2 — the FastQ columns are file paths)."""
import csv

import pytest

from runner import handoff
from runner.errors import ErrorCode, NfclawError

DIRECT = {"description": "mini_up writes a mini sheet",
          "upstream_params": {"nf_core_pipeline": "mini"},
          "params": {"input": {"samplesheet": "samplesheet/samplesheet.csv",
                               "provides": ["sample", "fastq_1", "fastq_2"]}}}


def _rule(body, up="mini_up", down="mini"):
    return handoff.parse_rule(body, upstream=up, downstream=down, origin="test")


def _trees(root):
    pdir = root / "pipelines"
    return pdir / "mini_up" / "upstream", pdir / "mini" / "upstream"


def _rows(path):
    with path.open(newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t" if path.suffix == ".tsv" else ","))


# --- rules: shape, registry, static fit ---------------------------------------------------

def test_registry_is_keyed_by_upstream_and_downstream(library):
    root = library("mini_up", "mini", rules={("mini_up", "mini"): DIRECT})
    rules = handoff.load_registry(root)
    assert list(rules) == [("mini_up", "mini")]
    assert rules[("mini_up", "mini")].origin == "handoffs/mini_up/mini.json"
    assert rules[("mini_up", "mini")].description == "mini_up writes a mini sheet"


def test_no_registry_directory_means_no_rules(tmp_path):
    assert handoff.load_registry(tmp_path) == {}


def test_a_rule_file_that_is_not_json_fails_clearly(library):
    root = library("mini_up", "mini")
    bad = root / "handoffs" / "mini_up" / "mini.json"
    bad.parent.mkdir(parents=True)
    bad.write_text("{nope")
    with pytest.raises(NfclawError, match="handoffs/mini_up/mini.json cannot be read"):
        handoff.load_registry(root)


@pytest.mark.parametrize("body, msg", [
    ([], "must be a JSON object"),
    ({"params": {}}, "at least one downstream parameter"),
    ({"params": {"input": {"file": "a", "upstream_param": "b"}}}, "exactly one of"),
    ({"params": {"input": {"samplesheet": "s.csv"}}}, "'provides'"),
    ({"params": {"input": {"file": "../escape.tsv"}}}, "relative path inside the upstream outdir"),
    ({"params": {"input": {"file": "/abs/x.tsv"}}}, "relative path inside the upstream outdir"),
    ({"params": {"input": {"file": "x.tsv", "rename": {}}}}, "unknown keys for a file source"),
    ({"params": {"input": {"build": {"rows": "r/{s}.fq", "columns": {"x": "{t}"}}}}},
     r"'\{t\}', which is not captured"),
    ({"params": {"input": {"build": {"rows": "r/x.fq", "columns": {"x": "y"}}}}},
     "placeholder"),
    ({"params": {"input": {"samplesheet": "s.csv", "provides": ["a"], "set": {"b": 1}}}},
     "'set' must map column names to strings"),
    ({"params": {"x": {"file": "a"}}, "surprise": 1}, "unknown keys"),
])
def test_malformed_rules_fail_clearly(body, msg):
    with pytest.raises(NfclawError, match=msg) as err:
        _rule(body)
    assert err.value.code is ErrorCode.PARAMS_INVALID


def test_compatible_rule_has_no_issues(library):
    up, down = _trees(library("mini_up", "mini"))
    assert handoff.check_rule(_rule(DIRECT), up, down) == []


def test_check_rule_reports_every_incompatibility(library):
    up, down = _trees(library("mini_up", "mini"))
    body = {"upstream_params": {"nf_core_pipeline": "nope", "unknown_flag": 1},
            "params": {"input": {"samplesheet": "s.csv", "provides": ["sample"]},
                       "not_a_param": {"file": "x.tsv"},
                       "fasta": {"upstream_param": "missing"},
                       "aligner": {"build": {"rows": "r/{s}.fq", "columns": {"sample": "{s}"}}}}}
    issues = "\n".join(handoff.check_rule(_rule(body), up, down))
    assert "must be one of: mini, other" in issues                 # enum from the upstream schema
    assert "unknown parameter '--unknown-flag'" in issues
    assert "missing required column 'fastq_1'" in issues           # from the downstream sheet schema
    assert "has no parameter '--not-a-param'" in issues
    assert "mini_up has no parameter '--missing'" in issues
    assert "'--aligner' of mini is not a samplesheet" in issues
    assert all(line.startswith("test: ") for line in issues.splitlines())


def test_rename_and_set_count_towards_the_provided_columns():
    src = _rule({"params": {"input": {"samplesheet": "s.csv", "provides": ["sample", "reads_1"],
                                      "rename": {"reads_1": "fastq_1"}, "set": {"lane": "1"}}}}
                ).params["input"]
    assert handoff.provided_columns(src) == ["sample", "fastq_1", "lane"]


def test_rule_hash_is_stable_and_content_addressed():
    assert _rule(DIRECT).sha256() == _rule(dict(DIRECT)).sha256()
    assert _rule(DIRECT).sha256() != _rule({**DIRECT, "description": "other"}).sha256()


# --- materialize: producing the handoff from a finished run ------------------------------

SHEET = ('"sample","fastq_1","fastq_2","run_accession"\n'
         '"A","{outdir}/fastq/A_1.fastq.gz","{outdir}/fastq/A_2.fastq.gz","SRR1"\n')
FASTQS = {"fastq/A_1.fastq.gz": "r1", "fastq/A_2.fastq.gz": "r2"}


def test_direct_samplesheet_is_snapshotted_validated_and_traced(library, finished_run, tmp_path):
    _, down = _trees(library("mini_up", "mini"))
    up = finished_run(tmp_path / "up", {"samplesheet/samplesheet.csv": SHEET, **FASTQS})
    hand = handoff.materialize(_rule(DIRECT), upstream_outdir=up, downstream_tree=down,
                               dest=tmp_path / "h")
    snap = tmp_path / "h" / "input.csv"
    assert hand.params == {"input": str(snap)}
    assert _rows(snap)[0]["fastq_1"] == f"{up}/fastq/A_1.fastq.gz"
    item = hand.record["params"]["input"]
    assert item["kind"] == "samplesheet" and item["sha256"] == handoff.sha256_file(snap)
    # every upstream file the snapshot points into is traced to the upstream's own output digest
    assert set(item["derived_from"]) == {"samplesheet/samplesheet.csv", *FASTQS}
    assert all(d and len(d) == 64 for d in item["derived_from"].values())
    assert hand.record["rule"]["body"] == DIRECT
    assert hand.record["upstream_params"] == {"nf_core_pipeline": "mini"}


def test_rename_set_and_relative_paths(library, finished_run, tmp_path):
    _, down = _trees(library("mini_up", "mini"))
    up = finished_run(tmp_path / "up", {
        "s.csv": "sample,reads_1,run_accession\nA,fastq/A_1.fastq.gz,SRR1\n", **FASTQS})
    rule = _rule({"params": {"input": {"samplesheet": "s.csv", "provides": ["sample", "reads_1"],
                                       "rename": {"reads_1": "fastq_1"},
                                       "set": {"lane": "{run_accession}"}}}})
    handoff.materialize(rule, upstream_outdir=up, downstream_tree=down, dest=tmp_path / "h")
    row = _rows(tmp_path / "h" / "input.csv")[0]
    assert row["fastq_1"] == f"{up}/fastq/A_1.fastq.gz"          # relative → absolute
    assert row["lane"] == "SRR1" and "reads_1" not in row


def test_a_rename_onto_an_existing_column_is_refused(library, finished_run, tmp_path):
    _, down = _trees(library("mini_up", "mini"))
    up = finished_run(tmp_path / "up", {"s.csv": "sample,fastq_1,r1\nA,x,y\n"})
    rule = _rule({"params": {"input": {"samplesheet": "s.csv", "provides": ["sample", "r1"],
                                       "rename": {"r1": "fastq_1"}}}})
    with pytest.raises(NfclawError, match="already has column fastq_1"):
        handoff.materialize(rule, upstream_outdir=up, downstream_tree=down, dest=tmp_path / "h")


def test_build_maps_output_files_into_rows(library, finished_run, tmp_path):
    _, down = _trees(library("mini_up", "mini"))
    up = finished_run(tmp_path / "up", {"reads/B_1.fq.gz": "b1", "reads/A_1.fq.gz": "a1",
                                        "reads/A_2.fq.gz": "a2"})
    rule = _rule({"params": {"input": {"build": {
        "rows": "reads/{sample}_1.fq.gz",
        "columns": {"sample": "{sample}", "fastq_1": "reads/{sample}_1.fq.gz",
                    "fastq_2": "reads/{sample}_2.fq.gz?"}}}}})
    hand = handoff.materialize(rule, upstream_outdir=up, downstream_tree=down, dest=tmp_path / "h")
    rows = _rows(tmp_path / "h" / "input.csv")
    assert [r["sample"] for r in rows] == ["A", "B"]                # sorted by path
    assert rows[0]["fastq_2"] == f"{up}/reads/A_2.fq.gz"
    assert rows[1]["fastq_2"] == ""                                 # optional and absent
    assert set(hand.record["params"]["input"]["derived_from"]) == {
        "reads/A_1.fq.gz", "reads/A_2.fq.gz", "reads/B_1.fq.gz"}


def test_build_with_no_matching_file_fails_the_handoff(library, finished_run, tmp_path):
    _, down = _trees(library("mini_up", "mini"))
    up = finished_run(tmp_path / "up", {"other/x.txt": "x"})
    rule = _rule({"params": {"input": {"build": {
        "rows": "reads/{sample}_1.fq.gz",
        "columns": {"sample": "{sample}", "fastq_1": "reads/{sample}_1.fq.gz"}}}}})
    with pytest.raises(NfclawError, match="no file in .* matches 'reads/{sample}_1.fq.gz'") as err:
        handoff.materialize(rule, upstream_outdir=up, downstream_tree=down, dest=tmp_path / "h")
    assert err.value.code is ErrorCode.HANDOFF_FAILED


@pytest.mark.parametrize("files, msg", [
    ({}, "nothing in"),
    ({"a/x.tsv": "1", "b/x.tsv": "2"}, "2 files match"),
])
def test_file_source_needs_exactly_one_match(library, finished_run, tmp_path, files, msg):
    _, down = _trees(library("mini_up", "mini"))
    up = finished_run(tmp_path / "up", files)
    rule = _rule({"params": {"fasta": {"file": "*/x.tsv"}}})
    with pytest.raises(NfclawError, match=msg) as err:
        handoff.materialize(rule, upstream_outdir=up, downstream_tree=down, dest=tmp_path / "h")
    assert err.value.code is ErrorCode.HANDOFF_FAILED


def test_file_source_ignores_the_provenance_bundle(library, finished_run, tmp_path):
    # outputs.sha256 lives in provenance/, which is not a result: a glob must never pick it.
    _, down = _trees(library("mini_up", "mini"))
    up = finished_run(tmp_path / "up", {"counts/outputs.sha256": "x"})
    hand = handoff.materialize(_rule({"params": {"fasta": {"file": "*/outputs.sha256"}}}),
                               upstream_outdir=up, downstream_tree=down, dest=tmp_path / "h")
    assert hand.params == {"fasta": str(up / "counts" / "outputs.sha256")}
    assert list(hand.record["params"]["fasta"]["derived_from"]) == ["counts/outputs.sha256"]


def test_upstream_param_and_optional(library, finished_run, tmp_path):
    _, down = _trees(library("mini_up", "mini"))
    up = finished_run(tmp_path / "up", {}, params={"gtf": "/refs/genes.gtf"})
    rule = _rule({"params": {"fasta": {"upstream_param": "gtf"},
                             "aligner": {"upstream_param": "never_set", "optional": True}}})
    hand = handoff.materialize(rule, upstream_outdir=up, downstream_tree=down, dest=tmp_path / "h")
    assert hand.params == {"fasta": "/refs/genes.gtf"}
    assert "aligner" not in hand.record["params"]


def test_a_missing_upstream_param_fails_unless_optional(library, finished_run, tmp_path):
    _, down = _trees(library("mini_up", "mini"))
    up = finished_run(tmp_path / "up", {})
    with pytest.raises(NfclawError, match="the mini_up run did not set --gtf"):
        handoff.materialize(_rule({"params": {"fasta": {"upstream_param": "gtf"}}}),
                            upstream_outdir=up, downstream_tree=down, dest=tmp_path / "h")


def test_a_sheet_the_downstream_would_reject_fails_the_handoff(library, finished_run, tmp_path):
    _, down = _trees(library("mini_up", "mini"))
    up = finished_run(tmp_path / "up", {"samplesheet/samplesheet.csv":
                                        "sample,fastq_1,fastq_2\nA,{outdir}/missing.fq.gz,\n"})
    with pytest.raises(NfclawError, match="file not found for 'fastq_1'") as err:
        handoff.materialize(_rule(DIRECT), upstream_outdir=up, downstream_tree=down,
                            dest=tmp_path / "h")
    assert err.value.code is ErrorCode.HANDOFF_FAILED
    assert err.value.details["snapshot"].endswith("input.csv")


def test_a_set_template_naming_an_absent_column_fails_clearly(library, finished_run, tmp_path):
    _, down = _trees(library("mini_up", "mini"))
    up = finished_run(tmp_path / "up", {"samplesheet/samplesheet.csv": SHEET, **FASTQS})
    rule = _rule({"params": {"input": {"samplesheet": "samplesheet/samplesheet.csv",
                                       "provides": ["sample", "fastq_1"],
                                       "set": {"lane": "{lane_id}"}}}})
    with pytest.raises(NfclawError, match="needs column 'lane_id'"):
        handoff.materialize(rule, upstream_outdir=up, downstream_tree=down, dest=tmp_path / "h")


def test_lineage_follows_absolute_paths_in_any_column(library, finished_run, tmp_path):
    # atacseq declares no path format for fastq_1; the files it names are still traced.
    _, down = _trees(library("mini_up", "mini"))
    up = finished_run(tmp_path / "up", {
        "s.csv": "sample,fastq_1,notes\nA,{outdir}/fastq/A_1.fastq.gz,{outdir}/fastq/A_2.fastq.gz\n",
        **FASTQS})
    rule = _rule({"params": {"input": {"samplesheet": "s.csv",
                                       "provides": ["sample", "fastq_1"]}}})
    hand = handoff.materialize(rule, upstream_outdir=up, downstream_tree=down, dest=tmp_path / "h")
    assert set(hand.record["params"]["input"]["derived_from"]) == {"s.csv", *FASTQS}
