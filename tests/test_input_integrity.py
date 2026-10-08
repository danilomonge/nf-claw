"""Malformed input maps and ambiguous or non-finite tabular values fail clearly."""
import pytest

from runner import parameters, samplesheet
from runner.errors import NfclawError
from runner.schema import Column, InputSchema, ParamSchema


@pytest.mark.parametrize("text", ["false", "0", "[]", "null"])
def test_falsy_yaml_scalar_or_sequence_is_not_an_empty_parameter_map(tmp_path, text):
    path = tmp_path / "params.yaml"
    path.write_text(text)
    with pytest.raises(NfclawError, match="object"):
        parameters.load_params_file(path)


def test_yaml_parameter_names_must_be_strings(tmp_path):
    path = tmp_path / "params.yaml"
    path.write_text("42: star\n")
    with pytest.raises(NfclawError, match="name"):
        parameters.load_params_file(path)


def test_direct_parameter_validation_rejects_nonstring_names():
    schema = ParamSchema("t", "", {})
    assert parameters.validate_params({42: "star"}, schema)


def test_non_json_yaml_values_are_reported_before_writing_params(tmp_path):
    path = tmp_path / "params.yaml"
    path.write_text("object: !!set {1: null, 2: null}\n")
    values = parameters.load_params_file(path)
    with pytest.raises(NfclawError, match="JSON"):
        parameters.write_params_file(values, tmp_path / "out" / "params.json")


@pytest.mark.parametrize("value", ["nan", "NaN", "inf", "-Infinity"])
def test_non_finite_samplesheet_numbers_are_rejected(tmp_path, value):
    sheet = tmp_path / "samples.csv"
    sheet.write_text(f"sample,percent_mapped\nA,{value}\n")
    schema = InputSchema(columns=(Column("sample", "string", True, None),
                                  Column("percent_mapped", "number", False, None)))
    assert any("finite" in issue for issue in samplesheet.validate(sheet, schema))


def test_duplicate_samplesheet_headers_are_ambiguous(tmp_path):
    sheet = tmp_path / "samples.csv"
    sheet.write_text("sample,sample\nA,B\n")
    schema = InputSchema(columns=(Column("sample", "string", True, None),))
    assert any("duplicate" in issue for issue in samplesheet.validate(sheet, schema))


def test_samplesheet_values_beyond_the_header_are_reported(tmp_path):
    sheet = tmp_path / "samples.csv"
    sheet.write_text("sample\nA,unexpected\n")
    schema = InputSchema(columns=(Column("sample", "string", True, None),))
    assert any("extra" in issue for issue in samplesheet.validate(sheet, schema))
