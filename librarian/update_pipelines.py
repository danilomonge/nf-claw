# librarian/update_pipelines.py
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from librarian import write_skill
from librarian.add_pipeline import read_sources

_SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def select_latest(tags: list[str]) -> str | None:
    parsed = [(tuple(int(x) for x in m.groups()), t)
              for t in tags if (m := _SEMVER.match(t))]
    return max(parsed)[1] if parsed else None


def remote_tags(url: str) -> list[str]:
    r = subprocess.run(["git", "ls-remote", "--tags", "--refs", url],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return []
    return [line.split("\t")[-1].rsplit("/", 1)[-1] for line in r.stdout.splitlines()]


def bump(name: str, url: str, repo_root: Path) -> str | None:
    latest = select_latest(remote_tags(url))
    if latest is None:
        return None
    up = repo_root / "pipelines" / name / "upstream"
    subprocess.run(["git", "-C", str(up), "fetch", "--tags", "--depth", "1",
                    "origin", f"refs/tags/{latest}:refs/tags/{latest}"], check=False)
    subprocess.run(["git", "-C", str(up), "checkout", f"tags/{latest}"], check=True)
    write_skill.generate(name, pipelines_dir=repo_root / "pipelines")
    return latest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="librarian.update_pipelines")
    parser.add_argument("--sources", default="sources.tsv")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    for src in read_sources(Path(args.sources)):
        try:
            tag = bump(src.name, src.url, root)
            print(f"{src.name}: {'bumped to ' + tag if tag else 'no release tag found'}")
        except Exception as exc:                          # one failure never blocks others
            print(f"{src.name}: ERROR {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
