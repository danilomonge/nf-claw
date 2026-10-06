from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runner import runlog
from runner.errors import ErrorCode, NfclawError


@dataclass(frozen=True)
class ExecResult:
    exit_code: int
    stdout_path: Path
    stderr_path: Path


def _tee(src, term_stream, log_file, run_log: runlog.RunLog, stream: str) -> None:
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
            run_log.write(chunk, stream)
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
        nextflow_log: Path | None = None, notes: list[str] | tuple[str, ...] = (),
        run_log: runlog.RunLog | None = None) -> ExecResult:
    """Run `command` from `cwd`, streaming its output live and recording it under `logs_dir`.

    `stdout.txt`/`stderr.txt` keep the child's two streams; `run.log` keeps the whole launch in order
    (see `runner.runlog`). All three are appended to, so a relaunch (`--resume`) never overwrites the
    attempt that failed. A caller that does more work after the launch (`nfclaw run` writes the
    provenance bundle) passes its own open `run_log` and finishes it itself; otherwise one is opened
    here — with `nextflow_log` and the `notes` advisories in its header — and finished on return."""
    own = run_log is None
    if run_log is None:
        run_log = runlog.RunLog.open(logs_dir, command=command, launch_dir=cwd,
                                     nextflow_log=nextflow_log, notes=notes, env=env_extra)
    try:
        return _run(command, cwd=cwd, logs_dir=logs_dir, timeout_seconds=timeout_seconds,
                    env_extra=env_extra, run_log=run_log)
    finally:
        if own:
            run_log.finish()


def _run(command: list[str], *, cwd: Path, logs_dir: Path, timeout_seconds: int | None,
         env_extra: dict[str, str] | None, run_log: runlog.RunLog) -> ExecResult:
    logs_dir.mkdir(parents=True, exist_ok=True)
    out_p, err_p = logs_dir / "stdout.txt", logs_dir / "stderr.txt"
    # start_new_session puts the child in its own process group, so nfclaw owns its shutdown: the
    # terminal's Ctrl-C reaches nfclaw as a KeyboardInterrupt (not the child), and nfclaw then tears
    # down the whole group below. Without this the child kept running in the background after Ctrl-C.
    popen_kwargs: dict[str, Any] = {} if sys.platform == "win32" else {"start_new_session": True}
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
            run_log.fail("could not launch", str(err))
            raise err from exc
        # One drainer per stream: both pipes must be read concurrently, or a child that fills one
        # while nfclaw is blocked reading the other would deadlock. Daemon threads so a wedged reader
        # can never keep the process alive on its own.
        readers = [
            threading.Thread(target=_tee, args=(proc.stdout, sys.stdout, out_fh, run_log, "out"),
                             daemon=True),
            threading.Thread(target=_tee, args=(proc.stderr, sys.stderr, err_fh, run_log, "err"),
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
                                       **_log_details(run_log)})
            run_log.fail(f"timed out after {timeout_seconds} s", str(err))
            raise err from exc
        except BaseException:
            # Ctrl-C (KeyboardInterrupt) or any other interruption of the wait: tear down the child
            # group so Nextflow — and every task process, container or JVM it launched — is stopped,
            # never left running in the background. Then re-raise so the interrupt is not swallowed.
            _terminate(proc)
            _join(readers)
            run_log.fail("interrupted")
            raise
        _join(readers)
    if code != 0:
        err = _failure(code, run_log)
        run_log.fail(f"failed (exit status {code})", str(err))
        raise err
    run_log.outcome = "success"
    return ExecResult(code, out_p, err_p)


def _log_details(run_log: runlog.RunLog) -> dict[str, str]:
    """The files that hold the rest of the story, as absolute paths — only ones that exist."""
    details = {"run_log": str(run_log.path)}
    if run_log.nextflow_log is not None and run_log.nextflow_log.is_file():
        details["nextflow_log"] = str(run_log.nextflow_log)
    return details


def _failure(code: int, run_log: runlog.RunLog) -> NfclawError:
    """The error for a launch that exited non-zero: what Nextflow itself reported, quoted from this
    launch's console, plus where the full logs are. Nextflow prints its error reports on stdout and
    some details on stderr (nf-schema's list of invalid values), and refers to its log relative to a
    directory the reader is not in."""
    on_stderr = runlog.stderr_excerpt(run_log.console_tail("err"))
    # Without an `ERROR ~` report on stdout its tail is only worth quoting when stderr is silent too
    # (an `error "…"` in a workflow prints just its message there); otherwise it is the banner.
    on_stdout = runlog.error_excerpt(run_log.console_tail("out"),
                                     tail_if_no_report=not on_stderr)
    details: dict = {"exit_code": code, **_log_details(run_log)}
    task = runlog.failing_task_dir(on_stdout + on_stderr)
    if task is not None and task.is_dir():
        details["failing_task"] = str(task / ".command.err")
    message = f"Nextflow execution failed (exit status {code})."
    if on_stdout:
        message += " Nextflow reported:\n" + _quote(on_stdout)
    if on_stderr:
        message += ("\n  and on stderr:\n" if on_stdout else " Nextflow reported on stderr:\n") + \
            _quote(on_stderr)
    causes = (runlog.nextflow_log_causes(run_log.nextflow_log)
              if "nextflow_log" in details and run_log.nextflow_log is not None else [])
    if causes:
        message += "\n  The underlying cause, from the Nextflow log:\n" + _quote(causes)
    task_hint = (" The failing task's complete output is in .command.err and .command.log beside "
                 "`failing_task`." if "failing_task" in details else "")
    return NfclawError(
        ErrorCode.EXECUTION_FAILED, message,
        fix=(f"Fix the cause Nextflow reports, then re-run the same command with --resume."
             f"{task_hint} The whole launch is in `run_log`. Common causes and fixes: "
             f"{runlog.known_issues_path()}."),
        details=details)


def _quote(lines: list[str]) -> str:
    return "\n".join(f"    {line}" if line else "" for line in lines)


_GRACE_SECONDS = 10


def _group_alive(pgid: int) -> bool:
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except OSError:                       # members exist that we may not signal: still not gone
        return True
    return True


def _terminate(proc: subprocess.Popen, grace: float = _GRACE_SECONDS) -> None:
    """Stop the child and everything it launched.

    Signals the whole process group, because killing just the child would orphan the task processes
    it spawned: SIGTERM first, so Nextflow runs its JVM shutdown hooks and cleans up its own tasks, then
    SIGKILL for whatever is still running once the grace period is over. The group is waited on, not
    just its leader — Nextflow exiting does not mean its tasks did, and a task that ignores or is
    still handling SIGTERM would otherwise be left running in the background.
    """
    if not hasattr(os, "killpg"):                     # Windows: no process groups to signal
        proc.kill()
        proc.wait()
        return
    pgid = proc.pid                                   # start_new_session: the child leads its group
    deadline = time.monotonic() + grace
    try:
        os.killpg(pgid, signal.SIGTERM)
    except OSError:
        pass
    try:
        try:
            proc.wait(timeout=grace)
        except subprocess.TimeoutExpired:
            pass
        while _group_alive(pgid) and time.monotonic() < deadline:
            time.sleep(0.1)
    finally:
        # Also on a second Ctrl-C during the grace period: that asks to stop now, not to leave the
        # group running — skip the rest of the wait, but still kill it.
        try:
            os.killpg(pgid, signal.SIGKILL)
        except OSError:
            pass                                      # the group is already gone
        proc.wait()
