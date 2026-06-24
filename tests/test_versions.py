import subprocess

import pytest

from runner import versions
from runner.errors import ErrorCode, NfclawError


@pytest.fixture(autouse=True)
def _make_tmp_removable(tmp_path):
    """Git pack objects under a worktree are written read-only. Make the whole tree
    writable on teardown so pytest's tmp-retention cleanup never trips over them and
    floods later runs with `rm_rf` warnings."""
    yield
    for p in sorted(tmp_path.rglob("*"), reverse=True):
        try:
            p.chmod(0o700)
        except OSError:
            pass


# --- _url_for: read the submodule URL straight from .gitmodules (offline, no git) ---
def test_url_for_reads_gitmodules(tmp_path):
    (tmp_path / ".gitmodules").write_text(
        '[submodule "pipelines/sarek/upstream"]\n'
        "\tpath = pipelines/sarek/upstream\n"
        "\turl = https://github.com/nf-core/sarek.git\n"
        '[submodule "pipelines/rnaseq/upstream"]\n'
        "\tpath = pipelines/rnaseq/upstream\n"
        "\turl = https://github.com/nf-core/rnaseq.git\n")
    assert versions._url_for("rnaseq", tmp_path) == "https://github.com/nf-core/rnaseq.git"
    assert versions._url_for("sarek", tmp_path) == "https://github.com/nf-core/sarek.git"


def test_url_for_none_when_absent(tmp_path):
    assert versions._url_for("nope", tmp_path) is None          # no .gitmodules at all
    (tmp_path / ".gitmodules").write_text(
        '[submodule "pipelines/sarek/upstream"]\n\turl = x\n')
    assert versions._url_for("rnaseq", tmp_path) is None        # name not present


# --- release_tags: semver only, newest first, union of remote + local, deduped ---
def test_release_tags_semver_only_newest_first(tmp_path, monkeypatch):
    monkeypatch.setattr(versions, "_url_for", lambda *a, **k: "url")
    monkeypatch.setattr(versions, "remote_tags",
                        lambda url: ["1.2.0", "2.0.0", "dev", "2.0.0-rc1", "v1.10.0"])
    monkeypatch.setattr(versions, "_local_tags", lambda up: ["1.1.0"])
    assert versions.release_tags("p", pipelines_dir=tmp_path, repo_root=tmp_path) == [
        "2.0.0", "v1.10.0", "1.2.0", "1.1.0"]


def test_release_tags_offline_falls_back_to_local(tmp_path, monkeypatch):
    monkeypatch.setattr(versions, "_url_for", lambda *a, **k: "url")
    monkeypatch.setattr(versions, "remote_tags", lambda url: [])   # network down
    monkeypatch.setattr(versions, "_local_tags", lambda up: ["1.0.0", "1.1.0"])
    assert versions.release_tags("p", pipelines_dir=tmp_path, repo_root=tmp_path) == [
        "1.1.0", "1.0.0"]


# --- _match_tag: tolerate the optional leading 'v' on either side ---
def test_match_tag_normalizes_v_prefix():
    assert versions._match_tag("2.0.0", ["2.0.0", "1.0.0"]) == "2.0.0"
    assert versions._match_tag("v2.0.0", ["2.0.0"]) == "2.0.0"
    assert versions._match_tag("2.0.0", ["v2.0.0"]) == "v2.0.0"
    assert versions._match_tag("9.9.9", ["2.0.0"]) is None


# --- resolve: validate against real tags; raise VERSION_NOT_FOUND with the list ---
def test_resolve_returns_canonical_tag(tmp_path, monkeypatch):
    monkeypatch.setattr(versions, "release_tags", lambda *a, **k: ["2.0.0", "1.2.0"])
    assert versions.resolve("p", "v1.2.0", pipelines_dir=tmp_path, repo_root=tmp_path) == "1.2.0"


def test_resolve_unknown_version_raises_with_available(tmp_path, monkeypatch):
    monkeypatch.setattr(versions, "release_tags", lambda *a, **k: ["2.0.0", "1.2.0"])
    with pytest.raises(NfclawError) as exc:
        versions.resolve("p", "9.9.9", pipelines_dir=tmp_path, repo_root=tmp_path)
    assert exc.value.code == ErrorCode.VERSION_NOT_FOUND
    assert exc.value.details["available"] == ["2.0.0", "1.2.0"]


# --- ensure: the orchestrator that downstream code consumes ---
def test_ensure_none_uses_pinned_submodule(tmp_path, monkeypatch):
    sentinel = object()
    monkeypatch.setattr(versions.submod, "ensure_initialized",
                        lambda name, pdir, root: sentinel)
    assert versions.ensure("p", None, pipelines_dir=tmp_path, repo_root=tmp_path) is sentinel


def test_ensure_requested_equals_pin_skips_cache(tmp_path, monkeypatch):
    from runner.submodule import SubmoduleStatus
    pin = SubmoduleStatus("p", tmp_path / "up", True, True, "2.0.0", "abc", ())
    monkeypatch.setattr(versions.submod, "ensure_initialized", lambda *a, **k: pin)
    monkeypatch.setattr(versions, "resolve", lambda *a, **k: "2.0.0")
    materialized = {}
    monkeypatch.setattr(versions, "materialize",
                        lambda *a, **k: materialized.setdefault("called", True))
    assert versions.ensure("p", "v2.0.0", pipelines_dir=tmp_path, repo_root=tmp_path) is pin
    assert "called" not in materialized                         # no needless worktree


def test_ensure_other_version_materializes(tmp_path, monkeypatch):
    from runner.submodule import SubmoduleStatus
    pin = SubmoduleStatus("p", tmp_path / "up", True, True, "2.0.0", "abc", ())
    cached = SubmoduleStatus("p", tmp_path / "cache", True, True, "1.2.0", "def", ())
    monkeypatch.setattr(versions.submod, "ensure_initialized", lambda *a, **k: pin)
    monkeypatch.setattr(versions, "resolve", lambda *a, **k: "1.2.0")
    monkeypatch.setattr(versions, "materialize", lambda name, tag, **k: cached)
    assert versions.ensure("p", "1.2.0", pipelines_dir=tmp_path, repo_root=tmp_path) is cached


# --- available: every release tag, the committed pin flagged ---
def test_available_flags_the_pin(tmp_path, monkeypatch):
    d = tmp_path / "pipelines" / "p"
    (d / "upstream").mkdir(parents=True)
    d.joinpath("skill.md").write_text("---\nname: p\nversion: 2.0.0\n---\n# p\n")
    monkeypatch.setattr(versions, "release_tags", lambda *a, **k: ["2.0.0", "1.2.0"])
    assert versions.available("p", pipelines_dir=tmp_path / "pipelines", repo_root=tmp_path) == [
        ("2.0.0", True), ("1.2.0", False)]


# --- materialize: a real git worktree pinned to the tag (the robustness core) ---
def _git(path, *args, **kw):
    subprocess.run(["git", "-C", str(path), *args], check=True,
                   capture_output=True, text=True, **kw)


def _upstream_repo_with_tag(pipelines_dir, name, tag):
    up = pipelines_dir / name / "upstream"
    up.mkdir(parents=True)
    (up / "main.nf").write_text("workflow {}\n")
    (up / "nextflow.config").write_text("manifest {}\n")
    (up / "nextflow_schema.json").write_text("{}\n")
    _git(up, "init", "-q", "-b", "main")
    _git(up, "-c", "user.email=t@t", "-c", "user.name=t", "add", ".")
    _git(up, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "init")
    _git(up, "tag", tag)
    return up


def test_materialize_checks_out_tag_into_cache(tmp_path):
    pdir = tmp_path / "pipelines"
    _upstream_repo_with_tag(pdir, "p", "1.2.0")
    st = versions.materialize("p", "1.2.0", pipelines_dir=pdir, repo_root=tmp_path)
    assert st.version == "1.2.0"
    assert st.complete is True
    assert st.path == pdir / "p" / versions.CACHE_DIRNAME / "1.2.0" / "upstream"
    assert (st.path / "main.nf").read_text() == "workflow {}\n"
    assert versions.is_cached(st) is True


def test_materialize_is_idempotent(tmp_path):
    pdir = tmp_path / "pipelines"
    _upstream_repo_with_tag(pdir, "p", "1.2.0")
    first = versions.materialize("p", "1.2.0", pipelines_dir=pdir, repo_root=tmp_path)
    second = versions.materialize("p", "1.2.0", pipelines_dir=pdir, repo_root=tmp_path)
    assert first.path == second.path and second.complete is True


# --- generate_docs: reuse the librarian renderer for an arbitrary version's tree ---
def test_generate_docs_writes_version_markdowns(tmp_path):
    import shutil
    from pathlib import Path
    from runner.submodule import SubmoduleStatus
    fix = Path(__file__).parent / "fixtures" / "mini"
    dest = tmp_path / ".versions" / "1.2.0" / "upstream"
    dest.mkdir(parents=True)
    for f in ("main.nf", "nextflow.config"):
        (dest / f).write_text("x")
    shutil.copy(fix / "nextflow_schema.json", dest / "nextflow_schema.json")
    st = SubmoduleStatus("mini", dest, True, True, "1.2.0", "abc123", ())
    skill_path, ref_path = versions.generate_docs(st, dest_dir=dest.parent)
    assert skill_path == dest.parent / "skill.md"
    assert "# mini" in skill_path.read_text()
    assert "version: 1.2.0" in skill_path.read_text()
    assert "mini" in ref_path.read_text()
