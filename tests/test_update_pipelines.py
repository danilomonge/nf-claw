from librarian import update_pipelines as up


def test_select_latest_ignores_prereleases():
    tags = ["v1.0.0", "1.2.0", "v1.10.0", "2.0.0-rc1", "nightly"]
    assert up.select_latest(tags) == "v1.10.0"


def test_select_latest_none_when_no_semver():
    assert up.select_latest(["dev", "main"]) is None


def test_relative_sources_resolved_against_repo_root(monkeypatch, tmp_path):
    # A relative --sources must resolve against --repo-root, not the CWD, so the source list and
    # `bump` (which builds paths from repo-root) always target the same repo — even when the caller
    # runs from elsewhere. Regression guard for the CWD/repo-root split.
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "sources.tsv").write_text("a\thttps://x/a.git\tlatest-release\n")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    seen: list[str] = []
    monkeypatch.setattr(up, "bump", lambda name, url, root: (seen.append(name), "1.0.0")[1])
    monkeypatch.chdir(elsewhere)                              # run from outside the repo
    rc = up.main(["--sources", "sources.tsv", "--repo-root", str(repo)])
    assert rc == 0
    assert seen == ["a"]                                      # found the repo's sources.tsv, not CWD's


def test_one_failure_does_not_block_others(monkeypatch, tmp_path, capsys):
    tsv = tmp_path / "sources.tsv"
    tsv.write_text("a\thttps://x/a.git\nb\thttps://x/b.git\n")
    calls = []

    def fake_bump(name, url, repo_root):
        calls.append(name)
        if name == "a":
            raise RuntimeError("boom")
        return "1.2.3"

    monkeypatch.setattr(up, "bump", fake_bump)
    rc = up.main(["--sources", str(tsv), "--repo-root", str(tmp_path)])
    assert rc == 1  # process every source, but fail the automation so partial errors are visible
    assert calls == ["a", "b"]  # b still processed after a raised
    out = capsys.readouterr().out
    assert "a: ERROR" in out and "b: bumped to 1.2.3" in out
