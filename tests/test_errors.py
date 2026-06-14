from runner.errors import ErrorCode, NfclawError


def test_error_renders_code_and_fix():
    e = NfclawError(ErrorCode.PIPELINE_NOT_FOUND, "nope", fix="run nfclaw list")
    s = str(e)
    assert "pipeline_not_found" in s
    assert "run nfclaw list" in s


def test_error_without_fix():
    e = NfclawError(ErrorCode.ENVIRONMENT, "bad env")
    assert str(e) == "[environment] bad env"
