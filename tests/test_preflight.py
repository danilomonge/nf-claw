from runner import preflight
from runner.submodule import SubmoduleStatus


def _st(path, complete=True):
    return SubmoduleStatus("sarek", path, True, complete, "3.8.1", "abc",
                           () if complete else ("main.nf",))


def test_outdir_inside_repo_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(preflight.shutil, "which", lambda x: "/usr/bin/" + x)
    inside = tmp_path / "results"
    issues = preflight.check_environment(profile="docker", output_dir=inside,
                                         submodule=_st(tmp_path / "up"),
                                         repo_root=tmp_path, resume=False)
    assert any("outside the repo" in i for i in issues)


def test_missing_nextflow_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(preflight.shutil, "which", lambda x: None)
    issues = preflight.check_environment(profile="docker",
                                         output_dir=tmp_path.parent / "out_xyz",
                                         submodule=_st(tmp_path / "up"),
                                         repo_root=tmp_path, resume=False)
    assert any("nextflow not found" in i for i in issues)
