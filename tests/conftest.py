import os

import pytest


@pytest.fixture(autouse=True)
def _isolate_nextflow_env(monkeypatch):
    """Run every test with a clean NXF_* environment.

    Provenance records the NXF_* variables a run inherited from the shell, so without this a
    developer who exports (say) NXF_OFFLINE or NXF_VER would see unrelated tests fail. Tests
    that care about inherited variables set them explicitly.
    """
    for key in [k for k in os.environ if k.startswith("NXF_")]:
        monkeypatch.delenv(key, raising=False)
