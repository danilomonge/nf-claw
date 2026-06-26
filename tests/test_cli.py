from pathlib import Path

from runner import cli


def _seed(tmp_path):
    for name in ("rnaseq", "sarek"):
        d = tmp_path / "pipelines" / name
        (d / "upstream").mkdir(parents=True)
        d.joinpath("skill.md").write_text(f"---\nname: {name}\nversion: 1.0.0\n---\n# {name}\n")
    return tmp_path


def test_list_prints_pipelines(tmp_path, monkeypatch, capsys):
    root = _seed(tmp_path)
    monkeypatch.setattr(cli, "_repo_root", lambda: root)
    assert cli.main(["list"]) == 0
    out = capsys.readouterr().out
    assert "rnaseq" in out and "sarek" in out


def test_show_prints_skill(tmp_path, monkeypatch, capsys):
    root = _seed(tmp_path)
    monkeypatch.setattr(cli, "_repo_root", lambda: root)
    assert cli.main(["show", "sarek"]) == 0
    assert "# sarek" in capsys.readouterr().out


def test_collect_overrides_parses_flags():
    ov = cli._collect_overrides(["--tools", "strelka", "--wes"])
    assert ov == {"tools": "strelka", "wes": True}


def test_collect_overrides_handles_equals_form():
    # `--key=value` is a universal CLI convention agents will use.
    assert cli._collect_overrides(["--genome=GRCh38"]) == {"genome": "GRCh38"}
    ov = cli._collect_overrides(["--tools=strelka,mutect2", "--wes", "--step", "mapping"])
    assert ov == {"tools": "strelka,mutect2", "wes": True, "step": "mapping"}


def test_run_prints_command_and_outputs_summary(tmp_path, monkeypatch, capsys):
    from runner import orchestration
    from runner.outputs import OutputsReport
    rep = OutputsReport(pipeline_info=None, multiqc_report=Path("/o/multiqc_report.html"),
                        files=("a.txt", "b.txt"))
    monkeypatch.setattr(orchestration, "run_pipeline",
                        lambda *a, **k: orchestration.RunResult("CMD", Path("/o"), False, rep))
    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)
    assert cli.main(["run", "x", "--outdir", str(tmp_path / "out")]) == 0
    out = capsys.readouterr().out
    assert "CMD" in out and "2 files" in out and "multiqc" in out


def test_versions_command_lists_tags_and_marks_pin(tmp_path, monkeypatch, capsys):
    from runner import versions
    root = _seed(tmp_path)
    monkeypatch.setattr(cli, "_repo_root", lambda: root)
    monkeypatch.setattr(versions, "available",
                        lambda name, **k: [("2.0.0", True), ("1.2.0", False)])
    assert cli.main(["versions", "sarek"]) == 0
    out = capsys.readouterr().out
    assert "2.0.0" in out and "latest" in out and "1.2.0" in out


def test_run_threads_pipeline_version(tmp_path, monkeypatch, capsys):
    from runner import orchestration
    captured = {}

    def fake_run(*a, **k):
        captured.update(k)
        return orchestration.RunResult("CMD", Path("/o"), True, None)

    monkeypatch.setattr(orchestration, "run_pipeline", fake_run)
    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)
    assert cli.main(["run", "x", "--outdir", str(tmp_path / "out"),
                     "--pipeline-version", "1.2.0"]) == 0
    assert captured["pipeline_version"] == "1.2.0"


def test_show_pipeline_version_prints_generated_docs(tmp_path, monkeypatch, capsys):
    from runner import versions
    from runner.submodule import SubmoduleStatus
    root = _seed(tmp_path)
    monkeypatch.setattr(cli, "_repo_root", lambda: root)
    cached = root / "pipelines" / "sarek" / ".versions" / "1.2.0" / "upstream"
    st = SubmoduleStatus("sarek", cached, True, True, "1.2.0", "abc", ())
    monkeypatch.setattr(versions, "ensure", lambda *a, **k: st)

    def fake_generate(status, *, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "skill.md").write_text("# sarek @ 1.2.0\n")
        return dest_dir / "skill.md", dest_dir / "reference.md"

    monkeypatch.setattr(versions, "generate_docs", fake_generate)
    assert cli.main(["show", "sarek", "--pipeline-version", "1.2.0"]) == 0
    assert "# sarek @ 1.2.0" in capsys.readouterr().out


def test_show_unknown_pipeline_with_version_errors_cleanly(tmp_path, monkeypatch, capsys):
    # An unknown pipeline must 404 cleanly (return 1), never attempt git work on a bad path.
    root = _seed(tmp_path)
    monkeypatch.setattr(cli, "_repo_root", lambda: root)
    assert cli.main(["show", "nope", "--pipeline-version", "1.0.0"]) == 1
    assert "pipeline_not_found" in capsys.readouterr().err


def test_versions_empty_reports_none_found(tmp_path, monkeypatch, capsys):
    from runner import versions
    root = _seed(tmp_path)
    monkeypatch.setattr(cli, "_repo_root", lambda: root)
    monkeypatch.setattr(versions, "available", lambda name, **k: [])
    assert cli.main(["versions", "sarek"]) == 0
    assert "no release" in capsys.readouterr().err.lower()


def test_run_threads_nxf_ver_and_env(tmp_path, monkeypatch):
    from runner import orchestration
    captured = {}

    def fake_run(*a, **k):
        captured.update(k)
        return orchestration.RunResult("CMD", Path("/o"), True, None)

    monkeypatch.setattr(orchestration, "run_pipeline", fake_run)
    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)
    rc = cli.main(["run", "x", "--outdir", str(tmp_path / "out"),
                   "--nxf-ver", "25.10.2",
                   "--nxf-env", "NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true",
                   "--nxf-env", "NXF_OFFLINE=true"])
    assert rc == 0
    assert captured["nxf_ver"] == "25.10.2"
    assert captured["nxf_env"] == {"NXF_JVM_ARGS": "-Djava.net.preferIPv6Addresses=true",
                                   "NXF_OFFLINE": "true"}


def test_run_rejects_non_nxf_env_var(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)
    rc = cli.main(["run", "x", "--outdir", str(tmp_path / "out"), "--nxf-env", "FOO=bar"])
    assert rc == 1
    assert "NXF_" in capsys.readouterr().err


def test_run_threads_config(tmp_path, monkeypatch):
    from runner import orchestration
    captured = {}
    monkeypatch.setattr(orchestration, "run_pipeline",
                        lambda *a, **k: captured.update(k) or orchestration.RunResult(
                            "CMD", Path("/o"), True, None))
    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)
    cfg = tmp_path / "host.config"
    cfg.write_text("docker { runOptions = '--network host' }\n")
    assert cli.main(["run", "x", "--outdir", str(tmp_path / "out"),
                     "-c", str(cfg), "--config", str(cfg)]) == 0
    assert captured["configs"] == [str(cfg), str(cfg)]            # repeatable, threaded through


def test_run_threads_allow_spaces(tmp_path, monkeypatch):
    from runner import orchestration
    captured = {}
    monkeypatch.setattr(orchestration, "run_pipeline",
                        lambda *a, **k: captured.update(k) or orchestration.RunResult(
                            "CMD", Path("/o"), True, None))
    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)
    assert cli.main(["run", "x", "--outdir", str(tmp_path / "out"), "--allow-spaces"]) == 0
    assert captured["allow_spaces"] is True
    captured.clear()
    assert cli.main(["run", "x", "--outdir", str(tmp_path / "out")]) == 0
    assert captured["allow_spaces"] is False                  # default off


def test_run_rejects_malformed_nxf_env(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)
    rc = cli.main(["run", "x", "--outdir", str(tmp_path / "out"), "--nxf-env", "NXF_VER"])
    assert rc == 1
    assert "KEY=VALUE" in capsys.readouterr().err


def test_run_surfaces_engine_warning_on_stderr(tmp_path, monkeypatch, capsys):
    from runner import orchestration
    monkeypatch.setattr(orchestration, "run_pipeline",
                        lambda *a, **k: orchestration.RunResult(
                            "CMD", Path("/o"), True, None, warnings=["engine too old"]))
    monkeypatch.setattr(cli, "_repo_root", lambda: tmp_path)
    assert cli.main(["run", "x", "--outdir", str(tmp_path / "out")]) == 0
    cap = capsys.readouterr()
    assert "CMD" in cap.out                                    # command still on stdout
    assert "warning: engine too old" in cap.err               # advisory on stderr
