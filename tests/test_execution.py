import sys
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
