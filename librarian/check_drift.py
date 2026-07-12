# librarian/check_drift.py
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

from librarian import write_catalog, write_skill
from librarian.add_pipeline import read_sources
from runner import submodule as submod


def _duplicates(names: list[str]) -> list[str]:
    return sorted(name for name, count in Counter(names).items() if count > 1)


def _gitmodule_entries(path: Path) -> tuple[list[tuple[str, str]], list[str]]:
    """Return pipeline name/url pairs plus malformed-block errors from .gitmodules."""
    text = path.read_text(encoding="utf-8")
    entries: list[tuple[str, str]] = []
    errors: list[str] = []
    for block in re.split(r"(?=^\[submodule )", text, flags=re.MULTILINE):
        if not block.startswith("[submodule "):
            continue
        path_match = re.search(r"^\s*path\s*=\s*pipelines/([^/]+)/upstream\s*$",
                               block, flags=re.MULTILINE)
        url_match = re.search(r"^\s*url\s*=\s*(\S+)\s*$", block, flags=re.MULTILINE)
        if path_match is None or url_match is None:
            header = block.splitlines()[0]
            errors.append(f".gitmodules has malformed pipeline block: {header}")
            continue
        entries.append((path_match.group(1), url_match.group(1)))
    return entries, errors


def _structure_drift(repo: Path, pipeline_names: list[str]) -> list[str]:
    """Check the offline repository manifests describe the same pipeline set and remotes."""
    sources_path, gitmodules_path = repo / "sources.tsv", repo / ".gitmodules"
    if not sources_path.exists() and not gitmodules_path.exists():
        return []  # small unit-test/embedded library without repository manifests
    drift: list[str] = []
    if not sources_path.exists():
        return ["sources.tsv is missing"]
    if not gitmodules_path.exists():
        return [".gitmodules is missing"]
    try:
        sources = read_sources(sources_path)
    except (OSError, ValueError) as exc:
        return [f"sources.tsv is invalid: {exc}"]
    gitmodules, errors = _gitmodule_entries(gitmodules_path)
    drift.extend(errors)

    source_names = [src.name for src in sources]
    module_names = [name for name, _ in gitmodules]
    for label, names in (("sources.tsv", source_names), (".gitmodules", module_names)):
        dupes = _duplicates(names)
        if dupes:
            drift.append(f"{label} has duplicate pipelines: {', '.join(dupes)}")

    expected = set(pipeline_names)
    for label, names in (("sources.tsv", source_names), (".gitmodules", module_names)):
        actual = set(names)
        missing, extra = sorted(expected - actual), sorted(actual - expected)
        if missing:
            drift.append(f"{label} is missing pipelines: {', '.join(missing)}")
        if extra:
            drift.append(f"{label} has unknown pipelines: {', '.join(extra)}")

    source_urls = {src.name: src.url for src in sources}
    module_urls = dict(gitmodules)
    for name in sorted(set(source_urls) & set(module_urls)):
        if source_urls[name] != module_urls[name]:
            drift.append(
                f"{name} remote differs: sources.tsv={source_urls[name]} "
                f".gitmodules={module_urls[name]}"
            )
    return drift


def check(pipelines_dir: Path) -> list[str]:
    drift: list[str] = []
    pipeline_dirs = sorted(p for p in pipelines_dir.iterdir() if p.is_dir())
    repo = pipelines_dir.parent
    drift.extend(_structure_drift(repo, [d.name for d in pipeline_dirs]))
    for d in pipeline_dirs:
        name = d.name
        st = submod.resolve(name, pipelines_dir)
        if not st.complete:
            missing = ", ".join(st.missing_files)
            drift.append(
                f"{name}/upstream is incomplete (missing {missing}; "
                f"run `git submodule update --init pipelines/{name}/upstream`)"
            )
            continue
        fresh = dict(zip(("skill.md", "reference.md"),
                         write_skill.render_status(st), strict=True))
        for fname, expected in fresh.items():           # compare in memory; never touch the tree
            committed = d / fname
            if not committed.exists():
                drift.append(f"{name}/{fname} is missing (run `make build`)")
            elif committed.read_text(encoding="utf-8") != expected:
                drift.append(f"{name}/{fname} is stale (run `make build`)")

    # catalog.{md,json} must also stay in sync with the skill.md frontmatter
    with tempfile.TemporaryDirectory() as td:
        tmp_md, tmp_json = Path(td) / "catalog.md", Path(td) / "catalog.json"
        write_catalog.generate(pipelines_dir=pipelines_dir, out_md=tmp_md, out_json=tmp_json)
        for fname, tmp in (("catalog.md", tmp_md), ("catalog.json", tmp_json)):
            committed = repo / fname
            if not committed.exists():
                drift.append(f"{fname} missing (run `make build`)")
            elif committed.read_text(encoding="utf-8") != tmp.read_text(encoding="utf-8"):
                drift.append(f"{fname} is stale (run `make build`)")
    return drift


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="librarian.check_drift")
    parser.add_argument("--pipelines-dir", default="pipelines")
    args = parser.parse_args(argv)
    drift = check(Path(args.pipelines_dir))
    for d in drift:
        print(f"DRIFT: {d}", file=sys.stderr)
    return 1 if drift else 0


if __name__ == "__main__":
    raise SystemExit(main())
