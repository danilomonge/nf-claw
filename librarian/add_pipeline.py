# librarian/add_pipeline.py
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    policy: str


def read_sources(tsv: Path) -> list[Source]:
    out: list[Source] = []
    for line in tsv.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t") if "\t" in line else line.split()
        name, url = parts[0].strip(), parts[1].strip()
        policy = parts[2].strip() if len(parts) > 2 else "latest-release"
        out.append(Source(name, url, policy))
    return out


def gitmodules_text(sources: list[Source]) -> str:
    return "".join(
        f'[submodule "pipelines/{s.name}/upstream"]\n'
        f"\tpath = pipelines/{s.name}/upstream\n"
        f"\turl = {s.url}\n"
        f"\tbranch = master\n"
        for s in sources
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="librarian.add_pipeline")
    parser.add_argument("--sources", default="sources.tsv")
    args = parser.parse_args(argv)
    srcs = read_sources(Path(args.sources))
    print(gitmodules_text(srcs))
    print(f"# {len(srcs)} pipelines. To materialize each submodule, run:")
    for s in srcs:
        print(f"git submodule add {s.url} pipelines/{s.name}/upstream")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
