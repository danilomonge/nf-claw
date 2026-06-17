from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runner import discovery, orchestration
from runner.errors import NfclawError


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _collect_overrides(extras: list[str]) -> dict:
    out: dict = {}
    i = 0
    while i < len(extras):
        tok = extras[i]
        if tok.startswith("--"):
            body = tok[2:]
            if "=" in body:                                   # --key=value (one token)
                key, _, val = body.partition("=")
                out[key.replace("-", "_")] = val
                i += 1
                continue
            key = body.replace("-", "_")
            if i + 1 < len(extras) and not extras[i + 1].startswith("--"):
                out[key] = extras[i + 1]                       # --key value (two tokens)
                i += 2
            else:
                out[key] = True                               # --flag (boolean)
                i += 1
        else:
            i += 1
    return out


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(prog="nfclaw")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p_show = sub.add_parser("show")
    p_show.add_argument("name")
    p_run = sub.add_parser("run")
    p_run.add_argument("name")
    p_run.add_argument("--input")
    p_run.add_argument("--outdir", required=True)
    p_run.add_argument("-profile", "--profile", dest="profile", default="docker")
    p_run.add_argument("--params-file", dest="params_file")
    p_run.add_argument("--check", action="store_true")
    p_run.add_argument("--demo", action="store_true")
    p_run.add_argument("--resume", action="store_true")
    p_run.add_argument("--no-provenance", action="store_true")
    p_run.add_argument("--timeout", type=int, default=60 * 60 * 12)

    args, extras = parser.parse_known_args(argv)
    root = _repo_root()
    pdir = root / "pipelines"

    if args.cmd == "list":
        for p in discovery.discover(pdir):
            fm = p.frontmatter
            print(f"{p.name}\t{fm.get('version', '')}\t{fm.get('description', '')}")
        return 0

    if args.cmd == "show":
        p = discovery.find(args.name, pdir)
        print(p.skill_md.read_text(encoding="utf-8") if p.skill_md.exists()
              else f"(no skill.md for {args.name})")
        return 0

    if args.cmd == "run":
        try:
            res = orchestration.run_pipeline(
                args.name, repo_root=root,
                input_path=Path(args.input).expanduser().resolve() if args.input else None,
                outdir=Path(args.outdir).expanduser().resolve(),
                profile=args.profile,
                params_file=Path(args.params_file) if args.params_file else None,
                cli_overrides=_collect_overrides(extras),
                resume=args.resume, demo=args.demo, check_only=args.check,
                write_provenance=not args.no_provenance, timeout_seconds=args.timeout)
        except NfclawError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(res.command)
        rep = res.outputs_report
        if rep is not None:                                   # real run — surface where results landed
            print(f"outputs: {len(rep.files)} files in {res.outdir}")
            if rep.multiqc_report is not None:
                print(f"multiqc: {rep.multiqc_report}")
        return 0
    return 2
