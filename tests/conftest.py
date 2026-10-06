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


_FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture
def library(tmp_path):
    """A tiny nf-claw checkout: fixture pipelines under pipelines/, handoff rules under handoffs/.

    `make("mini_up", "mini", rules={("mini_up", "mini"): {...}})` returns the checkout root."""
    import json
    import shutil
    from pathlib import Path

    def make(*names: str, rules: dict | None = None) -> Path:
        for name in names:
            up = tmp_path / "pipelines" / name / "upstream"
            if not up.exists():
                shutil.copytree(Path(_FIXTURES) / name, up)
                for f in ("main.nf", "nextflow.config"):
                    (up / f).write_text("x")
                (tmp_path / "pipelines" / name / "skill.md").write_text(f"---\nname: {name}\n---\n")
        for (upstream, downstream), body in (rules or {}).items():
            path = tmp_path / "handoffs" / upstream / f"{downstream}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(body))
        return tmp_path
    return make


@pytest.fixture
def finished_run():
    """Lay out a completed nfclaw run — result files, provenance/params.json, outputs.sha256 and a
    success manifest — what a real stage leaves behind. `{outdir}` in a file's text becomes the run's
    absolute outdir (fetchngs writes absolute FastQ paths into its samplesheet)."""
    import json
    from pathlib import Path

    from runner import provenance

    def make(outdir: Path, files: dict, params: dict | None = None) -> Path:
        for rel, text in files.items():
            p = outdir / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text.replace("{outdir}", str(outdir)))
        prov = outdir / "provenance"
        prov.mkdir(parents=True, exist_ok=True)
        (prov / "params.json").write_text(json.dumps({"outdir": str(outdir), **(params or {})}))
        (prov / "outputs.sha256").write_text("".join(
            f"{d}  {r}\n" for r, d in provenance.output_checksums(outdir).items()))
        (prov / "run_manifest.json").write_text(json.dumps(
            {"pipeline": "x", "version": "1.0.0", "commit": "c" * 40, "outcome": "success"}))
        return outdir
    return make
