import os
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


def test_failure_points_to_log_and_known_issues(tmp_path):
    with pytest.raises(NfclawError) as exc:
        execution.run([PY, "-c", "import sys; sys.exit(1)"], cwd=tmp_path,
                      logs_dir=tmp_path / "logs", timeout_seconds=30)
    assert "stderr.txt" in exc.value.fix and "known-issues.md" in exc.value.fix


def test_output_is_streamed_live_to_the_terminal_and_the_logs(tmp_path, capfd):
    # The wrapper must not stay mute during a run: the child's stdout/stderr are teed to the
    # terminal as they are produced *and* still captured to the log files (which the provenance
    # bundle and error messages reference). capfd captures at the file-descriptor level, which is
    # where the tee writes (sys.stdout/err .buffer).
    execution.run([PY, "-c", "import sys; print('LIVE_OUT'); print('LIVE_ERR', file=sys.stderr)"],
                  cwd=tmp_path, logs_dir=tmp_path / "logs", timeout_seconds=30)
    captured = capfd.readouterr()
    assert "LIVE_OUT" in captured.out and "LIVE_ERR" in captured.err   # reached the terminal
    assert (tmp_path / "logs" / "stdout.txt").read_text().strip() == "LIVE_OUT"   # and the logs
    assert (tmp_path / "logs" / "stderr.txt").read_text().strip() == "LIVE_ERR"


@pytest.mark.skipif(not hasattr(os, "killpg"), reason="needs POSIX process groups")
def test_keyboard_interrupt_tears_down_the_child_and_its_children(tmp_path):
    # Ctrl-C during a run must not leave Nextflow (or the task processes it launched) running in the
    # background. Reproduce the interrupt with interrupt_main() while run() is blocked in wait(), and
    # confirm both the child and a grandchild it spawned are gone afterwards.
    import _thread
    import threading
    import time

    pids = tmp_path / "pids.txt"
    script = (
        "import os, sys, subprocess, time;"
        "g = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']);"
        f"open(r'{pids}', 'w').write(f'{{os.getpid()}} {{g.pid}}');"
        "sys.stdout.flush();"
        "time.sleep(60)"
    )
    timer = threading.Timer(1.5, _thread.interrupt_main)
    timer.start()
    try:
        with pytest.raises(KeyboardInterrupt):
            execution.run([PY, "-c", script], cwd=tmp_path,
                          logs_dir=tmp_path / "logs", timeout_seconds=60)
    finally:
        timer.cancel()

    child_pid, grand_pid = (int(x) for x in pids.read_text().split())
    deadline = time.time() + 5
    for pid in (child_pid, grand_pid):
        while time.time() < deadline:
            try:
                os.kill(pid, 0)                          # still alive → wait for the teardown
                time.sleep(0.1)
            except ProcessLookupError:
                break                                    # gone, as required
        else:
            raise AssertionError(f"process {pid} survived the interrupt")
