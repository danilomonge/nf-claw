from pathlib import Path
from runner import nextflow_command as nc

def test_compose_profile_orders_test_first_modifiers_last():
    assert nc.compose_profile("docker", demo=True, modifiers=("arm64",)) == "test,docker,arm64"

def test_compose_profile_dedups():
    assert nc.compose_profile("docker,docker") == "docker"

def test_build_command_shape(tmp_path):
    up = tmp_path / "upstream"; up.mkdir()
    pf = tmp_path / "params.json"; pf.write_text("{}")
    cmd, s = nc.build(upstream=up, profile="docker", params_file=pf, resume=True)
    assert cmd[:2] == ["nextflow", "run"]
    assert "-profile" in cmd and "docker" in cmd
    assert "-params-file" in cmd and "-resume" in cmd
    assert cmd[2] == up.as_posix()
