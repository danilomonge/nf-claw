from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path

from runner.errors import ErrorCode, NfclawError


@dataclass(frozen=True)
class ExecResult:
    exit_code: int
    stdout_path: Path
    stderr_path: Path


def _tee(src, term_stream, log_file) -> None:
    """Forward a child stream to the terminal and the log file at once, live.

    Reads whatever is already available (`read1`) instead of waiting for a full buffer or a whole
    line, so a long pipeline's progress reaches the terminal as Nextflow produces it rather than only
    when the run ends. Bytes are copied verbatim to preserve the child's own formatting (carriage
    returns, colour). The terminal and the log file are written independently: a closed or unusable
    terminal never costs the run its captured log, which the provenance bundle and error messages
    point at.
    """
    term = getattr(term_stream, "buffer", None)          # write bytes; None if not a real byte sink
    try:
        for chunk in iter(lambda: src.read1(65536), b""):
            try:
                log_file.write(chunk)
                log_file.flush()
            except (OSError, ValueError):
                pass
            if term is not None:
                try:
                    term.write(chunk)
                    term.flush()
                except (OSError, ValueError):
                    term = None                          # stop writing to a broken terminal
    finally:
        try:
            src.close()
        except OSError:
            pass


def _join(threads: list[threading.Thread]) -> None:
    for t in threads:
        t.join(timeout=5)


def run(command: list[str], *, cwd: Path, logs_dir: Path,
        timeout_seconds: int, env_extra: dict[str, str] | None = None) -> ExecResult:
    logs_dir.mkdir(parents=True, exist_ok=True)
    out_p, err_p = logs_dir / "stdout.txt", logs_dir / "stderr.txt"
    # start_new_session puts the child in its own process group, so nfclaw owns its shutdown: the
    # terminal's Ctrl-C reaches nfclaw as a KeyboardInterrupt (not the child), and nfclaw then tears
    # down the whole group below. Without this the child kept running in the background after Ctrl-C.
    popen_kwargs = {} if sys.platform == "win32" else {"start_new_session": True}
    # Inherit the full environment, then overlay the caller's NXF_* overrides (engine version,
    # JVM args, …). Inheriting keeps shell-set vars (proxies, JAVA_HOME) working as before.
    env = {**os.environ, **env_extra} if env_extra else None
    with out_p.open("wb") as out_fh, err_p.open("wb") as err_fh:
        try:
            # Pipe the child's streams so nfclaw can tee them; without a pipe the output would go
            # straight to files (the terminal stays mute) or straight to the terminal (nothing is
            # captured). Teeing gives both.
            proc = subprocess.Popen(command, cwd=str(cwd), stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env, **popen_kwargs)
        except OSError as exc:
            raise NfclawError(ErrorCode.EXECUTION_FAILED,
                              f"Could not launch process: {exc}",
                              fix="Ensure `nextflow` is installed and on PATH.") from exc
        # One drainer per stream: both pipes must be read concurrently, or a child that fills one
        # while nfclaw is blocked reading the other would deadlock. Daemon threads so a wedged reader
        # can never keep the process alive on its own.
        readers = [
            threading.Thread(target=_tee, args=(proc.stdout, sys.stdout, out_fh), daemon=True),
            threading.Thread(target=_tee, args=(proc.stderr, sys.stderr, err_fh), daemon=True),
        ]
        for t in readers:
            t.start()
        try:
            code = proc.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            _terminate(proc)
            _join(readers)
            raise NfclawError(ErrorCode.EXECUTION_FAILED, "Execution timed out.",
                              fix="Increase --timeout or use a smaller dataset.",
                              details={"timeout_seconds": timeout_seconds}) from exc
        except BaseException:
            # Ctrl-C (KeyboardInterrupt) or any other interruption of the wait: tear down the child
            # group so Nextflow — and every task process, container or JVM it launched — is stopped,
            # never left running in the background. Then re-raise so the interrupt is not swallowed.
            _terminate(proc)
            _join(readers)
            raise
        _join(readers)
    if code != 0:
        raise NfclawError(ErrorCode.EXECUTION_FAILED, "Nextflow execution failed.",
                          fix=f"Inspect the log: {err_p}. Common causes and fixes: "
                              "docs/known-issues.md.",
                          details={"exit_code": code})
    return ExecResult(code, out_p, err_p)


def _terminate(proc: subprocess.Popen) -> None:
    """Stop the child and everything it launched.

    Signals the whole process group (SIGTERM first, so Nextflow runs its JVM shutdown hooks and
    cleans up its own tasks; SIGKILL only if it does not exit), because killing just the child would
    orphan the task processes it spawned.
    """
    if hasattr(os, "killpg"):
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(os.getpgid(proc.pid), sig)
                proc.wait(timeout=10)
                return
            except (OSError, ProcessLookupError, subprocess.TimeoutExpired):
                continue
    proc.kill()
