from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from runner import discovery, orchestration, resources, verify, versions
from runner.errors import ErrorCode, NfclawError


_ENV_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_NXF_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:-edge)?$")


def _repo_root() -> Path:
    root = Path(__file__).resolve().parent.parent
    if not (root / "pipelines").is_dir():
        raise NfclawError(
            ErrorCode.ENVIRONMENT,
            "nf-claw repository content was not found next to the installed package.",
            fix="Run from a cloned nf-claw repository and install it with `pip install -e .`.",
        )
    return root


def _input_value(raw: str | None) -> "Path | str | None":
    """Resolve a local `--input` to an absolute Path; pass a remote URL through unchanged.

    A URL (contains `://`) must NOT go through `Path().resolve()`, which would mangle it into a
    bogus local path (e.g. `/repo/https:/host/ss.csv`). nf-core pipelines accept a remote
    samplesheet URL — Nextflow stages it and nf-schema validates it — so nfclaw forwards it as-is."""
    if not raw:
        return None
    return raw if "://" in raw else Path(raw).expanduser().resolve()


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
        if not _ENV_NAME_RE.fullmatch(key):
            raise NfclawError(ErrorCode.PARAMS_INVALID,
                              f"--nxf-env has an invalid environment variable name: {key!r}.")
        env[key] = value
    return env


def _positive_int(raw: str) -> int:
    value = int(raw)
    if value <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return value


def _nxf_version(raw: str) -> str:
    if not _NXF_VERSION_RE.fullmatch(raw):
        raise argparse.ArgumentTypeError(
            "must be a full Nextflow version such as 25.10.2 or 25.10.2-edge"
        )
    return raw


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
            raise NfclawError(
                ErrorCode.PARAMS_INVALID,
                f"unexpected extra argument: {tok!r}",
                fix="Pipeline parameters must be passed as --param value or --param=value.",
            )
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
    # Compare a replay against the run it reproduces. Keyed on path, because comparing the raw
    # `outputs.sha256` lines counts one changed file as both a missing and an extra one.
    p_verify = sub.add_parser("verify")
    p_verify.add_argument("replay", help="--outdir of the replayed run")
    p_verify.add_argument("--against", dest="against", required=True,
                          help="--outdir of the original run it should reproduce")
    # allow_abbrev=False: `run` forwards every unknown flag to the pipeline (via parse_known_args
    # → _collect_overrides). With abbreviation on, a pipeline flag that is a prefix of a reserved
    # nfclaw flag (e.g. `--res`, `--time`) would be silently swallowed as `--resume`/`--timeout`
    # instead of passed through. Turning it off keeps reserved flags exact and lets everything else
    # reach Nextflow. Full flag names and single-dash `-profile` are unaffected.
    p_run = sub.add_parser("run", allow_abbrev=False)
    p_run.add_argument("name")
    p_run.add_argument("--input")
    p_run.add_argument("--outdir", required=True)
    p_run.add_argument("-profile", "--profile", dest="profile", default="docker")
    p_run.add_argument("--params-file", dest="params_file")
    p_run.add_argument("--pipeline-version", dest="pipeline_version")
    p_run.add_argument("--nxf-ver", dest="nxf_ver", type=_nxf_version,
                       help="pin the Nextflow engine version for this run (sets NXF_VER)")
    p_run.add_argument("--nxf-env", dest="nxf_env", action="append", default=[],
                       metavar="KEY=VALUE",
                       help="set an NXF_* env var for this run (repeatable), e.g. "
                            "NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true")
    # The nf-core-documented way to run on a machine smaller than the pipeline's default requests
    # (`process_high` is 12 CPUs / 72.GB in the stock nf-core base.config): a `process.resourceLimits`
    # ceiling. nfclaw generates the config and passes it with `-c`, so no hand-written file is needed.
    p_run.add_argument("--limit-cpus", dest="limit_cpus", type=_positive_int, metavar="N",
                       help="cap every process request at N CPUs "
                            "(Nextflow process.resourceLimits)")
    p_run.add_argument("--limit-memory", dest="limit_memory", metavar="SIZE",
                       help="cap every process request at SIZE memory, e.g. 15.GB")
    p_run.add_argument("--limit-time", dest="limit_time", metavar="DURATION",
                       help="cap every process request at DURATION, e.g. 1.h")
    p_run.add_argument("-c", "--config", dest="config", action="append", default=[],
                       metavar="PATH",
                       help="extra Nextflow config file passed through as `-c` (repeatable), e.g. "
                            "a docker host-network or custom-resources config")
    p_run.add_argument("--allow-spaces", dest="allow_spaces", action="store_true",
                       help="run even if a path contains spaces (off by default; spaces break "
                            "many bioinformatics tools and Nextflow's work dir)")
    p_run.add_argument("--check", action="store_true")
    p_run.add_argument("--demo", action="store_true")
    p_run.add_argument("--resume", action="store_true")
    p_run.add_argument("--no-provenance", action="store_true")
    p_run.add_argument("--timeout", type=_positive_int, default=60 * 60 * 12)

    args, extras = parser.parse_known_args(argv)
    try:
        root = _repo_root()
    except NfclawError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    pdir = root / "pipelines"

    if args.cmd == "list":
        for p in discovery.discover(pdir):
            fm = p.frontmatter
            print(f"{p.name}\t{fm.get('version', '')}\t{fm.get('description', '')}")
        return 0

    if args.cmd == "show":
        try:
            p = discovery.find(args.name, pdir)                # 404 before any git work
            if args.pipeline_version:
                st = versions.ensure(args.name, args.pipeline_version,
                                     pipelines_dir=pdir, repo_root=root)
                if versions.is_cached(st):                     # a non-pinned version → generate on demand
                    skill_path, ref_path = versions.generate_docs(st, dest_dir=st.path.parent)
                    print(skill_path.read_text(encoding="utf-8"))
                    print(f"reference.md for this version cached at {ref_path}", file=sys.stderr)
                    return 0
                # requested version IS the pin → fall through to the committed skill.md
        except NfclawError as exc:
            print(str(exc), file=sys.stderr)
            return 1
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

    if args.cmd == "verify":
        try:
            cmp = verify.compare(Path(args.against).expanduser().resolve(),
                                 Path(args.replay).expanduser().resolve())
        except NfclawError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(verify.report(cmp), end="")
        # A file the replay did not make (or made and the original did not) means it did different
        # work — that is a failure. Differing bytes in the same file are expected and are not.
        return 0 if cmp.structurally_equal else 1

    if args.cmd == "run":
        try:
            res = orchestration.run_pipeline(
                args.name, repo_root=root,
                input_path=_input_value(args.input),
                outdir=Path(args.outdir).expanduser().resolve(),
                profile=args.profile,
                params_file=Path(args.params_file) if args.params_file else None,
                cli_overrides=_collect_overrides(extras),
                resume=args.resume, demo=args.demo, check_only=args.check,
                write_provenance=not args.no_provenance, timeout_seconds=args.timeout,
                pipeline_version=args.pipeline_version,
                nxf_ver=args.nxf_ver, nxf_env=_parse_nxf_env(args.nxf_env),
                allow_spaces=args.allow_spaces, configs=args.config,
                limits=resources.parse(args.limit_cpus, args.limit_memory, args.limit_time))
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
