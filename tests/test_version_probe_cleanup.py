"""Engine metadata probes must not leave bootstrap downloads running after timeout."""
import os
import signal
import subprocess
import time

import pytest

from runner import engine_version, provenance


def _alive(pid):
    result = subprocess.run(["ps", "-p", str(pid), "-o", "stat="],
                            capture_output=True, text=True, timeout=2)
    return result.returncode == 0 and bool(result.stdout.strip()) and not result.stdout.strip().startswith("Z")


@pytest.mark.parametrize("probe", [provenance._nextflow_version, engine_version._installed_raw])
@pytest.mark.parametrize("stop", ["timeout", "interrupt"])
def test_stopped_version_probe_cleans_up_download_children(tmp_path, monkeypatch, probe, stop):
    launcher = tmp_path / "nextflow"
    marker = tmp_path / "child.pid"
    launcher.write_text('#!/bin/sh\nsleep 60 &\necho $! >"$CHILD_PID_FILE"\nwait\n')
    launcher.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    monkeypatch.setenv("CHILD_PID_FILE", str(marker))
    communicate = subprocess.Popen.communicate

    def short_probe_timeout(self, input=None, timeout=None):
        try:
            return communicate(self, input=input, timeout=1 if timeout == 30 else timeout)
        except subprocess.TimeoutExpired:
            if stop == "interrupt" and timeout == 30:
                raise KeyboardInterrupt from None
            raise

    monkeypatch.setattr(subprocess.Popen, "communicate", short_probe_timeout)
    child = None
    try:
        def invoke():
            return (probe({"CHILD_PID_FILE": str(marker), "PATH": os.environ["PATH"]})
                    if probe is provenance._nextflow_version else probe())
        if stop == "interrupt":
            with pytest.raises(KeyboardInterrupt):
                invoke()
        else:
            assert not invoke()
        assert marker.exists(), "the fixture must launch a child before timing out"
        child = int(marker.read_text())
        deadline = time.monotonic() + 2
        while _alive(child) and time.monotonic() < deadline:
            time.sleep(0.02)
        assert not _alive(child), "the stopped bootstrap left its download child alive"
    finally:
        if child and _alive(child):
            os.kill(child, signal.SIGKILL)
