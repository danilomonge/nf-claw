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


def test_excerpt_of_an_nf_core_failure_quotes_each_distinct_report_once():
    # Real nf-core/demo 1.2.0 console (corrupt FASTQ): Nextflow renders the process report three
    # times, and the nf-core template then adds its generic "ERROR ~ Pipeline failed" report — which
    # is the *last* `ERROR ~` line but not the cause. Each distinct report is quoted once, in order.
    excerpt = runlog.error_excerpt(_console("nfcore_task_failure.txt"))
    text = "\n".join(excerpt)
    assert text.count("ERROR ~ Error executing process > 'NFCORE_DEMO:DEMO:FASTQC (BROKEN)'") == 1
    assert text.count("ERROR ~ Pipeline failed.") == 1
    assert text.index("Error executing process") < text.index("Pipeline failed.")
    assert "java.util.zip.ZipException: Not in GZIP format" in text      # the tool's own error
    assert "Work dir:" in text
    assert len(excerpt) <= 50
    assert runlog.failing_task_dir(excerpt) == Path(
        "/mnt/volume/drafts/draft-7/nf-claw/work/67/506aabdbd84ecedb67949041e7e5f2")


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
    assert len(excerpt) <= 50
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


# --- the underlying cause, from Nextflow's own log -----------------------------------------------

def test_log_causes_quote_the_exception_chain_of_the_last_error():
    # Real .nextflow.log of a run whose host cannot reach GitHub: the console only says "Unable to
    # parse config file"; the reason exists nowhere but in the log's exception chain.
    causes = runlog.nextflow_log_causes(FIXTURES / "nextflow_log_config_unreachable.log")
    assert causes == [
        "Caused by: java.io.IOException: Cannot read config file include: "
        "https://raw.githubusercontent.com/nf-core/configs/master/nfcore_custom.config",
        "Caused by: java.net.SocketException: Network is unreachable",
    ]


def test_log_causes_are_empty_for_a_task_failure_report(tmp_path):
    # A failed task's entry repeats the console report; its bare "Caused by:" heading is not a cause.
    log = tmp_path / ".nextflow.log"
    log.write_text(
        "Oct-05 21:42:15.651 [TaskFinalizer-1] ERROR nextflow.processor.TaskProcessor - "
        "Error executing process > 'BOOM'\n\nCaused by:\n"
        "  Process `BOOM` terminated with an error exit status (3)\n\n"
        "Oct-05 21:42:15.663 [TaskFinalizer-1] DEBUG nextflow.Session - Session aborted\n")
    assert runlog.nextflow_log_causes(log) == []


def test_log_causes_ignore_exceptions_outside_the_last_error_entry(tmp_path):
    log = tmp_path / ".nextflow.log"
    log.write_text(
        "Oct-05 10:00:00.000 [main] WARN  nextflow.Foo - retrying\n"
        "Caused by: java.net.SocketTimeoutException: earlier, recovered\n"
        "Oct-05 10:00:01.000 [main] ERROR nextflow.cli.Launcher - boom\n"
        "Caused by: java.lang.IllegalStateException: the real one\n"
        "\tat x.y(Z.java:1)\n"
        "Oct-05 10:00:02.000 [main] DEBUG nextflow.Session - after\n"
        "Caused by: java.lang.RuntimeException: after the error entry\n")
    assert runlog.nextflow_log_causes(log) == [
        "Caused by: java.lang.IllegalStateException: the real one"]


def test_log_causes_of_a_missing_log_are_empty(tmp_path):
    assert runlog.nextflow_log_causes(tmp_path / "absent.log") == []


def test_log_causes_keep_a_multi_line_exception_message(tmp_path):
    # Real shape (Nextflow 26.04, a config syntax error): the message continues on the lines after
    # "startup failed:" and stops where the stack frames begin.
    log = tmp_path / ".nextflow.log"
    log.write_text(
        "Oct-05 22:03:47.926 [main] ERROR nextflow.cli.Launcher - Config parsing failed\n"
        "nextflow.exception.ConfigParseException: Config parsing failed\n"
        "\tat nextflow.config.ConfigBuilder.build(ConfigBuilder.groovy:821)\n"
        "Caused by: org.codehaus.groovy.control.MultipleCompilationErrorsException: startup failed:\n"
        "_nf_config_ffa03b8917b73ec2: 3: Unexpected input: '}' @ line 3, column 1.\n"
        "   }\n"
        "   ^\n"
        "\n"
        "1 error\n"
        "\n"
        "\tat org.codehaus.groovy.control.ErrorCollector.failIfErrors(ErrorCollector.java:292)\n"
        "\t... 9 common frames omitted\n")
    assert runlog.nextflow_log_causes(log) == [
        "Caused by: org.codehaus.groovy.control.MultipleCompilationErrorsException: startup failed:",
        "  _nf_config_ffa03b8917b73ec2: 3: Unexpected input: '}' @ line 3, column 1.",
        "     }",
        "     ^",
        "  1 error",
    ]


def test_log_causes_are_quoted_once(tmp_path):
    log = tmp_path / ".nextflow.log"
    log.write_text(
        "Oct-05 10:00:01.000 [main] ERROR nextflow.cli.Launcher - boom\n"
        "Caused by: java.net.SocketException: Network is unreachable\n"
        "\tat x.y(Z.java:1)\n"
        "Caused by: java.net.SocketException: Network is unreachable\n"
        "\tat x.y(Z.java:1)\n")
    assert runlog.nextflow_log_causes(log) == [
        "Caused by: java.net.SocketException: Network is unreachable"]


# --- stderr: where nf-schema puts its validation details -----------------------------------------

def test_nf_schema_details_are_quoted_from_stderr():
    # Real nf-core/demo 1.2.0 run with an invalid enum: stdout only says "Validation of pipeline
    # parameters failed!"; *which* value is invalid is written to stderr.
    excerpt = runlog.stderr_excerpt(_console("nfschema_validation.stderr.txt"))
    text = "\n".join(excerpt)
    assert "* --publish_dir_mode (bogus): Expected any of" in text
    assert "is available - Please consider updating" not in text      # launcher chatter dropped


def test_stderr_with_only_the_update_notice_has_nothing_to_quote():
    assert runlog.stderr_excerpt(
        "Nextflow 26.04.6 is available - Please consider updating your version to it\n") == []


def test_context_above_an_error_is_only_the_paragraph_directly_above_it():
    # nf-core prints its citation block before a validation error; only the paragraph adjacent to
    # the error line is quoted, never the run's banner or parameter summary.
    excerpt = runlog.error_excerpt(_console("nfschema_validation.stdout.txt"))
    assert excerpt[-3:] == ["ERROR ~ Validation of pipeline parameters failed!", "",
                            " -- Check '.nextflow.log' file for details"]
    assert len(excerpt) <= 6
    assert not any("zenodo" in line or "userName" in line for line in excerpt)


def test_without_a_report_the_console_tail_is_optional():
    console = _console("workflow_error.txt")
    assert runlog.error_excerpt(console, tail_if_no_report=False) == []
    assert runlog.error_excerpt(console)[-1] == "pipeline-level failure: missing --fasta"
