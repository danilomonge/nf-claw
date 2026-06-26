from pathlib import Path

from runner import preflight
from runner.submodule import SubmoduleStatus


def _st(path, complete=True):
    return SubmoduleStatus("sarek", path, True, complete, "3.8.1", "abc",
                           () if complete else ("main.nf",))


def test_outdir_inside_repo_flagged(tmp_path, monkeypatch):
    # Inside the repo and NOT gitignored (tmp_path isn't even a git repo) → rejected.
    monkeypatch.setattr(preflight.shutil, "which", lambda x: "/usr/bin/" + x)
    inside = tmp_path / "results"
    issues = preflight.check_environment(profile="singularity", output_dir=inside,
                                         submodule=_st(tmp_path / "up"),
                                         repo_root=tmp_path, resume=False)
    assert any("outside the repo" in i for i in issues)


def test_outdir_gitignored_in_repo_allowed(tmp_path, monkeypatch):
    # A gitignored outdir (the documented `--outdir results`) is allowed inside the repo.
    import subprocess
    monkeypatch.setattr(preflight.shutil, "which", lambda x: "/usr/bin/" + x)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".gitignore").write_text("results/\n")
    issues = preflight.check_environment(profile="singularity", output_dir=tmp_path / "results",
                                         submodule=_st(tmp_path / "up"),
                                         repo_root=tmp_path, resume=False)
    assert not any("outdir" in i for i in issues)


def test_missing_nextflow_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(preflight.shutil, "which", lambda x: None)
    issues = preflight.check_environment(profile="docker",
                                         output_dir=tmp_path.parent / "out_xyz",
                                         submodule=_st(tmp_path / "up"),
                                         repo_root=tmp_path, resume=False)
    assert any("nextflow not found" in i for i in issues)


def _clean_env(monkeypatch):
    # tools present, docker daemon healthy — isolate the space check from unrelated issues
    monkeypatch.setattr(preflight.shutil, "which", lambda x: "/usr/bin/" + x)
    monkeypatch.setattr(preflight.subprocess, "run",
                        lambda *a, **k: type("R", (), {"returncode": 0})())


def test_space_in_repo_path_blocks(tmp_path, monkeypatch):
    _clean_env(monkeypatch)
    spaced = tmp_path / "draft 2"
    spaced.mkdir()
    issues = preflight.check_environment(profile="singularity", output_dir=tmp_path / "out_x",
                                         submodule=_st(spaced / "up"), repo_root=spaced,
                                         resume=False)
    assert any("repo path" in i and "space" in i and "--allow-spaces" in i for i in issues)


def test_space_in_outdir_blocks(tmp_path, monkeypatch):
    _clean_env(monkeypatch)
    issues = preflight.check_environment(profile="singularity", output_dir=tmp_path / "a b" / "out",
                                         submodule=_st(tmp_path / "up"), repo_root=tmp_path,
                                         resume=False)
    assert any("--outdir" in i and "space" in i for i in issues)


def test_space_in_work_dir_blocks(tmp_path, monkeypatch):
    _clean_env(monkeypatch)
    issues = preflight.check_environment(profile="singularity", output_dir=tmp_path / "out_x",
                                         submodule=_st(tmp_path / "up"), repo_root=tmp_path,
                                         resume=False, work_dir=Path("/scratch dir/work"))
    assert any("work directory" in i and "NXF_WORK" in i for i in issues)


def test_allow_spaces_overrides_the_block(tmp_path, monkeypatch):
    _clean_env(monkeypatch)
    spaced = tmp_path / "draft 2"
    spaced.mkdir()
    issues = preflight.check_environment(profile="singularity", output_dir=spaced / "out",
                                         submodule=_st(spaced / "up"), repo_root=spaced,
                                         resume=False, work_dir=Path("/x y/work"),
                                         allow_spaces=True)
    assert not any("space" in i for i in issues)


def test_no_spaces_no_block(tmp_path, monkeypatch):
    _clean_env(monkeypatch)
    issues = preflight.check_environment(profile="singularity", output_dir=tmp_path / "out_x",
                                         submodule=_st(tmp_path / "up"), repo_root=tmp_path,
                                         resume=False, work_dir=tmp_path / "work")
    assert not any("space" in i for i in issues)
