"""Pipeline chains: several pipelines run in sequence, each one's outputs handed to the next.

A chain is an ordered list of stages. Every stage is an ordinary `nfclaw run` — the same checks, run
log and provenance bundle — in its own directory `<outdir>/NN-<stage>/`, started only after the stage
before it succeeded. Between two stages a handoff rule (runner.handoff) turns the finished upstream
run into the downstream's parameters. The chain's own record lives in `<outdir>/chain/`: the spec,
each stage's state, the handoff snapshots and a log whose last line states the outcome — so a chain
can be resumed, extended, audited and reconstructed from disk. Deliberately linear: no DAG, no
scheduler, no daemon.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from runner import (discovery, engine_version, execution, handoff, inputs, nextflow_command,
                    orchestration, parameters, preflight, resources, runlog, versions)
from runner import schema as schema_mod
from runner.errors import ErrorCode, NfclawError
from runner.submodule import SubmoduleStatus

try:
    import fcntl                                  # POSIX file locks (macOS/Linux)
except ImportError:                              # pragma: no cover — Windows has no fcntl
    fcntl = None

RECORD_DIRNAME = "chain"
LOG_NAME = "chain.log"
_ID = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_OPTION_KEYS = {"profile", "nxf_ver", "nxf_env", "config", "limits"}
_CHAIN_KEYS = {"stages", "allow_spaces"} | _OPTION_KEYS
_STAGE_KEYS = {"id", "pipeline", "input", "params", "params_file", "pipeline_version",
               "retries", "demo", "handoff"} | _OPTION_KEYS
_LIMIT_KEYS = {"cpus", "memory", "time"}
_PROBE_TIMEOUT = 300


# --- the spec --------------------------------------------------------------------------------

@dataclass(frozen=True)
class Stage:
    index: int                        # 1-based position in the chain
    id: str
    pipeline: str
    input: Any                        # stage's own --input (usually only the first stage has one)
    params: dict                      # the stage's own pipeline parameters (as on the command line)
    params_file: Path | None
    pipeline_version: str | None
    retries: int                      # relaunches (with -resume) after a pipeline failure
    demo: bool
    handoff: dict | Path | None       # an inline rule, or a rule file, used INTO this stage
    # How this stage's Nextflow runs, where it differs from the chain's: `profile`, `nxf_ver`,
    # `nxf_env` (merged over the chain's), `configs`, `limits`. Releases of different ages can need
    # different engines — fetchngs 1.13 wants Nextflow >= 25.10.4, mag 5.5 >= 26.04, and an older
    # atacseq a parser before 26.04's strict one.
    options: dict = field(default_factory=dict)

    @property
    def dirname(self) -> str:
        return f"{self.index:02d}-{self.id}"


@dataclass(frozen=True)
class RunOptions:
    """How one stage's Nextflow runs — what the `nfclaw run` flags of the same names set."""
    profile: str = "docker"
    nxf_ver: str | None = None
    nxf_env: dict[str, str] = field(default_factory=dict)
    configs: tuple[str, ...] = ()
    limits: resources.ResourceLimits | None = None


@dataclass(frozen=True)
class ChainSpec:
    stages: tuple[Stage, ...]
    profile: str = "docker"
    nxf_ver: str | None = None
    nxf_env: dict[str, str] = field(default_factory=dict)
    configs: tuple[str, ...] = ()
    limits: resources.ResourceLimits | None = None
    allow_spaces: bool = False


def _bad(message: str) -> NfclawError:
    return NfclawError(ErrorCode.PARAMS_INVALID, f"chain spec: {message}",
                       fix="See docs/chaining.md for the spec format.")


def _abs(value: str) -> str:
    """A path in the spec, absolute — relative ones mean what they would on the command line."""
    return str(Path(value).expanduser().resolve())


def options(spec: ChainSpec, stage: Stage) -> RunOptions:
    """The run options of `stage`: the chain's, with the stage's own overrides on top."""
    o = stage.options
    return RunOptions(profile=o.get("profile", spec.profile),
                      nxf_ver=o.get("nxf_ver", spec.nxf_ver),
                      nxf_env={**spec.nxf_env, **o.get("nxf_env", {})},
                      configs=o.get("configs", spec.configs),
                      limits=o.get("limits", spec.limits))


def _parse_options(raw: dict, where: str) -> dict:
    """The run options `raw` sets (chain-wide or for one stage), validated like the `nfclaw run`
    flags of the same names; only the keys present are returned."""
    out: dict[str, Any] = {}
    if "profile" in raw:
        if not isinstance(raw["profile"], str) or not raw["profile"].strip():
            raise _bad(f"{where}: 'profile' must be a profile name such as \"docker\"")
        out["profile"] = raw["profile"]
    if "limits" in raw:
        limits = raw["limits"] or {}
        if not isinstance(limits, dict) or set(limits) - _LIMIT_KEYS:
            raise _bad(f"{where}: 'limits' takes only: {', '.join(sorted(_LIMIT_KEYS))}")
        cpus = limits.get("cpus")
        if cpus is not None and (not isinstance(cpus, int) or isinstance(cpus, bool)):
            raise _bad(f"{where}: 'limits.cpus' must be a whole number")
    if "config" in raw:
        configs = raw["config"] or []
        if not isinstance(configs, list) or not all(isinstance(c, str) for c in configs):
            raise _bad(f"{where}: 'config' must list Nextflow config file paths")
        out["configs"] = tuple(_abs(c) for c in configs)
    try:
        if "nxf_env" in raw:
            out["nxf_env"] = resources.parse_nxf_env(raw["nxf_env"] or {})
        if raw.get("nxf_ver"):
            out["nxf_ver"] = resources.check_nxf_version(raw["nxf_ver"])
        if "limits" in raw:
            lim = raw["limits"] or {}
            parsed = resources.parse(lim.get("cpus"), lim.get("memory"), lim.get("time"))
            out["limits"] = None if parsed.is_empty() else parsed
    except NfclawError as exc:
        raise _bad(f"{where}: {exc.message}") from None
    return out


def _options_json(opts: dict) -> dict:
    """Run options as a spec writes them (for chain.json)."""
    out: dict[str, Any] = {}
    for key in ("profile", "nxf_ver", "nxf_env"):
        if key in opts:
            out[key] = opts[key]
    if "configs" in opts:
        out["config"] = list(opts["configs"])
    if "limits" in opts:
        lim = opts["limits"]
        out["limits"] = ({k: v for k, v in (("cpus", lim.cpus), ("memory", lim.memory),
                                            ("time", lim.time)) if v is not None} if lim else {})
    return out


def load_spec(path: Path) -> ChainSpec:
    """Read a chain spec (JSON, or YAML when pyyaml is installed)."""
    return parse_spec(parameters.load_params_file(path, label="chain spec"))


def parse_spec(data: dict) -> ChainSpec:
    if not isinstance(data, dict):
        raise _bad("must be an object")
    if unknown := sorted(set(data) - _CHAIN_KEYS):
        raise _bad(f"unknown keys: {', '.join(unknown)}")
    raw_stages = data.get("stages")
    if not isinstance(raw_stages, list) or not raw_stages:
        raise _bad("'stages' must list at least one stage")
    stages: list[Stage] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_stages, start=1):
        if not isinstance(raw, dict) or not isinstance(raw.get("pipeline"), str):
            raise _bad(f"stage {index} must be an object with a 'pipeline'")
        if unknown := sorted(set(raw) - _STAGE_KEYS):
            raise _bad(f"stage {index}: unknown keys: {', '.join(unknown)}")
        sid = raw.get("id") or raw["pipeline"]
        if not isinstance(sid, str) or not _ID.fullmatch(sid):
            raise _bad(f"stage {index}: id {sid!r} must match {_ID.pattern}")
        if sid in seen:
            raise _bad(f"duplicate stage id '{sid}' (give one of them its own 'id')")
        seen.add(sid)
        retries = raw.get("retries") or 0
        if not isinstance(retries, int) or isinstance(retries, bool) or retries < 0:
            raise _bad(f"stage '{sid}': 'retries' must be a whole number >= 0")
        params = raw.get("params") or {}
        if not isinstance(params, dict):
            raise _bad(f"stage '{sid}': 'params' must be an object of pipeline parameters")
        version = raw.get("pipeline_version")
        if version is not None and not isinstance(version, str):
            raise _bad(f"stage '{sid}': 'pipeline_version' must be a string such as \"3.27.0\"")
        hand = raw.get("handoff")
        if hand is not None and not isinstance(hand, (dict, str)):
            raise _bad(f"stage '{sid}': 'handoff' must be a rule object or a path to a rule file")
        params_file = raw.get("params_file")
        if params_file is not None and not isinstance(params_file, str):
            raise _bad(f"stage '{sid}': 'params_file' must be a path")
        # Keys as on the command line: `--skip-busco` and `skip_busco` name one parameter.
        params = {str(k).replace("-", "_"): v for k, v in params.items()}
        stage_input = raw.get("input")
        if "input" in params:                             # the same --input, written as a param
            if stage_input is not None:
                raise _bad(f"stage '{sid}': give its input once — 'input' or 'params.input'")
            stage_input = params.pop("input")
        stages.append(Stage(
            index=index, id=sid, pipeline=raw["pipeline"], input=stage_input,
            params=params,
            params_file=Path(_abs(params_file)) if params_file else None,
            pipeline_version=version or None, retries=retries,
            demo=bool(raw.get("demo", False)),
            handoff=Path(_abs(hand)) if isinstance(hand, str) else hand,
            options=_parse_options(raw, f"stage '{sid}'")))
    chain_opts = _parse_options(data, "chain")
    return ChainSpec(stages=tuple(stages), profile=chain_opts.get("profile", "docker"),
                     nxf_ver=chain_opts.get("nxf_ver"), nxf_env=chain_opts.get("nxf_env", {}),
                     configs=chain_opts.get("configs", ()), limits=chain_opts.get("limits"),
                     allow_spaces=bool(data.get("allow_spaces", False)))


# --- the plan: every stage and handoff resolved and checked before anything runs ------------

@dataclass(frozen=True)
class Planned:
    stage: Stage
    tree: SubmoduleStatus             # the pipeline code this stage runs
    rule: handoff.Rule | None         # the handoff INTO this stage (None for the first)
    input: Any                        # the stage's own --input, resolved (absolute when local)
    params: dict                      # its params + what the next stage's rule sets on it


def _rule_into(up: Stage, down: Stage, registry) -> handoff.Rule | None:
    if down.handoff is None:
        return registry.get((up.pipeline, down.pipeline))
    if isinstance(down.handoff, dict):
        return handoff.parse_rule(down.handoff, upstream=up.pipeline, downstream=down.pipeline,
                                  origin=f"inline handoff of stage '{down.id}'")
    return handoff.load_rule_file(down.handoff, upstream=up.pipeline, downstream=down.pipeline)


def plan(spec: ChainSpec, *, repo_root: Path) -> list[Planned]:
    """Resolve every stage's pipeline code and every handoff, and check how they fit together."""
    pdir = repo_root / "pipelines"
    for s in spec.stages:
        discovery.find(s.pipeline, pdir)                       # 404 before any git work
    registry = handoff.load_registry(repo_root)
    trees = [versions.ensure(s.pipeline, s.pipeline_version, pipelines_dir=pdir,
                             repo_root=repo_root) for s in spec.stages]
    rules: list[handoff.Rule | None] = [None]
    problems: list[str] = []
    for i in range(1, len(spec.stages)):
        up, down = spec.stages[i - 1], spec.stages[i]
        rule = _rule_into(up, down, registry)
        rules.append(rule)
        if rule is None:
            known = sorted(d for (u, d) in registry if u == up.pipeline)
            problems.append(
                f"no handoff from {up.pipeline} to {down.pipeline} (stage '{down.id}')"
                + (f"; {up.pipeline} feeds: {', '.join(known)}" if known else "")
                + f" — add handoffs/{up.pipeline}/{down.pipeline}.json, or give stage "
                  f"'{down.id}' an inline \"handoff\" (docs/chaining.md)")
            continue
        problems += handoff.check_rule(rule, trees[i - 1].path, trees[i].path)
        for key, value in rule.upstream_params.items():
            if key in up.params and up.params[key] != value:
                problems.append(f"stage '{up.id}' sets --{key}={up.params[key]}, but the handoff "
                                f"to '{down.id}' needs --{key}={value}")
    if problems:
        raise NfclawError(ErrorCode.PARAMS_INVALID, "The chain cannot run as specified.",
                          fix="Nothing was launched. Fix the stages or handoffs listed.",
                          details={"issues": problems})
    out: list[Planned] = []
    for i, s in enumerate(spec.stages):
        nxt = rules[i + 1] if i + 1 < len(rules) else None
        injected = dict(nxt.upstream_params) if nxt else {}
        ps = schema_mod.load_param_schema(trees[i].path)
        resolved = inputs.resolve(s.input, trees[i].path)
        out.append(Planned(s, trees[i], rules[i], resolved.value if resolved else None,
                           parameters.resolve_path_params({**injected, **s.params}, ps)))
    return out


def _file_sha256(path: Path | None) -> str | None:
    return handoff.sha256_file(path) if path is not None and path.is_file() else None


def fingerprint(p: Planned) -> str:
    """What a stage would do. A stage that succeeded is frozen: resuming with a spec that changes
    its fingerprint is refused (no silent re-run, no stale results under a new definition)."""
    s = p.stage
    body = {"pipeline": s.pipeline, "pipeline_version": s.pipeline_version, "input": p.input,
            "params": p.params, "params_file": _file_sha256(s.params_file), "demo": s.demo,
            "handoff": p.rule.sha256() if p.rule else None}
    text = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalized(spec: ChainSpec, planned: list[Planned]) -> dict:
    """The spec as `chain/chain.json` records it: absolute paths, so it means the same thing from any
    directory — it is what `--resume` without a spec, and a replay of the chain, re-read."""
    lim = spec.limits
    return {
        "profile": spec.profile, "nxf_ver": spec.nxf_ver, "nxf_env": dict(spec.nxf_env),
        "config": list(spec.configs), "allow_spaces": spec.allow_spaces,
        "limits": ({k: v for k, v in (("cpus", lim.cpus), ("memory", lim.memory),
                                      ("time", lim.time)) if v is not None} if lim else {}),
        "stages": [{"id": p.stage.id, "pipeline": p.stage.pipeline, "input": p.input,
                    "params": {k: v for k, v in p.params.items() if k in p.stage.params},
                    "params_file": str(p.stage.params_file) if p.stage.params_file else None,
                    "pipeline_version": p.stage.pipeline_version, "retries": p.stage.retries,
                    "demo": p.stage.demo,
                    "handoff": (str(p.stage.handoff) if isinstance(p.stage.handoff, Path)
                                else p.stage.handoff),
                    **_options_json(p.stage.options)}
                   for p in planned],
    }


# --- running it ----------------------------------------------------------------------------

@dataclass
class ChainResult:
    outdir: Path
    outcome: str
    stages: list[dict]
    commands: list[tuple[str, str]] = field(default_factory=list)   # --check: (stage, command)
    log_path: Path | None = None


def _write_json(path: Path, data: Any) -> Path:
    """Atomically: a reader polling state.json never sees half a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


@contextlib.contextmanager
def _lock(record: Path, outdir: Path) -> Iterator[None]:
    """One chain process per --outdir: two would race on the same stages and state."""
    record.mkdir(parents=True, exist_ok=True)
    fd = os.open(record / ".lock", os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o644)
    try:
        if fcntl is not None:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise NfclawError(
                    ErrorCode.ENVIRONMENT, f"another nfclaw chain is running in {outdir}",
                    fix=f"Wait for it (tail -n 1 {record / 'logs' / LOG_NAME}) or stop it with "
                        "kill <its pid>.") from None
        yield
    finally:
        os.close(fd)


def _retryable(exc: NfclawError) -> bool:
    """Only a pipeline that ran and failed is worth relaunching: a bad parameter, an invalid sheet or
    a missing tool fails the same way every time, and a timeout means the budget is spent."""
    return exc.code is ErrorCode.EXECUTION_FAILED and "timeout_seconds" not in exc.details


def _short(exc: NfclawError) -> str:
    code = exc.details.get("exit_code")
    return f"failed (exit status {code})" if code is not None else exc.code.value


def _warner(on_warning: Callable[[str], None] | None, stage: Stage):
    return None if on_warning is None else (lambda m: on_warning(f"[{stage.dirname}] {m}"))


def _say(log: runlog.RunLog, text: str) -> None:
    """A chain event: into the chain log, and onto the terminal between the stages' own output."""
    log.note(f"    {text}")
    print(f"nfclaw chain: {text}", file=sys.stderr, flush=True)


def _deferred(p: Planned) -> frozenset[str]:
    """The parameters of a stage its handoff will supply — unless the stage sets them itself."""
    if p.rule is None:
        return frozenset()
    return frozenset(t for t in p.rule.params
                     if not (t == "input" and p.input not in (None, "")) and t not in p.stage.params)


def _check(spec: ChainSpec, planned: list[Planned], *, repo_root: Path, outdir: Path,
           on_warning, keep: bool) -> list[tuple[str, str]]:
    """Validate each stage as `nfclaw run --check` would, writing nothing into --outdir. A later
    stage's handoff parameters do not exist yet; they are named as deferred, so only the stage's own
    parameters are judged (the handoff itself was checked statically by `plan`). `keep` keeps the
    files the printed commands name (for `--check`); the validation before a real run drops them."""
    commands = []
    for p in planned:
        opts = options(spec, p.stage)
        res = orchestration.run_pipeline(
            p.stage.pipeline, repo_root=repo_root, input_path=p.input,
            outdir=outdir / p.stage.dirname, profile=opts.profile,
            params_file=p.stage.params_file, cli_overrides=dict(p.params), resume=False,
            demo=p.stage.demo, check_only=True, write_provenance=False, timeout_seconds=None,
            pipeline_version=p.stage.pipeline_version, nxf_ver=opts.nxf_ver,
            nxf_env=opts.nxf_env, allow_spaces=spec.allow_spaces, configs=opts.configs,
            limits=opts.limits, on_warning=_warner(on_warning, p.stage),
            deferred_params=_deferred(p))
        if not keep and res.staging is not None:
            shutil.rmtree(res.staging, ignore_errors=True)
        label = p.stage.dirname
        if deferred := _deferred(p):                      # the printed command lacks them: say so
            flags = ", ".join(f"--{n.replace('_', '-')}" for n in sorted(deferred))
            label += f" — {flags} from the stage before it ({p.rule.origin})"
        commands.append((label, nextflow_command.shell_line(res.command, res.env)))
    return commands


def _probe_config(spec: ChainSpec, p: Planned) -> list[str]:
    """Whether the stage's Nextflow configuration parses with the engine it will run under.

    `nextflow config` resolves the pipeline's config and profiles without running anything (a few
    seconds). It catches the one failure no schema can predict: a release whose config the engine
    rejects outright — an older release on Nextflow 26's strict parser — which would otherwise
    surface only when that stage launches, after every stage before it has run. Run from a scratch
    directory so nothing lands anywhere; a probe that cannot run, or does not finish, is no verdict."""
    opts = options(spec, p.stage)
    if shutil.which("nextflow") is None:
        return []                                         # preflight reports a missing nextflow
    overlay = dict(opts.nxf_env)
    if opts.nxf_ver:
        overlay["NXF_VER"] = opts.nxf_ver
    cmd = ["nextflow", "config", str(p.tree.path),
           "-profile", nextflow_command.compose_profile(opts.profile, demo=p.stage.demo)]
    for cfg in opts.configs:
        cmd += ["-c", cfg]
    with tempfile.TemporaryDirectory(prefix="nfclaw-probe-") as scratch:
        try:
            r = subprocess.run(cmd, cwd=scratch, env={**os.environ, **overlay},
                               capture_output=True, text=True, timeout=_PROBE_TIMEOUT)
        except (OSError, subprocess.SubprocessError):
            return []
    if r.returncode == 0:
        return []
    engine = f"Nextflow {opts.nxf_ver}" if opts.nxf_ver else "the installed Nextflow"
    report = (runlog.error_excerpt(r.stdout or "")
              + runlog.stderr_excerpt(r.stderr or "")) or [f"exit status {r.returncode}"]
    # The engine the release was written for is the one it declares (docs/compatibility.md).
    declared = engine_version.minimum_version(
        engine_version.required_spec(p.tree.path / "nextflow.config"))
    hint = (f" — the release declares Nextflow {declared}: try \"nxf_ver\": \"{declared}\""
            if declared and declared != opts.nxf_ver else "")
    return [f"{p.stage.dirname} ({p.stage.pipeline}): {engine} cannot parse its "
            f"configuration{hint}:\n" + "\n".join(f"      {line}" for line in report)]


def _check_frozen(state: dict, planned: list[Planned]) -> None:
    problems = []
    for i, old in enumerate(state.get("stages", [])):
        if old.get("status") != "success":
            continue
        if i >= len(planned) or planned[i].stage.id != old.get("id"):
            problems.append(f"stage '{old.get('id')}' already succeeded as stage {i + 1}; a "
                            "resumed chain keeps its succeeded stages, in order")
        elif fingerprint(planned[i]) != old.get("fingerprint"):
            problems.append(f"stage '{old.get('id')}' already succeeded with a different definition "
                            "(its pipeline, version, input, params or handoff changed — including "
                            "what the handoff to the next stage sets on it)")
    if problems:
        raise NfclawError(ErrorCode.PARAMS_INVALID,
                          "This spec does not match the chain being resumed.",
                          fix="Edit or append only stages that have not succeeded, or run the "
                              "edited chain in a fresh --outdir.",
                          details={"issues": problems})


def run_chain(spec: ChainSpec | None, *, repo_root: Path, outdir: Path, check_only: bool = False,
              resume: bool = False, timeout_seconds: int | None = None,
              on_warning: Callable[[str], None] | None = None) -> ChainResult:
    """Run (or `check_only`: validate) a chain into `outdir`.

    Everything that can be judged before a pipeline runs is judged first — every stage's pipeline
    and version, every handoff against both schemas, every stage's own parameters — so a mistake in
    the last stage never surfaces after the first has run for hours. `resume` continues the chain
    recorded in `outdir` (with `spec`, or the recorded one when it is None)."""
    record = outdir / RECORD_DIRNAME
    state = _read_json(record / "state.json") if resume else None
    if resume and not isinstance(state, dict):
        raise NfclawError(ErrorCode.ENVIRONMENT, f"no chain to resume in {outdir}",
                          fix="Start it without --resume, or check the --outdir.")
    if spec is None:
        if not resume:
            raise NfclawError(ErrorCode.PARAMS_INVALID, "a chain spec is required",
                              fix="Pass the spec file, or --resume an existing chain.")
        spec = parse_spec(_read_json(record / "chain.json") or {})
    if not resume and (issue := preflight._outdir_issue(outdir, resume=False,
                                                        check_only=check_only)):
        raise NfclawError(ErrorCode.ENVIRONMENT, "Preflight checks failed.",
                          details={"issues": [issue.replace("to continue that run",
                                                            "to continue that chain")]})
    planned = plan(spec, repo_root=repo_root)
    if state is not None:
        _check_frozen(state, planned)
    done = {s.get("id") for s in (state or {}).get("stages", []) if s.get("status") == "success"}
    # A real run says each stage's advisories when that stage launches; only --check says them here.
    todo = [p for p in planned if p.stage.id not in done]
    commands = _check(spec, todo, repo_root=repo_root, outdir=outdir,
                      on_warning=on_warning if check_only else None, keep=check_only)
    if unparsable := [issue for p in todo for issue in _probe_config(spec, p)]:
        raise NfclawError(
            ErrorCode.ENVIRONMENT, "A stage could not start: Nextflow cannot parse its configuration.",
            fix=("Nothing was launched. Give that stage an engine its release parses — its "
                 "\"nxf_ver\" in the spec entry (see 'Nextflow too new for an older release' in "
                 f"{runlog.known_issues_path()}) — and run the chain again."),
            details={"issues": unparsable})
    if check_only:
        return ChainResult(outdir=outdir, outcome="checked", stages=[], commands=commands)
    return _execute(spec, planned, state, repo_root=repo_root, outdir=outdir,
                    timeout_seconds=timeout_seconds, on_warning=on_warning)


def _new_entry(p: Planned, outdir: Path) -> dict:
    return {"id": p.stage.id, "pipeline": p.stage.pipeline, "index": p.stage.index,
            "outdir": str(outdir / p.stage.dirname), "status": "pending",
            "fingerprint": fingerprint(p), "version": None, "commit": None, "handoff": None,
            "attempts": []}


def _execute(spec: ChainSpec, planned: list[Planned], state: dict | None, *, repo_root: Path,
             outdir: Path, timeout_seconds: int | None, on_warning) -> ChainResult:
    record = outdir / RECORD_DIRNAME
    outdir.mkdir(parents=True, exist_ok=True)
    with _lock(record, outdir):
        previous = {s.get("id"): s for s in (state or {}).get("stages", [])}
        stages = []
        for p in planned:
            old = previous.get(p.stage.id)
            if old and old.get("status") == "success":
                stages.append(old)                            # frozen (see _check_frozen)
            else:                                             # keep the attempt history
                stages.append({**_new_entry(p, outdir), "attempts": (old or {}).get("attempts", [])})
        state = {"chain_id": (state or {}).get("chain_id") or uuid.uuid4().hex,
                 "created": (state or {}).get("created") or runlog.now(),
                 "outcome": "running", "stages": stages}
        _write_json(record / "chain.json", normalized(spec, planned))
        _write_json(record / "state.json", state)
        log = runlog.RunLog(record / "logs" / LOG_NAME, label="chain")
        log.note(f"==> nfclaw chain started {runlog.now()}: {len(planned)} stages in {outdir}")
        print(f"nfclaw: logging this chain to {log.path}", file=sys.stderr, flush=True)
        deadline = None if timeout_seconds is None else time.monotonic() + timeout_seconds
        try:
            for i, p in enumerate(planned):
                entry = state["stages"][i]
                if entry["status"] == "success":
                    manifest = _read_json(Path(entry["outdir"]) / "provenance"
                                          / "run_manifest.json")
                    if not (isinstance(manifest, dict) and manifest.get("outcome") == "success"):
                        raise NfclawError(
                            ErrorCode.ENVIRONMENT,
                            f"stage '{p.stage.id}' is recorded as succeeded, but its provenance "
                            f"bundle no longer says so ({entry['outdir']})",
                            fix="Run the chain in a fresh --outdir.")
                    _say(log, f"{p.stage.dirname}: already succeeded — skipped")
                    continue
                _run_stage(p, planned[i - 1] if i else None, entry, state, spec=spec,
                           repo_root=repo_root, outdir=outdir, deadline=deadline,
                           budget=timeout_seconds, log=log, on_warning=on_warning)
            state["outcome"] = log.outcome = "success"
        except BaseException as exc:
            if state["outcome"] == "running":                 # not set by _run_stage: say why
                if isinstance(exc, (KeyboardInterrupt, execution.Terminated)):
                    state["outcome"] = execution.stop_outcome(exc)
                else:
                    reason = exc.message if isinstance(exc, NfclawError) else type(exc).__name__
                    state["outcome"] = f"failed ({reason})"
            log.fail(state["outcome"], str(exc) if isinstance(exc, NfclawError) else "")
            raise
        finally:
            state["updated"] = runlog.now()
            _write_json(record / "state.json", state)
            log.finish()
    return ChainResult(outdir=outdir, outcome=state["outcome"], stages=state["stages"],
                       log_path=log.path)


def _run_stage(p: Planned, prev: Planned | None, entry: dict, state: dict, *, spec: ChainSpec,
               repo_root: Path, outdir: Path, deadline: float | None, budget: int | None,
               log: runlog.RunLog, on_warning) -> None:
    stage, record = p.stage, outdir / RECORD_DIRNAME
    stage_dir = outdir / stage.dirname
    warn = _warner(on_warning, stage)
    overrides, input_path = dict(p.params), p.input
    link: dict[str, Any] = {"id": state["chain_id"], "record": str(record), "stage": stage.id,
                            "index": stage.index, "upstream": None}
    if prev is not None:
        dest = record / "handoffs" / stage.dirname
        _say(log, f"{stage.dirname}: preparing its input from {prev.stage.dirname} "
                  f"({p.rule.origin})")
        try:
            hand = handoff.materialize(p.rule, upstream_outdir=outdir / prev.stage.dirname,
                                       downstream_tree=p.tree.path, dest=dest)
        except NfclawError:
            entry["status"] = "failed"
            state["outcome"] = f"failed at stage {stage.dirname}: handoff"
            raise
        hand_path = _write_json(dest / "handoff.json",
                                {**hand.record, "from_stage": prev.stage.id, "to_stage": stage.id})
        entry["handoff"] = str(hand_path)
        for name, item in hand.record["params"].items():
            if dropped := item.get("dropped_rows"):
                _say(log, f"{stage.dirname}: {len(dropped)} row(s) of the {name} samplesheet "
                          f"{stage.pipeline} does not accept were dropped (recorded in "
                          f"{hand_path})")
        for name, value in hand.params.items():
            explicit = p.input if name == "input" else p.stage.params.get(name)
            if explicit not in (None, ""):
                if warn:
                    warn(f"--{name} is set by this stage itself; the value handed over from "
                         f"'{prev.stage.id}' ({value}) is not used")
            elif name == "input":
                input_path = value
            else:
                overrides[name] = value
        link["upstream"] = {"stage": prev.stage.id, "pipeline": prev.stage.pipeline,
                            "outdir": str(outdir / prev.stage.dirname), "handoff": str(hand_path),
                            "handoff_sha256": handoff.sha256_file(hand_path)}
    # A previous attempt of this stage left its run here: continue it with Nextflow's cache.
    resume = stage_dir.is_dir() and any(stage_dir.iterdir())
    attempt = 0
    while True:
        attempt += 1
        remaining = None if deadline is None else int(deadline - time.monotonic())
        if remaining is not None and remaining <= 0:
            entry["status"] = "failed"
            state["outcome"] = f"timed out after {budget} s"
            raise NfclawError(ErrorCode.EXECUTION_FAILED,
                              f"The chain's --timeout ran out before stage {stage.dirname}.",
                              fix="Resume the chain with --resume (and a larger --timeout).",
                              details={"timeout_seconds": budget})
        entry["status"] = "running"
        entry["attempts"].append({"started": runlog.now(), "resume": resume})
        _write_json(record / "state.json", state)
        _say(log, f"{stage.dirname}: {stage.pipeline} " + (f"attempt {attempt} " if attempt > 1
                                                           else "") + "started — log "
                  f"{stage_dir / 'provenance' / 'logs' / runlog.RUN_LOG_NAME}")
        opts = options(spec, stage)
        try:
            orchestration.run_pipeline(
                stage.pipeline, repo_root=repo_root, input_path=input_path, outdir=stage_dir,
                profile=opts.profile, params_file=stage.params_file, cli_overrides=overrides,
                resume=resume, demo=stage.demo, check_only=False, write_provenance=True,
                timeout_seconds=remaining, pipeline_version=stage.pipeline_version,
                nxf_ver=opts.nxf_ver, nxf_env=opts.nxf_env, allow_spaces=spec.allow_spaces,
                configs=opts.configs, limits=opts.limits, on_warning=warn, chain_link=link)
        except NfclawError as exc:
            entry["attempts"][-1].update(finished=runlog.now(), outcome=_short(exc))
            if _retryable(exc) and attempt <= stage.retries:
                _say(log, f"{stage.dirname}: attempt {attempt} {_short(exc)}; retrying with "
                          f"-resume ({attempt}/{stage.retries})")
                resume = True
                continue
            entry["status"] = "failed"
            state["outcome"] = (f"timed out after {budget} s" if "timeout_seconds" in exc.details
                                else f"failed at stage {stage.dirname}: {_short(exc)}")
            raise
        except (KeyboardInterrupt, execution.Terminated) as exc:
            entry["attempts"][-1].update(finished=runlog.now(),
                                         outcome=execution.stop_outcome(exc))
            entry["status"] = "stopped"
            state["outcome"] = f"{execution.stop_outcome(exc)} (stage {stage.dirname})"
            raise
        break
    manifest = _read_json(stage_dir / "provenance" / "run_manifest.json") or {}
    entry["attempts"][-1].update(finished=runlog.now(), outcome="success")
    entry.update(status="success", version=manifest.get("version"), commit=manifest.get("commit"))
    _write_json(record / "state.json", state)
    _say(log, f"{stage.dirname}: success ({stage.pipeline} {manifest.get('version') or ''})".rstrip())


# --- lineage: reconstructing and verifying a chain from disk -----------------------------------

def _record_for(path: Path) -> Path:
    if (path / RECORD_DIRNAME / "state.json").is_file():
        return path / RECORD_DIRNAME
    manifest = _read_json(path / "provenance" / "run_manifest.json") or {}
    record = (manifest.get("chain") or {}).get("record") if isinstance(manifest, dict) else None
    if record and (Path(record) / "state.json").is_file():
        return Path(record)
    raise NfclawError(ErrorCode.ENVIRONMENT, f"no chain recorded in or for {path}",
                      fix="Pass a chain's --outdir, or the outdir of one of its stages.")


def _digests(path: Path) -> dict[str, str]:
    """`hash  name` lines (outputs.sha256 names are relative, inputs.sha256 absolute) as
    {name: hash}."""
    out: dict[str, str] = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            digest, _, name = line.partition("  ")
            if digest and name:
                out[name] = digest
    except OSError:
        pass
    return out


def _sha(path: Path) -> str | None:
    try:
        return handoff.sha256_file(path)
    except OSError:
        return None


def status(path: Path) -> tuple[dict, list[str]]:
    """The chain recorded at (or for) `path`, and every broken link in it.

    A link holds when the downstream ran with exactly the recorded handoff (its manifest names the
    handoff's hash), the snapshot is unchanged and is the input the downstream hashed, and every
    upstream file the handoff drew on is what the upstream run recorded producing."""
    record = _record_for(path.expanduser().resolve())
    state = _read_json(record / "state.json") or {}
    problems: list[str] = []
    for entry in state.get("stages", []):
        if not entry.get("handoff"):
            continue
        sid, hand_path = entry["id"], Path(entry["handoff"])
        rec = _read_json(hand_path)
        if not isinstance(rec, dict):
            problems.append(f"{sid}: its handoff record is missing or unreadable ({hand_path})")
            continue
        down = Path(entry["outdir"])
        succeeded = entry.get("status") == "success"
        manifest = _read_json(down / "provenance" / "run_manifest.json") or {}
        link = ((manifest.get("chain") or {}).get("upstream") or {}) if isinstance(manifest, dict) \
            else {}
        if succeeded and link.get("handoff_sha256") != _sha(hand_path):
            problems.append(f"{sid}: the handoff record is not the one this stage ran with")
        up_out = _digests(Path((rec.get("upstream") or {}).get("outdir", "")) / "provenance"
                          / "outputs.sha256")
        down_in = _digests(down / "provenance" / "inputs.sha256")
        for name, item in (rec.get("params") or {}).items():
            if "sha256" in item:
                if _sha(Path(item["value"])) != item["sha256"]:
                    problems.append(f"{sid}: --{name} snapshot {item['value']} changed since the "
                                    "handoff")
                if name == "input" and succeeded and down_in.get(item["value"]) != item["sha256"]:
                    problems.append(f"{sid}: --input is not the snapshot this stage hashed")
            for rel, digest in (item.get("derived_from") or {}).items():
                if digest is not None and up_out.get(rel) != digest:
                    problems.append(f"{sid}: --{name}: {rel} is not what the upstream run "
                                    "produced")
    return state, problems


def format_status(state: dict, problems: list[str]) -> str:
    lines = [f"chain {state.get('chain_id', '?')}: {state.get('outcome', '?')}"]
    stages = state.get("stages", [])
    for i, s in enumerate(stages):
        ver = f"{s.get('version') or '?'} ({(s.get('commit') or '')[:12]})"
        lines.append(f"  {s['index']:02d}-{s['id']:<18} {s['pipeline']} {ver}  {s['status']}  "
                     f"{s['outdir']}")
        if s.get("handoff") and i:
            prev = stages[i - 1]
            lines.append(f"      input ← {prev['index']:02d}-{prev['id']}  ({s['handoff']})")
    lines += ["", "lineage: verified" if not problems else "lineage: BROKEN"]
    lines += [f"  - {p}" for p in problems]
    return "\n".join(lines) + "\n"
