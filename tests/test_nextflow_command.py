from runner import nextflow_command as nc

def test_compose_profile_orders_test_first_modifiers_last():
    assert nc.compose_profile("docker", demo=True, modifiers=("arm64",)) == "test,docker,arm64"

def test_compose_profile_dedups():
    assert nc.compose_profile("docker,docker") == "docker"

def test_build_command_shape(tmp_path):
    up = tmp_path / "upstream"
    up.mkdir()
    pf = tmp_path / "params.json"
    pf.write_text("{}")
    cmd, s = nc.build(upstream=up, profile="docker", params_file=pf, resume=True)
    assert cmd[:2] == ["nextflow", "run"]
    assert "-profile" in cmd and "docker" in cmd
    assert "-params-file" in cmd and "-resume" in cmd
    assert cmd[2] == up.as_posix()


def test_command_never_carries_a_positional_argument(tmp_path):
    # nf-core pipelines reject positional arguments (anything not behind a flag), and sarek's
    # nf-core-utils plugin warns naming the offending token. nfclaw must never be the source of one:
    # the command is built as an argv list and handed to Popen without a shell, so nothing can be
    # word-split or glob-expanded into an extra token. This pins that as an invariant.
    cmd, _ = nc.build(
        upstream=tmp_path / "up", profile="test,docker",
        params_file=tmp_path / "params.json", resume=True,
        work_dir=tmp_path / "work", extra_configs=(tmp_path / "extra.config",))
    assert cmd[0:2] == ["nextflow", "run"]
    assert cmd[2] == (tmp_path / "up").as_posix()          # the pipeline — the only bare argument
    # Every remaining token is either an option or the value directly after one.
    rest = cmd[3:]
    i = 0
    while i < len(rest):
        assert rest[i].startswith("-"), f"positional argument in the command: {rest[i]!r}"
        i += 1 if rest[i] == "-resume" else 2              # flags take no value; options take one
    assert i == len(rest)
