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
