# librarian/check_drift.py
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from librarian import write_catalog, write_skill


def check(pipelines_dir: Path) -> list[str]:
    drift: list[str] = []
    for d in sorted(p for p in pipelines_dir.iterdir() if p.is_dir()):
        name = d.name
        fresh = dict(zip(("skill.md", "reference.md"),
                         write_skill.render(name, pipelines_dir=pipelines_dir)))
        for fname, expected in fresh.items():           # compare in memory; never touch the tree
            committed = d / fname
            if not committed.exists():
                drift.append(f"{name}/{fname} is missing (run `make build`)")
            elif committed.read_text(encoding="utf-8") != expected:
                drift.append(f"{name}/{fname} is stale (run `make build`)")

    # catalog.{md,json} must also stay in sync with the skill.md frontmatter
    repo = pipelines_dir.parent
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
