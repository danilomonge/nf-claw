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
