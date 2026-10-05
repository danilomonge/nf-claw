from __future__ import annotations

import contextlib
import hashlib
import os
import re
import subprocess
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path

from runner.errors import ErrorCode, NfclawError

try:
    import fcntl                                  # POSIX file locks (macOS/Linux)
except ImportError:                              # pragma: no cover — Windows has no fcntl
    fcntl = None

REQUIRED_FILES = ("main.nf", "nextflow.config", "nextflow_schema.json")
_GIT_TIMEOUT = 30
_INIT_TIMEOUT = 300
_HEX_RE = re.compile(r"^[0-9a-f]{7,40}$")
_THREAD_LOCKS: dict[str, threading.Lock] = {}
_THREAD_LOCKS_GUARD = threading.Lock()


def _thread_lock(key: str) -> threading.Lock:
    with _THREAD_LOCKS_GUARD:
        return _THREAD_LOCKS.setdefault(key, threading.Lock())


def _lock_path(repo_root: Path) -> Path:
    """Where the submodule lock lives: in the repository's own git directory, which every process
    initialising this clone's submodules writes to anyway. Never the shared temp directory, where a
    file another user left blocked every first-time run and a planted symlink could redirect it."""
    common = _git(repo_root, "rev-parse", "--git-common-dir")
    if common:
        git_dir = Path(common)
        if not git_dir.is_absolute():
            git_dir = repo_root / git_dir
        if git_dir.is_dir():
            return git_dir / "nfclaw-submodule.lock"
    # Not a git checkout (submodule init will then fail on its own): a per-user temp lock.
    key = hashlib.sha256(str(repo_root.resolve()).encode()).hexdigest()[:16]
    uid = os.getuid() if hasattr(os, "getuid") else 0
    return Path(tempfile.gettempdir()) / f"nfclaw-submodule-{uid}-{key}.lock"


@contextlib.contextmanager
def _init_lock(repo_root: Path):
    """Serialize `git submodule update` across concurrent nfclaw processes on the same repo.
    Without it, parallel inits race on `.git/config` ("could not lock config file"). The lock is an
    flock on a file in the repository's git directory (see `_lock_path`) — it never touches the
    working tree, and it is opened without following symlinks or truncating anything. Thread-only
    where flock is unavailable (Windows)."""
    key = hashlib.sha256(str(repo_root.resolve()).encode()).hexdigest()[:16]
    if fcntl is None:
        with _thread_lock(key):
            yield
        return
    with _thread_lock(key):
        lock_path = _lock_path(repo_root)
        try:
            fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o666)
        except OSError as exc:
            raise NfclawError(
                ErrorCode.ENVIRONMENT,
                f"Could not open the submodule lock file {lock_path}: {exc.strerror or exc}",
                fix="If no other nfclaw process is running, remove it (it must be a regular file "
                    "you can write), then retry.") from exc
        try:
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


@dataclass(frozen=True)
class SubmoduleStatus:
    name: str
    path: Path
    initialized: bool
    complete: bool
    version: str
    commit: str
    missing_files: tuple[str, ...]
    # Advisories about how this tree was resolved (e.g. it is unreleased `dev` code), surfaced to
    # the caller as run warnings. Empty for the pinned release and for any other release tag.
    notes: tuple[str, ...] = ()


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
    st = resolve_at(name, pipelines_dir / name / "upstream")
    pinned = _committed_pin(pipelines_dir / name / "skill.md")
    if (pinned and st.commit and st.commit == pinned.get("commit")
            and _looks_like_commit_version(st.version, st.commit)):
        return SubmoduleStatus(
            name=st.name, path=st.path, initialized=st.initialized,
            complete=st.complete, version=pinned["version"], commit=st.commit,
            missing_files=st.missing_files,
        )
    return st


def _looks_like_commit_version(version: str, commit: str) -> bool:
    return bool(version and _HEX_RE.match(version) and commit.startswith(version))


def _committed_pin(skill_md: Path) -> dict[str, str] | None:
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith("---\n"):
        return None
    frontmatter = text.split("---", 2)[1]
    data: dict[str, str] = {}
    for line in frontmatter.splitlines():
        key, sep, value = line.partition(":")
        if sep and key.strip() in {"version", "commit"}:
            data[key.strip()] = value.strip()
    return data if data.get("version") and data.get("commit") else None


def ensure_initialized(name: str, pipelines_dir: Path, repo_root: Path) -> SubmoduleStatus:
    st = resolve(name, pipelines_dir)
    if not st.complete:
        rel = f"pipelines/{name}/upstream"
        with _init_lock(repo_root):
            st = resolve(name, pipelines_dir)               # re-check: another run may have just done it
            if not st.complete:
                try:
                    subprocess.run(
                        ["git", "submodule", "update", "--init", "--depth", "1", rel],
                        cwd=str(repo_root), check=True, capture_output=True, text=True,
                        timeout=_INIT_TIMEOUT,
                    )
                except (subprocess.SubprocessError, FileNotFoundError, OSError) as exc:
                    detail = getattr(exc, "stderr", "") or str(exc)
                    raise NfclawError(
                        ErrorCode.SUBMODULE_INCOMPLETE,
                        f"Could not initialize pipeline '{name}' submodule.",
                        fix=f"Check network access, then run: git submodule update --init {rel}",
                        details={"git_error": detail.strip()},
                    ) from exc
                st = resolve(name, pipelines_dir)
    if not st.complete:
        raise NfclawError(
            ErrorCode.SUBMODULE_INCOMPLETE,
            f"Pipeline '{name}' submodule is incomplete.",
            fix=f"Run: git submodule update --init pipelines/{name}/upstream",
            details={"missing": list(st.missing_files)},
        )
    return st
