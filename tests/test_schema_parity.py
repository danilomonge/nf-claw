from pathlib import Path

import pytest

from runner import schema

REPO = Path(__file__).resolve().parent.parent
SAREK = REPO / "pipelines" / "sarek" / "upstream"
ALLOWLIST = Path(__file__).parent / "fixtures" / "golden" / "sarek_allowlist.txt"

# Flags that were CONTROLS in the legacy Sarek wrapper (not nf-core/sarek params);
# these are intentionally NOT in the pipeline schema.
WRAPPER_CONTROLS = {
    "check", "resume", "arm", "gpu", "spark_profile", "mutect_profile",
    "run_downstream", "downstream_skill", "profile", "nextflow_config",
    "pipeline_version", "pipeline_local", "params_file", "no_banner",
    "verbose", "extra_param",
}


@pytest.mark.skipif(not (SAREK / "nextflow_schema.json").exists(),
                    reason="sarek submodule not initialized")
def test_schema_covers_legacy_sarek_allowlist():
    legacy = {
        line.strip().lstrip("-").replace("-", "_")
        for line in ALLOWLIST.read_text().split()
        if line.strip()
    } - WRAPPER_CONTROLS
    known = schema.load_param_schema(SAREK).known_params()
    missing = legacy - known
    assert missing == set(), f"schema misses legacy sarek flags: {sorted(missing)}"
