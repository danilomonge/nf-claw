from __future__ import annotations

import contextlib
import hashlib
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from runner.errors import ErrorCode, NfclawError

try:
    import fcntl                                  # POSIX file locks (macOS/Linux)
except ImportError:                              # pragma: no cover — Windows has no fcntl
    fcntl = None

REQUIRED_FILES = ("main.nf", "nextflow.config", "nextflow_schema.json")
_GIT_TIMEOUT = 30


@contextlib.contextmanager
def _init_lock(repo_root: Path):
    """Serialize `git submodule update` across concurrent nfclaw processes on the same repo.
    Without it, parallel inits race on `.git/config` ("could not lock config file"). The lock
    is an flock on a per-repo temp file — it never touches the working tree. No-op where flock
    is unavailable (Windows)."""
    if fcntl is None:
        yield
        return
    key = hashlib.sha256(str(repo_root.resolve()).encode()).hexdigest()[:16]
    lock_path = Path(tempfile.gettempdir()) / f"nfclaw-submodule-{key}.lock"
    with open(lock_path, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


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


def resolve_at(name: str, path: Path) -> SubmoduleStatus:
    """Status of a checked-out pipeline tree at an explicit path — works for the pinned
    submodule and for any materialized version worktree alike."""
    initialized = path.is_dir() and any(path.iterdir())
    missing = tuple(f for f in REQUIRED_FILES if not (path / f).exists())
    commit = _git(path, "rev-parse", "HEAD") if initialized else ""
    version = _git(path, "describe", "--tags", "--always") if initialized else ""
    return SubmoduleStatus(
        name=name, path=path, initialized=initialized,
        complete=initialized and not missing,
        version=version, commit=commit, missing_files=missing,
    )


def resolve(name: str, pipelines_dir: Path) -> SubmoduleStatus:
    return resolve_at(name, pipelines_dir / name / "upstream")


def ensure_initialized(name: str, pipelines_dir: Path, repo_root: Path) -> SubmoduleStatus:
    st = resolve(name, pipelines_dir)
    if not st.initialized:
        rel = f"pipelines/{name}/upstream"
        with _init_lock(repo_root):
            st = resolve(name, pipelines_dir)               # re-check: another run may have just done it
            if not st.initialized:
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
