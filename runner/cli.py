from __future__ import annotations

import argparse
import sys
from pathlib import Path

from runner import discovery, orchestration, versions
from runner.errors import ErrorCode, NfclawError


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _parse_nxf_env(items: list[str]) -> dict[str, str]:
    """Parse repeatable `--nxf-env KEY=VALUE` into a dict, restricted to `NXF_*` variables.

    Restricting to NXF_* keeps the knob focused on Nextflow's own runtime (and the provenance
    record meaningful); any other environment a run needs is still inherited from the shell."""
    env: dict[str, str] = {}
    for item in items:
        key, sep, value = item.partition("=")
        key = key.strip()
        if not sep:
            raise NfclawError(ErrorCode.PARAMS_INVALID,
                              f"--nxf-env must be KEY=VALUE (got {item!r}).")
        if not key.startswith("NXF_"):
            raise NfclawError(ErrorCode.PARAMS_INVALID,
                              f"--nxf-env only accepts NXF_* variables (got {key!r}); "
                              "other environment is inherited from the shell.")
        env[key] = value
    return env


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
    p_show.add_argument("--pipeline-version", dest="pipeline_version")
    p_versions = sub.add_parser("versions")
    p_versions.add_argument("name")
    p_run = sub.add_parser("run")
    p_run.add_argument("name")
    p_run.add_argument("--input")
    p_run.add_argument("--outdir", required=True)
    p_run.add_argument("-profile", "--profile", dest="profile", default="docker")
    p_run.add_argument("--params-file", dest="params_file")
    p_run.add_argument("--pipeline-version", dest="pipeline_version")
    p_run.add_argument("--nxf-ver", dest="nxf_ver",
                       help="pin the Nextflow engine version for this run (sets NXF_VER)")
    p_run.add_argument("--nxf-env", dest="nxf_env", action="append", default=[],
                       metavar="KEY=VALUE",
                       help="set an NXF_* env var for this run (repeatable), e.g. "
                            "NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true")
    p_run.add_argument("--allow-spaces", dest="allow_spaces", action="store_true",
                       help="run even if a path contains spaces (off by default; spaces break "
                            "many bioinformatics tools and Nextflow's work dir)")
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
        if args.pipeline_version:
            try:
                discovery.find(args.name, pdir)                # 404 before any git work
                st = versions.ensure(args.name, args.pipeline_version,
                                     pipelines_dir=pdir, repo_root=root)
            except NfclawError as exc:
                print(str(exc), file=sys.stderr)
                return 1
            if versions.is_cached(st):                         # a non-pinned version → generate on demand
                skill_path, ref_path = versions.generate_docs(st, dest_dir=st.path.parent)
                print(skill_path.read_text(encoding="utf-8"))
                print(f"reference.md for this version cached at {ref_path}", file=sys.stderr)
                return 0
            # requested version IS the pin → fall through to the committed skill.md
        p = discovery.find(args.name, pdir)
        print(p.skill_md.read_text(encoding="utf-8") if p.skill_md.exists()
              else f"(no skill.md for {args.name})")
        return 0

    if args.cmd == "versions":
        try:
            avail = versions.available(args.name, pipelines_dir=pdir, repo_root=root)
        except NfclawError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        if not avail:
            print(f"No releases found for {args.name} (check network connectivity).",
                  file=sys.stderr)
            return 0
        for tag, is_pin in avail:
            print(f"{tag}\tlatest (pinned)" if is_pin else tag)
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
                write_provenance=not args.no_provenance, timeout_seconds=args.timeout,
                pipeline_version=args.pipeline_version,
                nxf_ver=args.nxf_ver, nxf_env=_parse_nxf_env(args.nxf_env),
                allow_spaces=args.allow_spaces)
        except NfclawError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        for w in res.warnings:                                # advisory, non-blocking
            print(f"warning: {w}", file=sys.stderr)
        print(res.command)
        rep = res.outputs_report
        if rep is not None:                                   # real run — surface where results landed
            print(f"outputs: {len(rep.files)} files in {res.outdir}")
            if rep.multiqc_report is not None:
                print(f"multiqc: {rep.multiqc_report}")
        return 0
    return 2
