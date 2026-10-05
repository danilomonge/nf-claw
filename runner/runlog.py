"""The run log: one complete, fixed-place record of every launch, and the facts a failure needs.

`nfclaw run` launches Nextflow from `--outdir`, so everything a reader needs after the fact sits at
paths that do not depend on where they are standing:

- `<outdir>/provenance/logs/run.log` — the whole launch as it appeared on the terminal: nfclaw's
  header (command, launch dir, Nextflow log, advisories), Nextflow's stdout and stderr interleaved as
  produced, and a last line stating the outcome. A relaunch (`--resume`) appends, so the attempt that
  failed is never overwritten by the one that fixes it.
- Nextflow's own log — `<outdir>/.nextflow.log` (or `NXF_LOG_FILE`, resolved against `--outdir`).

Nothing here guesses a cause. On failure nfclaw quotes Nextflow's own error report verbatim — plus
the exception chain behind it from Nextflow's log, where the real reason is often the only thing
written — and names the files that hold the rest; the reader (or agent) does the diagnosis.
"""
from __future__ import annotations

import os
import re
import shlex
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

RUN_LOG_NAME = "run.log"

# The tail of a launch's console kept in memory for quoting its error. Nextflow ends a failed run
# with its error report, so the tail always holds it; a bound keeps a days-long run cheap.
_TAIL_BYTES = 256 * 1024
_MAX_EXCERPT_LINES = 50
_CONTEXT_LINES = 6           # non-blank lines quoted from just above the `ERROR ~` line
_TAIL_LINES = 15             # quoted when Nextflow printed no `ERROR ~` line at all

# `.nextflow.log` entries: "Oct-05 21:57:35.089 [main] ERROR nextflow.cli.Launcher - …".
_LOG_ENTRY = re.compile(r"^[A-Z][a-z]{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} \[[^\]]*\] ")
_LOG_ERROR = re.compile(r"^[A-Z][a-z]{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} \[[^\]]*\] ERROR ")
_LOG_TAIL_BYTES = 2 * 1024 * 1024
_MAX_CAUSES = 8
_MAX_CAUSE_LINES = 6         # continuation lines kept per cause message
_STACK_FRAME = re.compile(r"^\s+(at |\.\.\. \d+ (common frames omitted|more))")

_ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b[@-_]")
# Lines that end the context above `ERROR ~`: Nextflow's banner and launch line, and the end (or
# start) of an earlier report — Nextflow re-renders a report when stdout is not a terminal.
_CONTEXT_STOP = re.compile(r"N E X T F L O W|^Launching `|^\s*-- Check |^ERROR ~")
_REPORT_END = re.compile(r"^\s*-- Check ")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def nextflow_log_path(launch_dir: Path, env_extra: dict[str, str] | None = None) -> Path:
    """Where Nextflow writes its own log for a run launched from `launch_dir`.

    `.nextflow.log` in the launch directory unless `NXF_LOG_FILE` names another file (the overlay
    wins over the shell, as it does at launch); a relative name resolves against the launch directory
    because that is Nextflow's cwd. Nextflow's console only ever says "Check '.nextflow.log'" —
    relative to a directory the reader is usually not in."""
    raw = (env_extra or {}).get("NXF_LOG_FILE") or os.environ.get("NXF_LOG_FILE")
    path = Path(raw) if raw else Path(".nextflow.log")
    return path if path.is_absolute() else launch_dir / path


def known_issues_path() -> str:
    """The symptom→fix map, as an absolute path when the repository is present (it is for the
    documented `pip install -e .`), so the pointer works from any working directory."""
    doc = Path(__file__).resolve().parent.parent / "docs" / "known-issues.md"
    return str(doc) if doc.is_file() else "docs/known-issues.md"


def _clean(text: str) -> list[str]:
    """Console text as a terminal would show it: no colour/cursor sequences, and a line redrawn with
    carriage returns reduced to its final state."""
    lines = []
    for raw in text.split("\n"):
        line = raw.rstrip("\r").rsplit("\r", 1)[-1]
        lines.append(_ANSI.sub("", line).rstrip())
    return lines


def _squeeze(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        if line or (out and out[-1]):                     # collapse runs of blank lines
            out.append(line)
    while out and not out[-1]:
        out.pop()
    while out and not out[0]:
        out.pop(0)
    return out


def _reports(lines: list[str]) -> list[tuple[int, tuple[str, ...]]]:
    """Each `ERROR ~` report in the console as (start index, lines): from its `ERROR ~` line through
    Nextflow's closing "-- Check '.nextflow.log' file for details" (or up to the next report)."""
    reports = []
    i = 0
    while i < len(lines):
        if not lines[i].startswith("ERROR ~"):
            i += 1
            continue
        j = i + 1
        while j < len(lines) and not lines[j].startswith("ERROR ~"):
            j += 1
            if _REPORT_END.match(lines[j - 1]):
                break
        reports.append((i, tuple(_squeeze(lines[i:j]))))
        i = j
    return reports


def error_excerpt(console: str) -> list[str]:
    """Nextflow's own error reports from a launch's console output, quoted verbatim.

    Deterministic: every distinct `ERROR ~` report (Nextflow's error prefix), once each, in the order
    they first appear — Nextflow re-renders the same report when stdout is not a terminal, and the
    nf-core template follows the real one with a generic "ERROR ~ Pipeline failed" — preceded by the
    few lines printed just above the last rendering of the first: the failed step's progress line, or
    a config/script syntax error described above `ERROR ~ Config parsing failed`. Without an
    `ERROR ~` line (an `error "…"` raised in a workflow prints only its message) it is the last lines
    of the console. A long excerpt keeps its head (`Caused by`) and its tail (`Command error`,
    `Work dir`)."""
    lines = _clean(console)
    distinct: dict[tuple[str, ...], int] = {}             # report → start of its last rendering
    for at, report in _reports(lines):
        distinct[report] = at                            # insertion order = first appearance
    if distinct:
        first, start = next(iter(distinct.items()))
        seen = 0
        while start > 0 and seen < _CONTEXT_LINES:
            prev = lines[start - 1]
            if _CONTEXT_STOP.search(prev):
                break
            start -= 1
            seen += bool(prev)
        block = _squeeze(lines[start:distinct[first]])
        for report in distinct:
            block += ([""] if block else []) + list(report)
    else:
        block = [line for line in lines if line][-_TAIL_LINES:]
    if len(block) > _MAX_EXCERPT_LINES:
        head, tail = 15, _MAX_EXCERPT_LINES - 16
        omitted = len(block) - head - tail
        block = block[:head] + [f"… {omitted} lines omitted (full report in the run log) …"] + \
            block[-tail:]
    return block


def failing_task_dir(excerpt: list[str]) -> Path | None:
    """The work directory of the task that failed, as Nextflow's report names it (`Work dir:` and the
    path on the next line). Its `.command.err`/`.command.log` hold the tool's complete output."""
    for i, line in enumerate(excerpt):
        if line.strip() == "Work dir:":
            for nxt in excerpt[i + 1:]:
                if nxt.strip():
                    path = nxt.strip()
                    return Path(path) if path.startswith("/") else None
    return None


def nextflow_log_causes(log: Path) -> list[str]:
    """The exception chain behind Nextflow's last error, from its own log: the `Caused by: …` lines
    of the last ERROR entry, each with the rest of its message when it spans several lines. Deterministic, and often the only place the real reason is written —
    the console says "Unable to parse config file" while the log says "Network is unreachable".
    Empty when the entry carries no chain (a failed task's entry just repeats the console report)."""
    try:
        with log.open("rb") as fh:
            fh.seek(0, os.SEEK_END)
            fh.seek(max(0, fh.tell() - _LOG_TAIL_BYTES))
            lines = fh.read().decode("utf-8", errors="replace").splitlines()
    except OSError:
        return []
    errors = [i for i, line in enumerate(lines) if _LOG_ERROR.match(line)]
    if not errors:
        return []
    causes: list[list[str]] = []
    current: list[str] | None = None                     # the cause whose message is being read
    for line in lines[errors[-1] + 1:]:
        if _LOG_ENTRY.match(line):
            break                                        # the next entry: the error's chain is over
        if line.startswith("Caused by: ") and line[len("Caused by: "):].strip():
            current = [line.rstrip()]
            causes.append(current)
        elif _STACK_FRAME.match(line):
            current = None                               # the message ends where the frames begin
        elif current is not None and line.strip() and len(current) <= _MAX_CAUSE_LINES:
            current.append("  " + line.rstrip())         # a message that spans several lines
    distinct: list[list[str]] = []
    for cause in causes:
        if cause not in distinct:
            distinct.append(cause)
    return [line for cause in distinct[:_MAX_CAUSES] for line in cause]


class RunLog:
    """`run.log` for one launch: appended to (never truncated) and safe to write from both of the
    child's stream readers at once. Keeps the tail of this launch's console for quoting its error.

    Whoever opens it closes it with `finish()`, once nfclaw is done with the run — after the
    provenance bundle is written — so the final line never announces an outcome early."""

    def __init__(self, path: Path, *, nextflow_log: Path | None = None):
        self.path = path
        self.nextflow_log = nextflow_log
        self.outcome = "failed"                          # until the run says otherwise
        path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = path.open("ab")
        self._lock = threading.Lock()
        self._tail = bytearray()
        self._finished = False

    @classmethod
    def open(cls, logs_dir: Path, *, command: list[str], launch_dir: Path,
             nextflow_log: Path | None = None, notes: list[str] | tuple[str, ...] = ()) -> "RunLog":
        """Start the record of a launch: its header, and one line on the terminal saying where it
        is — before anything else prints, since a long run's own output soon buries it."""
        log = cls(logs_dir / RUN_LOG_NAME, nextflow_log=nextflow_log)
        log.note(f"==> nfclaw run started {now()}")
        log.note(f"    command: {shlex.join(command)}")
        log.note(f"    launch dir: {launch_dir}")
        if nextflow_log is not None:
            log.note(f"    nextflow log: {nextflow_log}")
        for note in notes:
            log.note(f"    warning: {note}")
        print(f"nfclaw: logging this run to {log.path}", file=sys.stderr, flush=True)
        return log

    def note(self, text: str) -> None:
        """A line of nfclaw's own (header, error, outcome) — not part of the console tail."""
        self._write((text.rstrip("\n") + "\n").encode("utf-8"), console=False)

    def write(self, chunk: bytes) -> None:
        """Bytes of the child's console, verbatim."""
        self._write(chunk, console=True)

    def _write(self, data: bytes, *, console: bool) -> None:
        with self._lock:
            if console:
                self._tail += data
                del self._tail[:-_TAIL_BYTES]
            try:
                self._fh.write(data)
                self._fh.flush()
            except (OSError, ValueError):
                pass                                     # a full disk must not kill the run itself

    def console_tail(self) -> str:
        with self._lock:
            return self._tail.decode("utf-8", errors="replace")

    def fail(self, outcome: str, error: str = "") -> None:
        """Record how the run failed: the error text now, the outcome for the final line."""
        self.outcome = outcome
        if error:
            self.note(error)

    def finish(self) -> None:
        """Close the record with its last line — `==> nfclaw run finished <time>: <outcome>`."""
        if self._finished:
            return
        self._finished = True
        self.note(f"==> nfclaw run finished {now()}: {self.outcome}")
        try:
            self._fh.close()
        except OSError:
            pass
