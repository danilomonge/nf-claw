from librarian import discover_pipelines as dp

# A trimmed shape of nf-co.re/pipelines.json -> remote_workflows.
WORKFLOWS = [
    {
        "name": "rnaseq",
        "full_name": "nf-core/rnaseq",
        "archived": False,
        "releases": [{"tag_name": "dev"}, {"tag_name": "3.14.0"}, {"tag_name": "3.26.0"}],
    },
    {
        "name": "abotyper",
        "full_name": "nf-core/abotyper",
        "archived": False,
        "releases": [{"tag_name": "dev"}],  # no stable release -> skipped
    },
    {
        "name": "oldpipe",
        "full_name": "nf-core/oldpipe",
        "archived": True,  # archived -> skipped even with a release
        "releases": [{"tag_name": "1.0.0"}],
    },
    {
        "name": "demo",
        "full_name": "nf-core/demo",
        "archived": False,
        "releases": [{"tag_name": "v1.2.0"}, {"tag_name": "1.0.0"}],
    },
]


def test_latest_stable_picks_highest_semver_ignoring_dev():
    assert dp.latest_stable(WORKFLOWS[0]["releases"]) == "3.26.0"
    assert dp.latest_stable([{"tag_name": "dev"}]) is None
    assert dp.latest_stable([{"tag_name": "1.0.0-rc1"}]) is None  # pre-release ignored


def test_candidates_filters_archived_and_releaseless_and_builds_url():
    cands = dp.candidates(WORKFLOWS)
    names = [c[0] for c in cands]
    assert names == ["demo", "rnaseq"]  # sorted; abotyper + oldpipe dropped
    assert ("demo", "https://github.com/nf-core/demo.git", "v1.2.0") in cands
    assert ("rnaseq", "https://github.com/nf-core/rnaseq.git", "3.26.0") in cands


def test_new_pipelines_excludes_already_tracked():
    fresh = dp.new_pipelines(WORKFLOWS, existing={"rnaseq"})
    assert [c[0] for c in fresh] == ["demo"]


def test_append_source_writes_tab_separated_row(tmp_path):
    src = tmp_path / "sources.tsv"
    src.write_text("# name\turl\tpolicy\nrnaseq\thttps://x\tlatest-release\n", encoding="utf-8")
    dp._append_source(src, "demo", "https://github.com/nf-core/demo.git")
    rows = [line for line in src.read_text().splitlines() if line and not line.startswith("#")]
    assert rows[-1] == "demo\thttps://github.com/nf-core/demo.git\tlatest-release"
