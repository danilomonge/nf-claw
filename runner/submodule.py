from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from runner.errors import ErrorCode, NfclawError

REQUIRED_FILES = ("main.nf", "nextflow.config", "nextflow_schema.json")
_GIT_TIMEOUT = 30


@dataclass(frozen=True)
class SubmoduleStatus:
    name: str
    path: Path
    initialized: bool
    complete: bool
    version: str
    commit: str
    missing_files: tuple[str, ...]


def _git(path: Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=str(path), capture_output=True,
                             text=True, timeout=_GIT_TIMEOUT, check=True)
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return ""
    return out.stdout.strip()


def resolve(name: str, pipelines_dir: Path) -> SubmoduleStatus:
    path = pipelines_dir / name / "upstream"
    initialized = path.is_dir() and any(path.iterdir())
    missing = tuple(f for f in REQUIRED_FILES if not (path / f).exists())
    commit = _git(path, "rev-parse", "HEAD") if initialized else ""
    version = _git(path, "describe", "--tags", "--always") if initialized else ""
    return SubmoduleStatus(
        name=name, path=path, initialized=initialized,
        complete=initialized and not missing,
        version=version, commit=commit, missing_files=missing,
    )


def ensure_initialized(name: str, pipelines_dir: Path, repo_root: Path) -> SubmoduleStatus:
    st = resolve(name, pipelines_dir)
    if not st.initialized:
        rel = f"pipelines/{name}/upstream"
        subprocess.run(["git", "submodule", "update", "--init", "--depth", "1", rel],
                       cwd=str(repo_root), check=True)
        st = resolve(name, pipelines_dir)
    if not st.complete:
        raise NfclawError(
            ErrorCode.SUBMODULE_INCOMPLETE,
            f"Pipeline '{name}' submodule is incomplete.",
            fix=f"Run: git submodule update --init pipelines/{name}/upstream",
            details={"missing": list(st.missing_files)},
        )
    return st
