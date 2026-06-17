from pathlib import Path

from runner import schema

FIX = Path(__file__).parent / "fixtures"


def test_loads_params_and_refs():
    ps = schema.load_param_schema(FIX / "mini")
    assert {"input", "outdir", "fasta", "aligner"} <= ps.known_params()
    assert ps.reference_path_params() == {"input", "outdir", "fasta"}
    assert ps.params["aligner"].enum == ("star", "hisat2")
    assert ps.params["aligner"].default == "star"


def test_groups_present():
    ps = schema.load_param_schema(FIX / "mini")
    assert "reference_genome_options" in ps.groups()


def test_input_schema_columns():
    insch = schema.load_input_schema(FIX / "mini")
    cols = {c.name: c for c in insch.columns}
    assert {"sample", "fastq_1", "fastq_2"} <= set(cols)
    assert cols["fastq_1"].fmt == "file-path" and cols["fastq_1"].is_path is True
    assert cols["sample"].fmt is None and cols["sample"].is_path is False
    assert cols["sample"].required is True


def test_no_input_schema_returns_none():
    assert schema.load_input_schema(FIX / "mini_no_input") is None


def test_anyof_type_unioned(tmp_path):
    import json
    s = {"definitions": {"g": {"properties": {
        "lane": {"anyOf": [{"type": "integer"}, {"type": "string"}], "description": "lane"},
        "plain": {"type": "string"},
    }}}}
    (tmp_path / "nextflow_schema.json").write_text(json.dumps(s))
    ps = schema.load_param_schema(tmp_path)
    assert ps.params["lane"].type == "integer or string"   # was bare "string" before
    assert ps.params["plain"].type == "string"


def test_type_array_is_unioned(tmp_path):
    import json
    s = {"definitions": {"g": {"properties": {
        "help": {"type": ["boolean", "string"], "description": "h"}}}}}
    (tmp_path / "nextflow_schema.json").write_text(json.dumps(s))
    ps = schema.load_param_schema(tmp_path)
    assert ps.params["help"].type == "boolean or string"   # was Python repr "['boolean', 'string']"


def test_boolean_enum_default_are_json_literals(tmp_path):
    import json
    s = {"definitions": {"g": {"properties": {
        "flag": {"type": "boolean", "enum": [False], "default": True}}}}}
    (tmp_path / "nextflow_schema.json").write_text(json.dumps(s))
    ps = schema.load_param_schema(tmp_path)
    assert ps.params["flag"].enum == ("false",)            # JSON literal, not Python "False"
    assert ps.params["flag"].default is True               # raw value kept; rendered later
    assert schema.json_scalar(True) == "true" and schema.json_scalar(False) == "false"
    assert schema.json_scalar(0) == "0" and schema.json_scalar("x") == "x"   # non-bools via str()
