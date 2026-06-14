import json
from pathlib import Path

from runner import schema, parameters

FIX = Path(__file__).parent / "fixtures"


def test_typo_warning_for_unknown_param():
    ps = schema.load_param_schema(FIX / "mini")
    warns = parameters.typo_warnings({"alnger": "star"}, ps)
    assert warns and "alnger" in warns[0]


def test_known_param_no_warning():
    ps = schema.load_param_schema(FIX / "mini")
    assert parameters.typo_warnings({"aligner": "star"}, ps) == []


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
