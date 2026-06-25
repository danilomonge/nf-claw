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


def test_space_advisory_flags_spaces_in_paths():
    from pathlib import Path
    adv = preflight.space_advisories(submodule=_st(Path("/vol/draft 2/up")),
                                     output_dir=Path("/clean/out"))
    assert len(adv) == 1 and "space" in adv[0].lower() and "NXF_WORK" in adv[0]


def test_space_advisory_silent_without_spaces():
    from pathlib import Path
    assert preflight.space_advisories(submodule=_st(Path("/clean/up")),
                                      output_dir=Path("/clean/out")) == []
