# librarian/write_catalog.py
from __future__ import annotations

import argparse
import json
from pathlib import Path

from runner import discovery


def generate(*, pipelines_dir: Path, out_md: Path, out_json: Path) -> None:
    rows = [{"name": p.name,
             "version": p.frontmatter.get("version", ""),
             "description": p.frontmatter.get("description", ""),
             "input": p.frontmatter.get("input", ""),
             "output": p.frontmatter.get("output", ""),
             "tools": [t.strip() for t in (p.frontmatter.get("tools") or "").split(",")
                       if t.strip()]}
            for p in discovery.discover(pipelines_dir)]
    out_json.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _safe(text: object) -> str:  # keep free text safe inside a markdown table cell
        return " ".join(str(text).split()).replace("|", "\\|")

    lines = ["# Pipeline catalog", "",
             f"{len(rows)} nf-core pipelines. Grep this file for a keyword, then read "
             "`pipelines/<name>/skill.md`. `input` is derived from each pipeline's samplesheet "
             "schema; `output` is the guaranteed output contract (per-release detail is in the "
             "pipeline's upstream `docs/output.md`, linked from its skill). Each pipeline's "
             "`skill.md` and `catalog.json` also list the `tools` it runs, taken from the "
             "pipeline's own `CITATIONS.md`.", "",
             "| pipeline | version | input | output | description |",
             "|---|---|---|---|---|"]
    lines += [f"| `{r['name']}` | {r['version']} | {_safe(r['input'])} | {_safe(r['output'])} "
              f"| {_safe(r['description'])} |" for r in rows]
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="librarian.write_catalog")
    parser.add_argument("--pipelines-dir", default="pipelines")
    args = parser.parse_args(argv)
    generate(pipelines_dir=Path(args.pipelines_dir),
             out_md=Path("catalog.md"), out_json=Path("catalog.json"))
    print("wrote catalog.md and catalog.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
