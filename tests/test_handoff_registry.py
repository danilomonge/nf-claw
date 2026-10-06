"""The shipped handoff rules (handoffs/): they parse, name library pipelines, and fit the pinned
schemas. The fit needs initialized submodules; the drift gate (CI) has them."""
from pathlib import Path

import pytest

from runner import handoff, schema, submodule

ROOT = Path(__file__).resolve().parent.parent
RULES = handoff.load_registry(ROOT)


def _tree(name):
    st = submodule.resolve(name, ROOT / "pipelines")
    if not st.complete:
        pytest.skip(f"{name} submodule not initialized")
    return st.path


def test_registry_parses_and_names_library_pipelines():
    assert ("fetchngs", "rnaseq") in RULES
    names = {d.name for d in (ROOT / "pipelines").iterdir() if d.is_dir()}
    for up, down in RULES:
        assert up in names and down in names, f"handoffs/{up}/{down}.json names an unknown pipeline"
        assert RULES[(up, down)].description, f"handoffs/{up}/{down}.json has no description"


@pytest.mark.parametrize("edge", sorted(RULES), ids=lambda e: f"{e[0]}->{e[1]}")
def test_every_rule_fits_the_pinned_schemas(edge):
    up, down = (_tree(n) for n in edge)
    assert handoff.check_rule(RULES[edge], up, down) == []


def test_fetchngs_rules_set_their_own_target_from_fetchngs_enum():
    # The direct handoffs rely on fetchngs's --nf-core-pipeline; its schema enum is the authority.
    enum = schema.load_param_schema(_tree("fetchngs")).params["nf_core_pipeline"].enum
    targets = [down for (up, down) in RULES if up == "fetchngs"]
    assert targets
    for down in targets:
        assert RULES[("fetchngs", down)].upstream_params == {"nf_core_pipeline": down}
        assert down in enum
