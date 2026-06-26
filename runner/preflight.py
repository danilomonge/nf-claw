from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from runner.submodule import SubmoduleStatus


def check_environment(*, profile: str, output_dir: Path, submodule: SubmoduleStatus,
                      repo_root: Path, resume: bool, work_dir: Path | None = None,
                      allow_spaces: bool = False) -> list[str]:
    issues: list[str] = []
    for tool, hint in (("git", ""), ("nextflow", ""), ("java", " (Nextflow needs Java 17+)")):
        if shutil.which(tool) is None:
            issues.append(f"{tool} not found on PATH{hint}")
    tokens = {t.strip() for t in profile.split(",")}
    if "docker" in tokens and shutil.which("docker") is None:
        issues.append("profile uses docker but docker not found on PATH")
    if "singularity" in tokens and not (shutil.which("singularity") or shutil.which("apptainer")):
        issues.append("profile uses singularity but singularity/apptainer not found")
    if "docker" in tokens and shutil.which("docker"):
        try:
            ok = subprocess.run(["docker", "info"], capture_output=True, timeout=10).returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            ok = False
        if not ok:
            issues.append("docker daemon not responding (is Docker running?)")
    if not submodule.complete:
        issues.append(f"pipeline submodule incomplete: missing {list(submodule.missing_files)}")
    try:
        output_dir.resolve().relative_to(repo_root.resolve())
    except ValueError:
        pass                                                  # outside the repo — fine
    else:
        # Inside the repo is OK only if git ignores it (so run outputs never pollute tracked
        # files or trip the drift gate) — this is what lets the documented `--outdir results`
        # work. Probe a child path so a directory-only rule (`results/`) still matches.
        try:
            ignored = subprocess.run(
                ["git", "-C", str(repo_root), "check-ignore", "-q", str(output_dir / "_probe")],
                capture_output=True, timeout=10).returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            ignored = False
        if not ignored:
            issues.append(f"--outdir must be outside the repo or a gitignored path (got {output_dir})")
    if output_dir.exists() and any(output_dir.iterdir()) and not resume:
        issues.append(f"--outdir is not empty: {output_dir} (use -resume or a fresh dir)")
    issues += _space_issues(repo_root=repo_root, output_dir=output_dir,
                            work_dir=work_dir, allow_spaces=allow_spaces)
    return issues


def _space_issues(*, repo_root: Path, output_dir: Path, work_dir: Path | None,
                  allow_spaces: bool) -> list[str]:
    """Fail-fast, deterministic: a space in the repo tree, the Nextflow work directory or the
    output path breaks many bioinformatics tools (they build shell commands without quoting
    their work paths) and Docker on macOS outright. A path either contains a space or it does
    not — there is no heuristic here. `--allow-spaces` is the explicit opt-out."""
    if allow_spaces:
        return []
    issues: list[str] = []
    for label, path in (("the repo path", repo_root),
                        ("the Nextflow work directory", work_dir),
                        ("--outdir", output_dir)):
        if path is None or " " not in str(path):
            continue
        fix = ("set the work directory off it with --nxf-env NXF_WORK=/a/space-free/dir"
               if "work" in label else "use a space-free path")
        issues.append(f"{label} contains a space: {path} — bioinformatics tools and Nextflow's "
                      f"work directory mishandle spaces (Docker on macOS fails outright). "
                      f"{fix}, or pass --allow-spaces to run anyway.")
    return issues
