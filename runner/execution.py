from __future__ import annotations

import os
import shlex
import signal
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path

from runner import runlog
from runner.errors import ErrorCode, NfclawError


@dataclass(frozen=True)
class ExecResult:
    exit_code: int
    stdout_path: Path
    stderr_path: Path


def _tee(src, term_stream, log_file, run_log: runlog.RunLog) -> None:
    """Forward a child stream to the terminal, its own log file and the run log at once, live.

    Reads whatever is already available (`read1`) instead of waiting for a full buffer or a whole
    line, so a long pipeline's progress reaches the terminal as Nextflow produces it rather than only
    when the run ends. Bytes are copied verbatim to preserve the child's own formatting (carriage
    returns, colour). The terminal and the files are written independently: a closed or unusable
    terminal never costs the run its captured logs, which the provenance bundle and error messages
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
            run_log.write(chunk)
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
        timeout_seconds: int | None, env_extra: dict[str, str] | None = None,
        nextflow_log: Path | None = None, notes: list[str] | tuple[str, ...] = ()) -> ExecResult:
    """Run `command` from `cwd`, streaming its output live and recording it under `logs_dir`.

    `stdout.txt`/`stderr.txt` keep the child's two streams; `run.log` keeps the whole launch in order
    with nfclaw's header and a final outcome line (see `runner.runlog`). All three are appended to, so
    a relaunch (`--resume`) never overwrites the attempt that failed. `nextflow_log` is where Nextflow
    writes its own log for this launch; `notes` are advisories recorded in the run log's header."""
    logs_dir.mkdir(parents=True, exist_ok=True)
    out_p, err_p = logs_dir / "stdout.txt", logs_dir / "stderr.txt"
    run_log = runlog.RunLog(logs_dir / runlog.RUN_LOG_NAME)
    run_log.note(f"==> nfclaw run started {runlog.now()}")
    run_log.note(f"    command: {shlex.join(command)}")
    run_log.note(f"    launch dir: {cwd}")
    if nextflow_log is not None:
        run_log.note(f"    nextflow log: {nextflow_log}")
    for note in notes:
        run_log.note(f"    warning: {note}")
    # Say where the record is before anything else prints: a long run's own output soon buries it.
    print(f"nfclaw: logging this run to {run_log.path}", file=sys.stderr, flush=True)
    # start_new_session puts the child in its own process group, so nfclaw owns its shutdown: the
    # terminal's Ctrl-C reaches nfclaw as a KeyboardInterrupt (not the child), and nfclaw then tears
    # down the whole group below. Without this the child kept running in the background after Ctrl-C.
    popen_kwargs = {} if sys.platform == "win32" else {"start_new_session": True}
    # Inherit the full environment, then overlay the caller's NXF_* overrides (engine version,
    # JVM args, …). Inheriting keeps shell-set vars (proxies, JAVA_HOME) working as before.
    env = {**os.environ, **env_extra} if env_extra else None
    with out_p.open("ab") as out_fh, err_p.open("ab") as err_fh:
        try:
            # Pipe the child's streams so nfclaw can tee them; without a pipe the output would go
            # straight to files (the terminal stays mute) or straight to the terminal (nothing is
            # captured). Teeing gives both.
            proc = subprocess.Popen(command, cwd=str(cwd), stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env, **popen_kwargs)
        except OSError as exc:
            err = NfclawError(ErrorCode.EXECUTION_FAILED, f"Could not launch process: {exc}",
                              fix="Ensure `nextflow` is installed and on PATH.",
                              details={"run_log": str(run_log.path)})
            run_log.finish("could not launch", str(err))
            raise err from exc
        # One drainer per stream: both pipes must be read concurrently, or a child that fills one
        # while nfclaw is blocked reading the other would deadlock. Daemon threads so a wedged reader
        # can never keep the process alive on its own.
        readers = [
            threading.Thread(target=_tee, args=(proc.stdout, sys.stdout, out_fh, run_log),
                             daemon=True),
            threading.Thread(target=_tee, args=(proc.stderr, sys.stderr, err_fh, run_log),
                             daemon=True),
        ]
        for t in readers:
            t.start()
        try:
            code = proc.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            _terminate(proc)
            _join(readers)
            err = NfclawError(ErrorCode.EXECUTION_FAILED, "Execution timed out.",
                              fix="Increase --timeout or use a smaller dataset; the run log shows "
                                  "how far the run got.",
                              details={"timeout_seconds": timeout_seconds,
                                       **_log_details(run_log, nextflow_log)})
            run_log.finish(f"timed out after {timeout_seconds} s", str(err))
            raise err from exc
        except BaseException:
            # Ctrl-C (KeyboardInterrupt) or any other interruption of the wait: tear down the child
            # group so Nextflow — and every task process, container or JVM it launched — is stopped,
            # never left running in the background. Then re-raise so the interrupt is not swallowed.
            _terminate(proc)
            _join(readers)
            run_log.finish("interrupted")
            raise
        _join(readers)
    if code != 0:
        err = _failure(code, run_log, nextflow_log)
        run_log.finish(f"failed (exit status {code})", str(err))
        raise err
    run_log.finish("success")
    return ExecResult(code, out_p, err_p)


def _log_details(run_log: runlog.RunLog, nextflow_log: Path | None) -> dict[str, str]:
    """The files that hold the rest of the story, as absolute paths — only ones that exist."""
    details = {"run_log": str(run_log.path)}
    if nextflow_log is not None and nextflow_log.is_file():
        details["nextflow_log"] = str(nextflow_log)
    return details


def _failure(code: int, run_log: runlog.RunLog, nextflow_log: Path | None) -> NfclawError:
    """The error for a launch that exited non-zero: Nextflow's own report, quoted from this launch's
    console, plus where the full logs are. Nextflow prints that report on stdout — stderr only carries
    the launcher's chatter — and refers to its log relative to a directory the reader is not in."""
    excerpt = runlog.error_excerpt(run_log.console_tail())
    details: dict = {"exit_code": code, **_log_details(run_log, nextflow_log)}
    task = runlog.failing_task_dir(excerpt)
    if task is not None and task.is_dir():
        details["failing_task"] = str(task / ".command.err")
    message = f"Nextflow execution failed (exit status {code})."
    if excerpt:
        message += " Nextflow reported:\n" + "\n".join(f"    {line}" if line else ""
                                                         for line in excerpt)
    task_hint = (" The failing task's complete output is in .command.err and .command.log beside "
                 "`failing_task`." if "failing_task" in details else "")
    return NfclawError(
        ErrorCode.EXECUTION_FAILED, message,
        fix=(f"Fix the cause Nextflow reports, then re-run the same command with --resume."
             f"{task_hint} The whole launch is in `run_log`. Common causes and fixes: "
             f"{runlog.known_issues_path()}."),
        details=details)


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
