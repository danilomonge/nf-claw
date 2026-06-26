from runner import outputs


def test_collect_finds_pipeline_info_and_multiqc(tmp_path):
    (tmp_path / "pipeline_info").mkdir()
    (tmp_path / "pipeline_info" / "software_versions.yml").write_text("x")
    mqc = tmp_path / "multiqc"; mqc.mkdir()
    (mqc / "multiqc_report.html").write_text("<html>")
    rep = outputs.collect(tmp_path)
    assert rep.pipeline_info is not None
    assert rep.multiqc_report is not None
    assert "pipeline_info/software_versions.yml" in rep.files


def test_collect_excludes_nextflow_internals(tmp_path):
    # When Nextflow launches from the outdir, .nextflow/ and .nextflow.log* land there — they are
    # engine internals, never pipeline results.
    (tmp_path / ".nextflow" / "cache").mkdir(parents=True)
    (tmp_path / ".nextflow" / "cache" / "db").write_text("x")
    (tmp_path / ".nextflow.log").write_text("log")
    (tmp_path / ".nextflow.log.1").write_text("log")
    (tmp_path / "result.txt").write_text("r")
    rep = outputs.collect(tmp_path)
    assert "result.txt" in rep.files
    assert not any(".nextflow" in f for f in rep.files)
