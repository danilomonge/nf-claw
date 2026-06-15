from pathlib import Path

from librarian import add_pipeline


def test_read_sources_tsv(tmp_path):
    tsv = tmp_path / "sources.tsv"
    tsv.write_text("# c\nrnaseq\thttps://x/rnaseq.git\tlatest-release\n")
    srcs = add_pipeline.read_sources(tsv)
    assert srcs[0].name == "rnaseq" and srcs[0].policy == "latest-release"


def test_gitmodules_text():
    from librarian.add_pipeline import Source
    text = add_pipeline.gitmodules_text([Source("sarek", "https://x/sarek.git", "latest-release")])
    assert 'path = pipelines/sarek/upstream' in text
    assert 'url = https://x/sarek.git' in text
    assert 'branch' not in text  # matches what `git submodule add` writes (.gitmodules has no branch pin)
