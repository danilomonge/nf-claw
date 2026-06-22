from runner import engine_version as ev


def test_required_spec_reads_manifest(tmp_path):
    cfg = tmp_path / "nextflow.config"
    cfg.write_text("manifest {\n    nextflowVersion = '!>=25.04.3'\n}\n")
    assert ev.required_spec(cfg) == "!>=25.04.3"


def test_required_spec_none_when_absent(tmp_path):
    cfg = tmp_path / "nextflow.config"
    cfg.write_text("manifest { name = 'x' }\n")
    assert ev.required_spec(cfg) is None


def test_warning_silent_when_satisfied():
    assert ev.warning("!>=25.04.3", "  version 25.10.5 build 5935\n") is None


def test_warning_silent_when_equal():
    assert ev.warning(">=24.04.0", "version 24.04.0 build 1") is None


def test_warning_when_installed_too_old():
    w = ev.warning("!>=26.04.0", "version 25.10.4 build 5935")
    assert w is not None
    assert "26.04.0" in w and "25.10.4" in w


def test_warning_silent_on_unparseable_spec():
    # operators / ranges we don't model → never contradict Nextflow's own enforcement
    assert ev.warning("==24.04.0", "version 23.10.0 build 1") is None
    assert ev.warning(">=24.04.0 && <25", "version 23.10.0") is None


def test_warning_silent_when_installed_unknown():
    assert ev.warning(">=24.04.0", "no version here") is None
    assert ev.warning(">=24.04.0", None) is None
    assert ev.warning(None, "version 24.04.0") is None


def test_check_silent_without_manifest_constraint(tmp_path):
    (tmp_path / "nextflow.config").write_text("manifest { name = 'x' }\n")
    assert ev.check(tmp_path) == []


def test_check_warns_when_too_old(tmp_path, monkeypatch):
    (tmp_path / "nextflow.config").write_text("manifest { nextflowVersion = '!>=26.04.0' }\n")
    monkeypatch.setattr(ev, "_installed_raw", lambda: "version 25.10.4 build 1")
    out = ev.check(tmp_path)
    assert len(out) == 1 and "26.04.0" in out[0]
