"""Guards on the automation: the workflows hold write tokens and run third-party pipeline code."""
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WF = ROOT / ".github" / "workflows"


def _text(name: str) -> str:
    return (WF / name).read_text(encoding="utf-8")


def _job(text: str, name: str) -> str:
    """The body of one job (from `  <name>:` to the next 2-space-indented key)."""
    m = re.search(rf"^  {name}:\n(.*?)(?=^  \S|\Z)", text, re.M | re.S)
    assert m, f"job {name!r} not found"
    return m.group(1)


def test_no_workflow_expands_inputs_inside_a_shell_script():
    # `${{ inputs.* }}` inside `run:` is substituted before bash parses the script, so a crafted
    # value becomes shell code. Inputs may only reach a script through an `env:` mapping.
    for wf in sorted(WF.glob("*.yml")):
        for line in wf.read_text(encoding="utf-8").splitlines():
            if re.search(r"\$\{\{\s*(inputs|github\.event\.inputs)\.", line):
                assert re.match(r"^\s+[A-Z][A-Z0-9_]*:\s", line), f"{wf.name}: {line.strip()}"


def test_discovery_step_fails_when_discovery_fails():
    # `discover_pipelines | tee` without pipefail reported a crashed discovery (e.g. nf-co.re down)
    # as "No new pipelines to add." with a green check.
    step = _text("discover-pipelines.yml").split("id: disc", 1)[1].split("\n      - ", 1)[0]
    assert "pipefail" in step


def test_jobs_that_run_upstream_code_do_not_keep_a_write_token():
    # Both jobs evaluate upstream pipeline code (`nextflow run -preview` parses each release's Groovy
    # config) while holding contents: write; the checkout must not leave that token in .git/config.
    for name in ("auto-update.yml", "discover-pipelines.yml"):
        text = _text(name)
        assert text.count("uses: actions/checkout@") == text.count("persist-credentials: false"), name


def test_pages_and_oidc_permissions_are_scoped_to_the_deploy_job():
    # The build job runs `npm ci` + `next build` (third-party code); only the deploy job needs to
    # publish to Pages or mint an OIDC token.
    text = _text("deploy-pages.yml")
    top = text.split("\njobs:", 1)[0]
    build, deploy = _job(text, "build"), _job(text, "deploy")
    for scope in ("pages: write", "id-token: write"):
        assert scope not in top and scope not in build
        assert scope in deploy


def test_acceptance_script_fails_when_it_finds_no_pipelines(tmp_path):
    # With no arguments it validates `nfclaw list`; an empty list must fail, not pass vacuously.
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "nfclaw").write_text("#!/bin/sh\nexit 0\n")
    (fake / "nfclaw").chmod(0o755)
    env = {**os.environ, "PATH": f"{fake}{os.pathsep}{os.environ['PATH']}",
           "RUNNER_TEMP": str(tmp_path)}
    r = subprocess.run(["bash", str(ROOT / "scripts" / "nextflow_accept.sh")], cwd=tmp_path,
                       env=env, capture_output=True, text=True)
    assert r.returncode != 0
    assert "no pipelines" in (r.stdout + r.stderr).lower()


def test_acceptance_script_rejects_a_failed_partial_pipeline_inventory(tmp_path):
    fake = tmp_path / "bin"
    fake.mkdir()
    (fake / "nfclaw").write_text("#!/bin/sh\necho mini\nexit 1\n")
    (fake / "nfclaw").chmod(0o755)
    env = {**os.environ, "PATH": f"{fake}{os.pathsep}{os.environ['PATH']}",
           "RUNNER_TEMP": str(tmp_path)}
    result = subprocess.run(["bash", str(ROOT / "scripts/nextflow_accept.sh")], cwd=tmp_path,
                            env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert "could not list" in result.stdout
