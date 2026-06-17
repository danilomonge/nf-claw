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


def test_compose_merges_and_writes_json(tmp_path):
    ps = schema.load_param_schema(FIX / "mini")
    dest = tmp_path / "params.json"
    pf = parameters.compose(cli_overrides={"aligner": "hisat2"}, params_file=None,
                            schema=ps, outdir=tmp_path / "out",
                            input_path=Path("/data/ss.csv"), dest=dest)
    data = json.loads(pf.read_text())
    assert data["input"] == "/data/ss.csv"
    assert data["aligner"] == "hisat2"
    assert data["outdir"].endswith("/out")
