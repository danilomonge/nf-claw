from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from runner.submodule import SubmoduleStatus


def check_environment(*, profile: str, output_dir: Path, submodule: SubmoduleStatus,
                      repo_root: Path, resume: bool) -> list[str]:
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
    if sys.platform == "darwin" and "docker" in tokens and \
       (" " in str(submodule.path) or " " in str(output_dir)):
        issues.append("path contains spaces; Docker on macOS fails (errno 35). "
                      "Use a space-free path or Singularity.")
    return issues
