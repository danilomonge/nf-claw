import os
import sys
import pytest
from pathlib import Path
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


def test_failure_quotes_nextflow_error_and_points_at_the_real_logs(tmp_path):
    # Nextflow prints its error report on *stdout*; stderr only carries launcher chatter (the
    # "Nextflow X is available" notice). Pointing at stderr.txt sent every reader to an empty file.
    nf_log = tmp_path / ".nextflow.log"
    nf_log.write_text("engine detail")
    child = ("import sys; print('Nextflow 99 is available', file=sys.stderr); "
             "print('ERROR ~ Error executing process > BOOM'); "
             "print(); print('Caused by:'); print('  the real cause'); sys.exit(1)")
    with pytest.raises(NfclawError) as exc:
        execution.run([PY, "-c", child], cwd=tmp_path, logs_dir=tmp_path / "logs",
                      timeout_seconds=30, nextflow_log=nf_log)
    text = str(exc.value)
    assert "ERROR ~ Error executing process > BOOM" in text and "the real cause" in text
    assert exc.value.details["run_log"] == str(tmp_path / "logs" / "run.log")
    assert exc.value.details["nextflow_log"] == str(nf_log)
    assert exc.value.details["exit_code"] == 1
    assert "known-issues.md" in exc.value.fix
    assert "stderr.txt" not in text


def test_failure_quotes_the_underlying_cause_from_the_nextflow_log(tmp_path):
    # The console said only "Unable to parse config file"; the cause is in Nextflow's log alone.
    import shutil
    nf_log = tmp_path / ".nextflow.log"
    shutil.copy(Path(__file__).parent / "fixtures" / "nextflow_console" /
                "nextflow_log_config_unreachable.log", nf_log)
    child = "import sys; print('ERROR ~ Unable to parse config file'); sys.exit(1)"
    with pytest.raises(NfclawError) as exc:
        execution.run([PY, "-c", child], cwd=tmp_path, logs_dir=tmp_path / "logs",
                      timeout_seconds=30, nextflow_log=nf_log)
    text = str(exc.value)
    assert "Caused by: java.net.SocketException: Network is unreachable" in text
    assert "nfcore_custom.config" in text


def test_failure_quotes_what_nextflow_wrote_on_stderr(tmp_path):
    # nf-schema writes *which* parameter is invalid to stderr; stdout only says that validation failed.
    child = ("import sys; print('Nextflow 99 is available - Please consider updating your version "
             "to it', file=sys.stderr); print('ERROR ~ Validation of pipeline parameters failed!'); "
             "print(' -- Check .nextflow.log file for details'); sys.stdout.flush(); "
             "print('* --publish_dir_mode (bogus): Expected any of [copy, link]', file=sys.stderr); "
             "sys.exit(1)")
    with pytest.raises(NfclawError) as exc:
        execution.run([PY, "-c", child], cwd=tmp_path, logs_dir=tmp_path / "logs",
                      timeout_seconds=30)
    text = str(exc.value)
    assert "ERROR ~ Validation of pipeline parameters failed!" in text
    assert "* --publish_dir_mode (bogus): Expected any of [copy, link]" in text
    assert "is available" not in text


def test_failure_without_a_report_quotes_stderr_rather_than_the_stdout_banner(tmp_path):
    child = ("import sys; print('BANNER LINE'); print('params summary'); "
             "print('java.lang.OutOfMemoryError: Java heap space', file=sys.stderr); sys.exit(1)")
    with pytest.raises(NfclawError) as exc:
        execution.run([PY, "-c", child], cwd=tmp_path, logs_dir=tmp_path / "logs",
                      timeout_seconds=30)
    text = str(exc.value)
    assert "java.lang.OutOfMemoryError: Java heap space" in text
    assert "BANNER LINE" not in text


def test_failure_without_any_report_quotes_the_stdout_tail(tmp_path):
    # `error "..."` in a workflow body prints only its message, on stdout.
    child = ("import sys; print('pipeline-level failure: missing --fasta'); "
             "print('Nextflow 99 is available - Please consider updating your version to it', "
             "file=sys.stderr); sys.exit(1)")
    with pytest.raises(NfclawError) as exc:
        execution.run([PY, "-c", child], cwd=tmp_path, logs_dir=tmp_path / "logs",
                      timeout_seconds=30)
    assert "pipeline-level failure: missing --fasta" in str(exc.value)


def test_failure_does_not_point_at_a_nextflow_log_that_was_never_written(tmp_path):
    # Nextflow can fail before it creates its log (e.g. the launcher cannot fetch NXF_VER).
    with pytest.raises(NfclawError) as exc:
        execution.run([PY, "-c", "import sys; sys.exit(1)"], cwd=tmp_path,
                      logs_dir=tmp_path / "logs", timeout_seconds=30,
                      nextflow_log=tmp_path / ".nextflow.log")
    assert "nextflow_log" not in exc.value.details
    assert exc.value.details["run_log"] == str(tmp_path / "logs" / "run.log")


def test_failure_points_at_the_failing_task_files(tmp_path):
    task = tmp_path / "work" / "ca" / "546a82"
    task.mkdir(parents=True)
    (task / ".command.err").write_text("samtools: could not open input.bam")
    child = (f"import sys; print('ERROR ~ Error executing process > BOOM'); print('Work dir:'); "
             f"print('  {task}'); sys.exit(1)")
    with pytest.raises(NfclawError) as exc:
        execution.run([PY, "-c", child], cwd=tmp_path, logs_dir=tmp_path / "logs",
                      timeout_seconds=30)
    assert exc.value.details["failing_task"] == str(task / ".command.err")


def test_run_log_records_the_whole_launch_in_order(tmp_path):
    # One file holds everything a launch printed — nfclaw's header, Nextflow's stdout and stderr
    # interleaved as produced — and ends with the outcome, so a background run needs no redirect.
    child = ("import sys, time; print('OUT1', flush=True); time.sleep(0.2); "
             "print('ERR1', file=sys.stderr, flush=True); time.sleep(0.2); print('OUT2')")
    execution.run([PY, "-c", child], cwd=tmp_path, logs_dir=tmp_path / "logs",
                  timeout_seconds=30, notes=["engine older than required"])
    log = (tmp_path / "logs" / "run.log").read_text()
    assert log.index("==> nfclaw run started") < log.index("OUT1") < log.index("ERR1") \
        < log.index("OUT2")
    assert "warning: engine older than required" in log
    assert f"launch dir: {tmp_path}" in log
    assert log.rstrip().splitlines()[-1].startswith("==> nfclaw run finished")
    assert log.rstrip().endswith(": success")


def test_failed_run_log_ends_with_the_outcome_after_the_error(tmp_path):
    with pytest.raises(NfclawError) as exc:
        execution.run([PY, "-c", "import sys; print('ERROR ~ boom'); sys.exit(4)"], cwd=tmp_path,
                      logs_dir=tmp_path / "logs", timeout_seconds=30)
    log = (tmp_path / "logs" / "run.log").read_text()
    assert str(exc.value) in log                         # the exact error the terminal showed
    assert log.rstrip().splitlines()[-1].endswith(": failed (exit status 4)")


def test_timed_out_run_is_logged(tmp_path):
    with pytest.raises(NfclawError) as exc:
        execution.run([PY, "-c", "import time; print('started', flush=True); time.sleep(10)"],
                      cwd=tmp_path, logs_dir=tmp_path / "logs", timeout_seconds=1)
    assert exc.value.details["run_log"] == str(tmp_path / "logs" / "run.log")
    log = (tmp_path / "logs" / "run.log").read_text()
    assert "started" in log
    assert log.rstrip().splitlines()[-1].endswith(": timed out after 1 s")


def test_a_relaunch_appends_to_the_logs_instead_of_overwriting_them(tmp_path):
    # `--resume` relaunches into the same --outdir; the failed attempt's log is the evidence of what
    # went wrong and must survive the retry.
    with pytest.raises(NfclawError):
        execution.run([PY, "-c", "import sys; print('ATTEMPT1'); sys.exit(1)"], cwd=tmp_path,
                      logs_dir=tmp_path / "logs", timeout_seconds=30)
    execution.run([PY, "-c", "print('ATTEMPT2')"], cwd=tmp_path, logs_dir=tmp_path / "logs",
                  timeout_seconds=30)
    log = (tmp_path / "logs" / "run.log").read_text()
    assert log.count("==> nfclaw run started") == 2
    assert log.index("ATTEMPT1") < log.index("ATTEMPT2")
    out = (tmp_path / "logs" / "stdout.txt").read_text()
    assert "ATTEMPT1" in out and "ATTEMPT2" in out


def test_launch_announces_where_the_run_is_logged(tmp_path, capfd):
    execution.run([PY, "-c", "print('x')"], cwd=tmp_path, logs_dir=tmp_path / "logs",
                  timeout_seconds=30)
    assert f"nfclaw: logging this run to {tmp_path / 'logs' / 'run.log'}" in capfd.readouterr().err


def test_launch_failure_is_logged(tmp_path):
    with pytest.raises(NfclawError) as exc:
        execution.run([str(tmp_path / "no-such-binary")], cwd=tmp_path,
                      logs_dir=tmp_path / "logs", timeout_seconds=30)
    assert exc.value.details["run_log"] == str(tmp_path / "logs" / "run.log")
    log = (tmp_path / "logs" / "run.log").read_text()
    assert log.rstrip().splitlines()[-1].endswith(": could not launch")


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
    log = (tmp_path / "logs" / "run.log").read_text()
    assert log.rstrip().splitlines()[-1].endswith(": interrupted")   # the log says how it ended

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


def test_no_timeout_waits_for_the_run_to_finish(tmp_path):
    # `nfclaw run` sets no wall-clock limit by default; None must mean "wait", not "time out".
    res = execution.run([PY, "-c", "import time; time.sleep(0.2); print('done')"], cwd=tmp_path,
                        logs_dir=tmp_path / "logs", timeout_seconds=None)
    assert res.exit_code == 0
    assert (tmp_path / "logs" / "stdout.txt").read_text().strip() == "done"


def test_teardown_kills_a_task_that_outlives_sigterm(tmp_path):
    # Nextflow exiting on SIGTERM does not mean its tasks did: one that ignores (or is still handling)
    # SIGTERM was left running in the background once the leader had exited.
    import os
    import subprocess
    import sys
    import time

    import pytest
    if sys.platform != "linux":
        pytest.skip("reads process state from /proc")
    pid_file = tmp_path / "task.pid"
    leader = tmp_path / "leader.sh"
    leader.write_text(
        "#!/bin/bash\n"
        f"bash -c 'trap \"\" TERM; echo $$ > {pid_file}; exec sleep 300' "
        ">/dev/null 2>&1 </dev/null &\n"
        "sleep 300\n")
    leader.chmod(0o755)
    proc = subprocess.Popen([str(leader)], start_new_session=True)
    deadline = time.monotonic() + 10
    while not pid_file.exists() or not pid_file.read_text().strip():
        assert time.monotonic() < deadline
        time.sleep(0.05)
    task = int(pid_file.read_text())

    def state():
        try:
            return open(f"/proc/{task}/stat").read().split()[2]
        except FileNotFoundError:
            return "gone"

    try:
        execution._terminate(proc, grace=1)
        time.sleep(0.2)
        assert state() in ("gone", "Z", "X"), state()      # dead (a zombie until init reaps it)
    finally:
        if state() not in ("gone", "Z", "X"):
            os.kill(task, 9)


def test_a_second_interrupt_during_teardown_still_kills_the_group(monkeypatch):
    # A second Ctrl-C while waiting out the grace period aborted the teardown before SIGKILL.
    import signal
    import types

    import pytest
    sent = []
    monkeypatch.setattr(execution.os, "killpg", lambda pgid, sig: sent.append(sig))

    def interrupted_wait(timeout=None):
        if timeout is not None:
            raise KeyboardInterrupt
        return 0

    proc = types.SimpleNamespace(pid=4242, wait=interrupted_wait)
    with pytest.raises(KeyboardInterrupt):
        execution._terminate(proc, grace=5)
    assert sent == [signal.SIGTERM, signal.SIGKILL]
