from __future__ import annotations

import os
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from runner import diagnostics
from runner.errors import ErrorCode, NfclawError


@dataclass(frozen=True)
class ExecResult:
    exit_code: int
    stdout_path: Path
    stderr_path: Path


def _stderr_tail(path: Path, limit: int = 8000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[-limit:]
    except OSError:
        return ""


def run(command: list[str], *, cwd: Path, logs_dir: Path,
        timeout_seconds: int, env_extra: dict[str, str] | None = None,
        diagnose_paths: tuple[Path, ...] = ()) -> ExecResult:
    logs_dir.mkdir(parents=True, exist_ok=True)
    out_p, err_p = logs_dir / "stdout.txt", logs_dir / "stderr.txt"
    popen_kwargs = {} if sys.platform == "win32" else {"start_new_session": True}
    # Inherit the full environment, then overlay the caller's NXF_* overrides (engine version,
    # JVM args, …). Inheriting keeps shell-set vars (proxies, JAVA_HOME) working as before.
    env = {**os.environ, **env_extra} if env_extra else None
    with out_p.open("w") as out_fh, err_p.open("w") as err_fh:
        try:
            proc = subprocess.Popen(command, cwd=str(cwd), stdout=out_fh,
                                    stderr=err_fh, env=env, **popen_kwargs)
        except OSError as exc:
            raise NfclawError(ErrorCode.EXECUTION_FAILED,
                              f"Could not launch process: {exc}",
                              fix="Ensure `nextflow` is installed and on PATH.") from exc
        try:
            code = proc.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            _terminate(proc)
            raise NfclawError(ErrorCode.EXECUTION_FAILED, "Execution timed out.",
                              fix="Increase --timeout or use a smaller dataset.",
                              details={"timeout_seconds": timeout_seconds})
    if code != 0:
        # Turn the failure into an actionable hint where we recognise the cause, then always
        # point at the full log. Lets the caller (and the agent) apply the right fix immediately.
        hints = diagnostics.diagnose(_stderr_tail(err_p), paths=diagnose_paths)
        fix = " ".join(hints + [f"Full log: {err_p}"])
        raise NfclawError(ErrorCode.EXECUTION_FAILED, "Nextflow execution failed.",
                          fix=fix, details={"exit_code": code})
    return ExecResult(code, out_p, err_p)


def _terminate(proc: subprocess.Popen) -> None:
    if hasattr(os, "killpg"):
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.killpg(os.getpgid(proc.pid), sig)
                proc.wait(timeout=10)
                return
            except (OSError, ProcessLookupError, subprocess.TimeoutExpired):
                continue
    proc.kill()
