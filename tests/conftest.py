import os
import subprocess
import sys
import tempfile
import time

import pytest


@pytest.fixture(autouse=True)
def _isolate_temp_dir(monkeypatch, tmp_path_factory):
    """Point Python's temp root at a per-test directory pytest cleans up.

    `nfclaw run --check` deliberately stages its params file in a fresh temp directory that outlives
    the process (the printed command must stay runnable), so every check-only test left an
    `nfclaw-check-*` directory behind in the system temp dir.
    """
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path_factory.mktemp("tmp")))


@pytest.fixture(autouse=True)
def _isolate_nextflow_env(monkeypatch):
    """Run every test with a clean NXF_* environment.

    Provenance records the NXF_* variables a run inherited from the shell, so without this a
    developer who exports (say) NXF_OFFLINE or NXF_VER would see unrelated tests fail. Tests
    that care about inherited variables set them explicitly.
    """
    for key in [k for k in os.environ if k.startswith("NXF_")]:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def named_process():
    """Start a sleeping process whose command line carries `markers` (as nfclaw's, a replay's or
    Nextflow's would) and hand it back only once the kernel shows that command line.

    Right after `Popen` returns, a Linux child can still be in the middle of `exec`: its
    /proc/<pid>/cmdline is not yet the new program's (about 1 in 5 starts on the de.NBI host), so a
    test that checked it at once saw an unknown process and failed at random."""
    from runner import runlog

    procs = []

    def start(*markers: str) -> subprocess.Popen:
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)", *markers])
        procs.append(proc)
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if all(m in (runlog._argv(proc.pid) or []) for m in markers):
                break
            time.sleep(0.01)
        return proc

    yield start
    for proc in procs:
        proc.kill()
        proc.wait()
