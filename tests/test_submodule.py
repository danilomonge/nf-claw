from runner import submodule


def test_uninitialized_when_empty(tmp_path):
    (tmp_path / "sarek" / "upstream").mkdir(parents=True)
    st = submodule.resolve("sarek", tmp_path)
    assert st.initialized is False
    assert st.complete is False


def test_complete_when_required_files_present(tmp_path):
    up = tmp_path / "sarek" / "upstream"
    up.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config", "nextflow_schema.json"):
        (up / f).write_text("x")
    st = submodule.resolve("sarek", tmp_path)
    assert st.initialized is True
    assert st.complete is True
    assert st.missing_files == ()


def test_resolve_at_uses_explicit_path(tmp_path):
    # resolve_at points at an arbitrary tree (e.g. a version worktree), not pipelines/<name>/upstream.
    tree = tmp_path / ".versions" / "1.2.0" / "upstream"
    tree.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config", "nextflow_schema.json"):
        (tree / f).write_text("x")
    st = submodule.resolve_at("sarek", tree)
    assert st.path == tree
    assert st.complete is True


def test_incomplete_when_files_missing(tmp_path):
    up = tmp_path / "sarek" / "upstream"
    up.mkdir(parents=True)
    (up / "main.nf").write_text("x")  # missing nextflow.config + schema
    st = submodule.resolve("sarek", tmp_path)
    assert st.initialized is True
    assert st.complete is False
    assert "nextflow.config" in st.missing_files
