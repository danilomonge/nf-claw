from pathlib import Path

from runner import runlog

FIXTURES = Path(__file__).parent / "fixtures" / "nextflow_console"


def _console(name: str) -> str:
    # Real console output captured from Nextflow 26.04.3 (stdout of `nextflow run`, not a TTY).
    return (FIXTURES / name).read_text(encoding="utf-8")


# --- where Nextflow writes its own log ------------------------------------------------------------

def test_nextflow_log_defaults_to_the_launch_dir(monkeypatch):
    # nfclaw launches Nextflow from --outdir, and Nextflow writes `.nextflow.log` into its launch
    # directory — not into the caller's cwd, which is where its relative "Check '.nextflow.log'" hint
    # sends an agent looking.
    monkeypatch.delenv("NXF_LOG_FILE", raising=False)
    assert runlog.nextflow_log_path(Path("/runs/out")) == Path("/runs/out/.nextflow.log")


def test_nextflow_log_honours_a_relative_nxf_log_file_against_the_launch_dir(monkeypatch):
    monkeypatch.setenv("NXF_LOG_FILE", "logs/nf.log")
    assert runlog.nextflow_log_path(Path("/runs/out")) == Path("/runs/out/logs/nf.log")


def test_nextflow_log_overlay_wins_over_the_shell(monkeypatch):
    monkeypatch.setenv("NXF_LOG_FILE", "shell.log")
    got = runlog.nextflow_log_path(Path("/runs/out"), {"NXF_LOG_FILE": "/abs/overlay.log"})
    assert got == Path("/abs/overlay.log")


# --- quoting Nextflow's own error report ----------------------------------------------------------

def test_excerpt_of_a_task_failure_is_the_last_error_report_once():
    # Nextflow 26.04 prints the report twice when stdout is not a TTY; quote it once, in full.
    excerpt = "\n".join(runlog.error_excerpt(_console("task_failure.txt")))
    assert excerpt.count("ERROR ~ Error executing process > 'BOOM'") == 1
    assert "the real task error: samtools could not open input.bam" in excerpt
    assert "Work dir:" in excerpt
    assert "BOOM | 0 of 1" in excerpt                    # the progress line naming the failed step


def test_excerpt_keeps_the_detail_nextflow_prints_before_its_error_line():
    # A config/script syntax error is described *above* `ERROR ~ Config parsing failed`.
    excerpt = "\n".join(runlog.error_excerpt(_console("config_parse_error.txt")))
    assert "Error bad.config:3:1: Unexpected input: '}'" in excerpt
    assert "ERROR ~ Config parsing failed" in excerpt
    assert "N E X T F L O W" not in excerpt              # the banner is not part of the error


def test_excerpt_without_an_error_marker_is_the_console_tail():
    # `error "..."` in a workflow body prints just the message — no `ERROR ~` prefix.
    excerpt = runlog.error_excerpt(_console("workflow_error.txt"))
    assert excerpt[-1] == "pipeline-level failure: missing --fasta"


def test_excerpt_strips_terminal_control_sequences():
    console = ("\x1b[0;35m[nf-core/demo]\x1b[0m starting\n"
               "progress 10%\rprogress 100%\r\n"
               "ERROR ~ \x1b[31mboom\x1b[0m\n")
    excerpt = runlog.error_excerpt(console)
    assert "ERROR ~ boom" in excerpt
    assert "progress 100%" in excerpt and not any("10%" in line for line in excerpt)
    assert not any("\x1b" in line or "\r" in line for line in excerpt)


def test_a_long_error_report_is_capped_but_keeps_its_head_and_tail():
    body = [f"  line {i}" for i in range(200)]
    console = "\n".join(["ERROR ~ Error executing process > 'BIG'", "Caused by:", *body,
                         "Work dir:", "  /w/ab/cdef"]) + "\n"
    excerpt = runlog.error_excerpt(console)
    assert len(excerpt) <= 45
    assert excerpt[0] == "ERROR ~ Error executing process > 'BIG'"
    assert excerpt[-2:] == ["Work dir:", "  /w/ab/cdef"]
    assert any("lines omitted" in line for line in excerpt)


def test_empty_console_gives_an_empty_excerpt():
    assert runlog.error_excerpt("") == []


# --- the failing task ----------------------------------------------------------------------------

def test_failing_task_dir_is_read_from_the_report():
    excerpt = runlog.error_excerpt(_console("task_failure.txt"))
    assert runlog.failing_task_dir(excerpt) == Path(
        "/mnt/volume/drafts/draft-7/probe/l1/work/ca/546a82c2be33e7d21e7983b988f1e9")


def test_no_failing_task_dir_when_the_report_names_none():
    assert runlog.failing_task_dir(runlog.error_excerpt(_console("config_parse_error.txt"))) is None
