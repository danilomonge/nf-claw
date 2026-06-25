import json
from pathlib import Path

from runner import schema, parameters

FIX = Path(__file__).parent / "fixtures"


def test_validate_params_flags_unknown():
    ps = schema.load_param_schema(FIX / "mini")
    errs = parameters.validate_params({"alnger": "star"}, ps)   # typo'd flag
    assert errs and "alnger" in errs[0] and "unknown" in errs[0]


def test_validate_params_accepts_known_and_valid_enum():
    ps = schema.load_param_schema(FIX / "mini")
    assert parameters.validate_params({"aligner": "star"}, ps) == []   # star is in the enum


def test_validate_params_flags_value_outside_enum():
    ps = schema.load_param_schema(FIX / "mini")
    errs = parameters.validate_params({"aligner": "bowtie"}, ps)   # not in (star, hisat2)
    assert errs and "must be one of" in errs[0] and "star" in errs[0]


def test_validate_params_boolean_enum_uses_json_literals(tmp_path):
    import json
    (tmp_path / "nextflow_schema.json").write_text(json.dumps(
        {"definitions": {"g": {"properties": {"flag": {"type": "boolean", "enum": [False]}}}}}))
    ps = schema.load_param_schema(tmp_path)
    assert parameters.validate_params({"flag": "false"}, ps) == []   # CLI string, schema-literal → ok
    assert parameters.validate_params({"flag": False}, ps) == []     # native bool from a params-file → ok
    assert parameters.validate_params({"flag": "False"}, ps)         # Python casing → rejected
    assert parameters.validate_params({"flag": "true"}, ps)          # not in enum → rejected


def _schema_with_types(tmp_path):
    (tmp_path / "nextflow_schema.json").write_text(json.dumps({"definitions": {"g": {"properties": {
        "skip_busco": {"type": "boolean"},
        "max_cpus": {"type": "integer"},
        "ratio": {"type": "number"},
        "genome": {"type": "string"},
        "flexible": {"type": ["integer", "string"]},
    }}}}))
    return schema.load_param_schema(tmp_path)


def test_coerce_to_schema_converts_cli_strings_by_declared_type(tmp_path):
    ps = _schema_with_types(tmp_path)
    out = parameters.coerce_to_schema(
        {"skip_busco": "true", "max_cpus": "4", "ratio": "0.5",
         "genome": "GRCh38", "flexible": "7", "unknown_flag": "x"}, ps)
    assert out["skip_busco"] is True
    assert out["max_cpus"] == 4 and isinstance(out["max_cpus"], int)
    assert out["ratio"] == 0.5 and isinstance(out["ratio"], float)
    assert out["genome"] == "GRCh38"          # string param → untouched
    assert out["flexible"] == "7"             # union type → ambiguous → left for nf-schema
    assert out["unknown_flag"] == "x"         # not in schema → left


def test_coerce_to_schema_is_case_insensitive_and_safe(tmp_path):
    ps = _schema_with_types(tmp_path)
    assert parameters.coerce_to_schema({"skip_busco": "FALSE"}, ps)["skip_busco"] is False
    assert parameters.coerce_to_schema({"skip_busco": True}, ps)["skip_busco"] is True   # bare flag untouched
    # unparseable values are left as-is so nf-schema reports a precise error
    assert parameters.coerce_to_schema({"max_cpus": "lots"}, ps)["max_cpus"] == "lots"
    assert parameters.coerce_to_schema({"skip_busco": "maybe"}, ps)["skip_busco"] == "maybe"


def test_merge_resolve_and_write(tmp_path):
    ps = schema.load_param_schema(FIX / "mini")
    merged = parameters.merge(cli_overrides={"aligner": "hisat2"}, params_file=None,
                              input_path=Path("rel/ss.csv"), outdir=tmp_path / "out")
    resolved = parameters.resolve_path_params(merged, ps)
    data = json.loads(parameters.write_params_file(resolved, tmp_path / "params.json").read_text())
    assert data["aligner"] == "hisat2"
    assert data["outdir"].endswith("/out")
    assert data["input"].startswith("/") and data["input"].endswith("rel/ss.csv")  # made absolute


def test_params_file_values_are_validated(tmp_path):
    # A typo or bad enum inside a --params-file must fail fast, exactly like a CLI flag.
    ps = schema.load_param_schema(FIX / "mini")
    pf = tmp_path / "p.json"
    pf.write_text('{"aligner": "bowtie", "alnger": "star"}')        # bad enum + typo'd key
    merged = parameters.merge(cli_overrides={}, params_file=pf, input_path=None, outdir=tmp_path / "o")
    errs = parameters.validate_params(merged, ps)
    assert any("bowtie" in e and "must be one of" in e for e in errs)   # enum caught
    assert any("alnger" in e and "unknown" in e for e in errs)         # typo caught
