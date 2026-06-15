from runner.errors import ErrorCode, NfclawError


def test_error_renders_code_and_fix():
    e = NfclawError(ErrorCode.PIPELINE_NOT_FOUND, "nope", fix="run nfclaw list")
    s = str(e)
    assert "pipeline_not_found" in s
    assert "run nfclaw list" in s


def test_error_without_fix():
    e = NfclawError(ErrorCode.ENVIRONMENT, "bad env")
    assert str(e) == "[environment] bad env"


def test_error_renders_detail_issues():
    # The actionable info (which checks failed) lives in details; it must reach the user.
    e = NfclawError(ErrorCode.ENVIRONMENT, "Preflight checks failed.",
                    details={"issues": ["docker not found on PATH", "--outdir is not empty"]})
    s = str(e)
    assert "environment" in s
    assert "docker not found on PATH" in s
    assert "--outdir is not empty" in s
