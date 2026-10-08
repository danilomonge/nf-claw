"""Exercise the release gate against controlled external Nextflow outcomes."""
import os
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _executable(path, text):
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def _accept(tmp_path, log, exit_code):
    up = tmp_path / "pipelines" / "mini" / "upstream"
    up.mkdir(parents=True)
    (up / "nextflow.config").write_text("manifest { nextflowVersion = '!>=25.10.4' }\n")
    fake = tmp_path / "bin"
    fake.mkdir()
    _executable(fake / "git", "#!/bin/sh\n[ \"$1\" = submodule ] || exit 2\nexit 0\n")
    _executable(fake / "nextflow", '#!/bin/sh\nprintf "%s\\n" "$@" > "$FAKE_NXF_ARGS"\n'
                'cat "$FAKE_NXF_LOG"\nexit "$FAKE_NXF_EXIT"\n')
    source_log = tmp_path / "nextflow-output.txt"
    source_log.write_text(log)
    result = tmp_path / "verdict.tsv"
    env = {**os.environ, "PATH": f"{fake}{os.pathsep}{os.environ['PATH']}",
           "RUNNER_TEMP": str(tmp_path), "GITHUB_STEP_SUMMARY": str(tmp_path / "summary.md"),
           "NFCLAW_RESULT_FILE": str(result), "NFCLAW_KEEP_SUBMODULES": "1",
           "FAKE_NXF_LOG": str(source_log), "FAKE_NXF_EXIT": str(exit_code),
           "FAKE_NXF_ARGS": str(tmp_path / "nextflow-args.txt")}
    process = subprocess.run(["bash", str(ROOT / "scripts" / "nextflow_accept.sh"), "mini"],
                             cwd=tmp_path, env=env, capture_output=True, text=True)
    return process, result.read_text()


@pytest.mark.parametrize("banner", ["* PREVIEW *", "Only displaying parameters that differ",
                                    "Core Nextflow options", "If you use nf-core"])
def test_banner_does_not_accept_workflow_failure(tmp_path, banner):
    process, verdict = _accept(tmp_path, f"{banner}\nERROR ~ Invalid sample metadata\n", 1)
    assert process.returncode != 0
    assert verdict == "mini\trejected\n"


@pytest.mark.parametrize("exit_code", [124, 137, 143])
def test_timeout_or_signal_after_banner_is_rejected(tmp_path, exit_code):
    process, verdict = _accept(tmp_path, "* PREVIEW *\n", exit_code)
    assert process.returncode != 0
    assert verdict == "mini\trejected\n"


def test_remote_input_staging_failure_is_unverified_and_fails_gate(tmp_path):
    process, verdict = _accept(tmp_path, "* PREVIEW *\nERROR ~ No such file or directory: "
                              "https://example.invalid/reads.fastq.gz\n", 1)
    assert process.returncode != 0
    assert verdict == "mini\tstaging-unverified\n"


def test_successful_preview_is_accepted(tmp_path):
    process, verdict = _accept(tmp_path, "* PREVIEW *\n", 0)
    assert process.returncode == 0
    assert verdict == "mini\taccepted\n"
    # The gate invokes preview mode, which Nextflow defines as skipping every process.
    args = (tmp_path / "nextflow-args.txt").read_text().splitlines()
    assert "-preview" in args and "-stub-run" not in args


def _discovery_step(tmp_path, verdict):
    raw = (ROOT / ".github" / "workflows" / "discover-pipelines.yml").read_text()
    step = raw.split("id: disc", 1)[1].split("\n      - name: Unit tests", 1)[0]
    script = re.search(r"^        run: \|\n(.*)", step, re.M | re.S).group(1)
    script = "\n".join(line[10:] for line in script.splitlines())
    fake = tmp_path / "bin"
    fake.mkdir()
    _executable(fake / "python", '#!/bin/sh\ncase "$*" in\n'
                '  *"--rollback "*) printf "%s\\n" "$*" >> "$ROLLBACK_LOG" ;;\n'
                '  *"librarian.discover_pipelines"*) echo "mini: added at 1.0.0" ;;\n'
                '  *"librarian.write_catalog"*) exit 0 ;;\n'
                '  *) exit 2 ;;\nesac\n')
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    _executable(scripts / "nextflow_accept.sh", '#!/bin/sh\nprintf "%s" "$FAKE_VERDICT" '
                '> "$NFCLAW_RESULT_FILE"\nexit 1\n')
    output = tmp_path / "github-output"
    rollback = tmp_path / "rollback.txt"
    env = {**os.environ, "PATH": f"{fake}{os.pathsep}{os.environ['PATH']}", "LIMIT": "12",
           "RUNNER_TEMP": str(tmp_path), "GITHUB_OUTPUT": str(output),
           "FAKE_VERDICT": verdict, "ROLLBACK_LOG": str(rollback)}
    process = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env,
                             capture_output=True, text=True)
    return process, output.read_text() if output.exists() else "", rollback


@pytest.mark.parametrize("verdict", ["rejected", "staging-unverified"])
def test_discovery_drops_every_pipeline_without_completed_acceptance(tmp_path, verdict):
    process, output, rollback = _discovery_step(tmp_path, f"mini\t{verdict}\n")
    assert process.returncode == 0
    assert output == "kept=0\n"
    assert "--rollback mini" in rollback.read_text()


@pytest.mark.parametrize("verdict", ["", "mini\tunknown\n", "other\taccepted\n",
                                    "mini\taccepted\nmini\taccepted\n"])
def test_discovery_cannot_keep_a_pipeline_with_missing_or_unknown_verdict(tmp_path, verdict):
    process, output, _ = _discovery_step(tmp_path, verdict)
    assert process.returncode != 0
    assert "kept=" not in output


def test_discovery_keeps_a_completed_acceptance(tmp_path):
    process, output, rollback = _discovery_step(tmp_path, "mini\taccepted\n")
    assert process.returncode == 0
    assert output == "kept=1\n"
    assert not rollback.exists()
