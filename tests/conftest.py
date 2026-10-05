import os
import tempfile

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
