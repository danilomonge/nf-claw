"""The run log: one complete, fixed-place record of every launch, and the facts a failure needs.

`nfclaw run` launches Nextflow from `--outdir`, so everything a reader needs after the fact sits at
paths that do not depend on where they are standing:

- `<outdir>/provenance/logs/run.log` — the whole launch as it appeared on the terminal: nfclaw's
  header (command, launch dir, Nextflow log, advisories), Nextflow's stdout and stderr interleaved as
  produced, and a last line stating the outcome. A relaunch (`--resume`) appends, so the attempt that
  failed is never overwritten by the one that fixes it.
- Nextflow's own log — `<outdir>/.nextflow.log` (or `NXF_LOG_FILE`, resolved against `--outdir`).

Nothing here guesses a cause. On failure nfclaw quotes Nextflow's own error report verbatim and names
the files that hold the rest; the reader (or agent) does the diagnosis.
"""
from __future__ import annotations

import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

RUN_LOG_NAME = "run.log"

# The tail of a launch's console kept in memory for quoting its error. Nextflow ends a failed run
# with its error report, so the tail always holds it; a bound keeps a days-long run cheap.
_TAIL_BYTES = 256 * 1024
_MAX_EXCERPT_LINES = 40
_CONTEXT_LINES = 6           # non-blank lines quoted from just above the `ERROR ~` line
_TAIL_LINES = 15             # quoted when Nextflow printed no `ERROR ~` line at all

_ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b[@-_]")
# Lines that end the context above `ERROR ~`: Nextflow's banner and launch line, and the last line of
# an earlier report (26.x prints the report twice when stdout is not a terminal).
_CONTEXT_STOP = re.compile(r"N E X T F L O W|^Launching `|^\s*-- Check ")


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


def error_excerpt(console: str) -> list[str]:
    """Nextflow's own error report from a launch's console output, quoted verbatim.

    Deterministic: from the last `ERROR ~` line (Nextflow's error prefix) to the end, with the few
    lines Nextflow prints just above it — a config or script syntax error is described there, above
    `ERROR ~ Config parsing failed`. Without an `ERROR ~` line (an `error "…"` raised in a workflow
    prints only its message) it is the last lines of the console. A long report keeps its head
    (`Caused by`) and its tail (`Command error`, `Work dir`)."""
    lines = _clean(console)
    marks = [i for i, line in enumerate(lines) if line.startswith("ERROR ~")]
    if marks:
        start = marks[-1]
        seen = 0
        while start > 0 and seen < _CONTEXT_LINES:
            prev = lines[start - 1]
            if _CONTEXT_STOP.search(prev):
                break
            start -= 1
            seen += bool(prev)
        block = _squeeze(lines[start:])
    else:
        block = [line for line in lines if line][-_TAIL_LINES:]
    if len(block) > _MAX_EXCERPT_LINES:
        head, tail = 12, _MAX_EXCERPT_LINES - 13
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


class RunLog:
    """`run.log` for one launch: appended to (never truncated) and safe to write from both of the
    child's stream readers at once. Keeps the tail of this launch's console for quoting its error."""

    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = path.open("ab")
        self._lock = threading.Lock()
        self._tail = bytearray()

    def note(self, text: str) -> None:
        """A line of nfclaw's own (header, outcome) — not part of the console tail."""
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

    def finish(self, outcome: str, error: str = "") -> None:
        """Close the record of this launch: the error text (if any), then one last line — always the
        file's final line once the run ends — `==> nfclaw run finished <time>: <outcome>`."""
        if error:
            self.note(error)
        self.note(f"==> nfclaw run finished {now()}: {outcome}")
        try:
            self._fh.close()
        except OSError:
            pass
