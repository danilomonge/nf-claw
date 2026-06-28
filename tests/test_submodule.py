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


def test_ensure_initialized_serializes_parallel_init(tmp_path, monkeypatch):
    # Several processes/threads initialising the same submodule at once must not race on
    # .git/config: the lock + re-check means `git submodule update` runs exactly once.
    import threading
    import types
    up = tmp_path / "pipelines" / "mini" / "upstream"
    up.mkdir(parents=True)                                        # exists but empty → not initialised
    calls = []

    def fake_run(args, **kw):
        if "submodule" in args:                                  # the init call (not the _git reads)
            calls.append(args)
            for f in submodule.REQUIRED_FILES:
                (up / f).write_text("x")                         # simulate a successful init
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(submodule.subprocess, "run", fake_run)
    errors = []

    def worker():
        try:
            submodule.ensure_initialized("mini", tmp_path / "pipelines", tmp_path)
        except Exception as exc:                                 # noqa: BLE001 — record any failure
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert not errors
    assert len(calls) == 1                                       # ran once under the lock + re-check


def test_resolve_at_uses_explicit_path(tmp_path):
    # resolve_at points at an arbitrary tree (e.g. a version worktree), not pipelines/<name>/upstream.
    tree = tmp_path / ".versions" / "1.2.0" / "upstream"
    tree.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config", "nextflow_schema.json"):
        (tree / f).write_text("x")
    st = submodule.resolve_at("sarek", tree)
    assert st.path == tree
    assert st.complete is True


def test_resolve_uses_committed_skill_version_when_shallow_tags_are_absent(tmp_path, monkeypatch):
    # A shallow submodule may not have release tags locally, making `git describe --tags --always`
    # return a short hash. If the committed skill.md matches the exact commit, the pinned release
    # version in that file is the offline source of truth.
    up = tmp_path / "sarek" / "upstream"
    up.mkdir(parents=True)
    for f in submodule.REQUIRED_FILES:
        (up / f).write_text("x")
    (tmp_path / "sarek" / "skill.md").write_text(
        "---\nversion: 2.1.0\ncommit: abcdef1234567890\n---\n")

    def fake_git(path, *args):
        if args == ("rev-parse", "HEAD"):
            return "abcdef1234567890"
        if args == ("describe", "--tags", "--always"):
            return "abcdef1"
        return ""

    monkeypatch.setattr(submodule, "_git", fake_git)
    st = submodule.resolve("sarek", tmp_path)
    assert st.version == "2.1.0"


def test_resolve_keeps_git_tag_when_available_even_if_skill_is_stale(tmp_path, monkeypatch):
    up = tmp_path / "sarek" / "upstream"
    up.mkdir(parents=True)
    for f in submodule.REQUIRED_FILES:
        (up / f).write_text("x")
    (tmp_path / "sarek" / "skill.md").write_text(
        "---\nversion: abcdef1\ncommit: abcdef1234567890\n---\n")

    def fake_git(path, *args):
        if args == ("rev-parse", "HEAD"):
            return "abcdef1234567890"
        if args == ("describe", "--tags", "--always"):
            return "2.1.0"
        return ""

    monkeypatch.setattr(submodule, "_git", fake_git)
    assert submodule.resolve("sarek", tmp_path).version == "2.1.0"


def test_incomplete_when_files_missing(tmp_path):
    up = tmp_path / "sarek" / "upstream"
    up.mkdir(parents=True)
    (up / "main.nf").write_text("x")  # missing nextflow.config + schema
    st = submodule.resolve("sarek", tmp_path)
    assert st.initialized is True
    assert st.complete is False
    assert "nextflow.config" in st.missing_files
