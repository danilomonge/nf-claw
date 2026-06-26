import sys
from pathlib import Path

import pytest
from runner import execution
from runner.errors import NfclawError

PY = sys.executable

def test_success_writes_logs(tmp_path):
    res = execution.run([PY, "-c", "print('hi')"], cwd=tmp_path,
                        logs_dir=tmp_path / "logs", timeout_seconds=30)
    assert res.exit_code == 0
    assert (tmp_path / "logs" / "stdout.txt").read_text().strip() == "hi"

def test_nonzero_raises(tmp_path):
    with pytest.raises(NfclawError):
        execution.run([PY, "-c", "import sys; sys.exit(3)"], cwd=tmp_path,
                      logs_dir=tmp_path / "logs", timeout_seconds=30)

def test_timeout_raises(tmp_path):
    with pytest.raises(NfclawError):
        execution.run([PY, "-c", "import time; time.sleep(5)"], cwd=tmp_path,
                      logs_dir=tmp_path / "logs", timeout_seconds=1)


def test_env_extra_is_applied_to_subprocess(tmp_path):
    execution.run([PY, "-c", "import os; print(os.environ.get('NXF_VER', 'MISSING'))"],
                  cwd=tmp_path, logs_dir=tmp_path / "logs", timeout_seconds=30,
                  env_extra={"NXF_VER": "25.10.2"})
    assert (tmp_path / "logs" / "stdout.txt").read_text().strip() == "25.10.2"


def test_env_extra_preserves_inherited_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("INHERITED_MARKER", "yes")
    execution.run([PY, "-c", "import os; print(os.environ.get('INHERITED_MARKER', 'MISSING'))"],
                  cwd=tmp_path, logs_dir=tmp_path / "logs", timeout_seconds=30,
                  env_extra={"NXF_VER": "1"})
    assert (tmp_path / "logs" / "stdout.txt").read_text().strip() == "yes"


def test_failure_enriches_error_from_stderr_signature(tmp_path):
    cmd = [PY, "-c", "import sys; sys.stderr.write('java.net.SocketException: Network is "
           "unreachable\\n'); sys.exit(1)"]
    with pytest.raises(NfclawError) as exc:
        execution.run(cmd, cwd=tmp_path, logs_dir=tmp_path / "logs", timeout_seconds=30)
    assert "NXF_JVM_ARGS" in exc.value.fix                    # the diagnosed fix, not just "inspect log"
    assert "Full log" in exc.value.fix                        # raw log still pointed to


def test_failure_flags_space_via_diagnose_paths(tmp_path):
    cmd = [PY, "-c", "import sys; sys.exit(1)"]
    with pytest.raises(NfclawError) as exc:
        execution.run(cmd, cwd=tmp_path, logs_dir=tmp_path / "logs", timeout_seconds=30,
                      diagnose_paths=(Path("/vol/draft 2/out"),))
    assert "space" in exc.value.fix.lower() and "NXF_WORK" in exc.value.fix
