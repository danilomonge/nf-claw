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
