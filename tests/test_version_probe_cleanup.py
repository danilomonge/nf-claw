"""Engine metadata probes must not leave bootstrap downloads running after timeout."""
import os
import signal
import subprocess
import time

import pytest

from runner import engine_version, provenance


@pytest.mark.parametrize("probe", [provenance._nextflow_version, engine_version._installed_raw])
def test_failed_version_probe_cannot_supply_version_evidence_or_diagnostic_secrets(monkeypatch, probe):
    module = provenance if probe is provenance._nextflow_version else engine_version
    monkeypatch.setattr(module, "capture", lambda *a, **k: subprocess.CompletedProcess(
                            ["nextflow", "-version"], 1, "nextflow version 25.10.4 build 11033\n",
                            "failed download https://private-credential@host.invalid/engine\n"))
    assert not probe(), "a failed metadata command does not establish the installed engine"


@pytest.mark.parametrize("probe", [provenance._nextflow_version, engine_version._installed_raw])
def test_version_evidence_contains_only_a_validated_version_line(monkeypatch, probe):
    module = provenance if probe is provenance._nextflow_version else engine_version
    line = "nextflow version 25.10.4 build 11033"
    monkeypatch.setattr(module, "capture", lambda *a, **k: subprocess.CompletedProcess(
        ["nextflow", "-version"], 0, "bootstrap https://private-credential@host.invalid/engine\n",
        line + "\nLast modified: diagnostic metadata\n"))
    assert probe() == line


@pytest.mark.parametrize("output", ["unverified version 25.10.4", "",
                                   "nextflow version 25.10.4\nnextflow version 26.04.0\n"])
def test_missing_or_conflicting_version_lines_are_unknown(monkeypatch, output):
    monkeypatch.setattr(provenance, "capture", lambda *a, **k: subprocess.CompletedProcess(
        ["nextflow", "-version"], 0, output, ""))
    assert provenance._nextflow_version() == ""


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
        if timeout == 30:
            # Exercise interruption after the bootstrap actually starts its child.
            # Scheduler delays must not turn this into a test of launcher startup speed.
            deadline = time.monotonic() + 10
            while not marker.exists() and self.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
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


def test_timed_out_chain_config_probe_stops_children_before_scratch_cleanup(
        tmp_path, monkeypatch, library):
    from runner import chain
    root = library("mini_up")
    spec = chain.parse_spec({"stages": [{"pipeline": "mini_up"}]})
    planned = chain.plan(spec, repo_root=root)
    launcher = tmp_path / "nextflow"
    marker = tmp_path / "config-child.pid"
    launcher.write_text('#!/bin/sh\nsleep 60 &\necho $! >"$CHILD_PID_FILE"\nwait\n')
    launcher.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}:{os.environ['PATH']}")
    monkeypatch.setenv("CHILD_PID_FILE", str(marker))
    communicate = subprocess.Popen.communicate

    def timeout_after_child_started(self, input=None, timeout=None):
        if timeout == 1:
            # The regression is about stopping a running child, not OS scheduling latency.
            deadline = time.monotonic() + 10
            while not marker.exists() and self.poll() is None and time.monotonic() < deadline:
                time.sleep(0.02)
        return communicate(self, input=input, timeout=timeout)

    monkeypatch.setattr(subprocess.Popen, "communicate", timeout_after_child_started)
    child = None
    try:
        issues = chain._probe_config(spec, planned[0], timeout_seconds=1)
        assert len(issues) == 1 and "could not be verified" in issues[0]
        assert marker.exists(), "the fixture must launch a child before timing out"
        child = int(marker.read_text())
        deadline = time.monotonic() + 2
        while _alive(child) and time.monotonic() < deadline:
            time.sleep(0.02)
        assert not _alive(child), "config probing left a process in a removed scratch directory"
    finally:
        if child and _alive(child):
            os.kill(child, signal.SIGKILL)
