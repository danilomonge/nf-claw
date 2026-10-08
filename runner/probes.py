"""Bounded metadata probes, including cleanup of bootstrap subprocesses."""
from __future__ import annotations

import os
import signal
import subprocess


def capture(command: list[str], *, timeout: float,
            env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    """Capture a probe and stop its process group on timeout or interruption.

    A Nextflow launcher can spawn curl or Java even for ``-version``. The standard
    subprocess.run timeout kills only its leader, leaving those children behind.
    These metadata probes require no pipeline shutdown grace period.
    """
    grouped = hasattr(os, "killpg")
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, env=env, start_new_session=grouped)
    try:
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except BaseException:
            try:
                if grouped:
                    os.killpg(proc.pid, signal.SIGKILL)
                else:
                    proc.kill()
            except ProcessLookupError:
                pass
            try:
                proc.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                # An escaped descendant must not make pipe drainage wait forever.
                proc.stdout.close()
                proc.stderr.close()
                proc.wait(timeout=2)
            raise
        return subprocess.CompletedProcess(command, proc.returncode, stdout, stderr)
    finally:
        proc.stdout.close()
        proc.stderr.close()
