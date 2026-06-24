"""Resolve and materialize a *specific* released version of a pipeline.

`nfclaw` pins each pipeline's submodule to its latest release. This module lets a
user run any other published release tag instead: it validates the requested tag
against the real upstream tags, checks it out into a git-ignored per-version cache
(a worktree sharing the submodule's object store), and returns a `SubmoduleStatus`
pointing at that tree — the same value the rest of the runner already consumes for
the pinned version. The default (no version) path is unchanged.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path

from runner import discovery
from runner import submodule as submod
from runner.errors import ErrorCode, NfclawError
from runner.submodule import SubmoduleStatus

CACHE_DIRNAME = ".versions"
_SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
_GIT_TIMEOUT = 120


# --- discovering which versions exist ---------------------------------------

def _url_for(name: str, repo_root: Path) -> str | None:
    """The submodule's git URL from `.gitmodules` — read offline, no git needed."""
    try:
        text = (repo_root / ".gitmodules").read_text(encoding="utf-8")
    except OSError:
        return None
    section = f'[submodule "pipelines/{name}/upstream"]'
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() != section:
            continue
        for follow in lines[i + 1:]:
            s = follow.strip()
            if s.startswith("["):                      # next section — url not in this one
                break
            if s.startswith("url"):
                return s.split("=", 1)[1].strip()
    return None


def remote_tags(url: str) -> list[str]:
    """Tag names published by the upstream remote (empty on any failure — caller falls back)."""
    try:
        r = subprocess.run(["git", "ls-remote", "--tags", "--refs", url],
                           capture_output=True, text=True, timeout=60)
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return []
    if r.returncode != 0:
        return []
    return [line.split("\t")[-1].rsplit("/", 1)[-1] for line in r.stdout.splitlines()]


def _local_tags(upstream: Path) -> list[str]:
    """Tags already present in the (initialized) submodule clone — the offline fallback."""
    out = submod._git(upstream, "tag", "--list")
    return out.splitlines() if out else []


def _semver_key(tag: str) -> tuple[int, int, int]:
    m = _SEMVER.match(tag)
    return tuple(int(x) for x in m.groups()) if m else (0, 0, 0)


def release_tags(name: str, *, pipelines_dir: Path, repo_root: Path) -> list[str]:
    """Every semver release tag for the pipeline, newest first.

    Union of the remote's tags and any already fetched locally, so it still returns
    a useful list when the network is unavailable. Non-semver refs (dev, rc, …) are
    dropped — only immutable releases are runnable.
    """
    url = _url_for(name, repo_root)
    tags = list(remote_tags(url)) if url else []
    tags += _local_tags(pipelines_dir / name / "upstream")
    semver = {t for t in tags if _SEMVER.match(t)}
    return sorted(semver, key=_semver_key, reverse=True)


def available(name: str, *, pipelines_dir: Path, repo_root: Path) -> list[tuple[str, bool]]:
    """`(tag, is_pin)` for every release, newest first. The pin is the committed
    (latest) version from the pipeline's skill.md — known offline, no init required."""
    pipeline = discovery.find(name, pipelines_dir)             # 404 if unknown
    pin = pipeline.frontmatter.get("version", "").lstrip("v")
    tags = release_tags(name, pipelines_dir=pipelines_dir, repo_root=repo_root)
    return [(t, t.lstrip("v") == pin) for t in tags]


# --- resolving a requested version to a canonical tag -----------------------

def _match_tag(version: str, tags: list[str]) -> str | None:
    """The actual tag matching the user's input, tolerating a leading 'v' on either side."""
    want = version.strip().lstrip("v")
    for tag in tags:
        if tag.lstrip("v") == want:
            return tag
    return None


def resolve(name: str, version: str, *, pipelines_dir: Path, repo_root: Path) -> str:
    """Validate `version` against the real release tags, returning the canonical tag.
    Raises VERSION_NOT_FOUND (listing what is available) for anything else."""
    tags = release_tags(name, pipelines_dir=pipelines_dir, repo_root=repo_root)
    match = _match_tag(version, tags)
    if match is None:
        raise NfclawError(
            ErrorCode.VERSION_NOT_FOUND,
            f"'{version}' is not a released version of nf-core/{name}.",
            fix=f"Pick an available version (see `nfclaw versions {name}`), "
                "or omit --pipeline-version to use the pinned latest.",
            details={"available": tags or ["(none found — check network connectivity)"]},
        )
    return match


# --- materializing a version into the per-version cache ---------------------

def cache_dir(name: str, tag: str, pipelines_dir: Path) -> Path:
    return pipelines_dir / name / CACHE_DIRNAME / tag


def is_cached(st: SubmoduleStatus) -> bool:
    """True when the status points at a materialized version, not the pinned submodule."""
    return CACHE_DIRNAME in st.path.parts


def _has_tag(upstream: Path, tag: str) -> bool:
    return bool(submod._git(upstream, "rev-parse", "-q", "--verify", f"refs/tags/{tag}"))


def _fetch_tag(upstream: Path, tag: str) -> None:
    subprocess.run(
        ["git", "-C", str(upstream), "fetch", "--depth", "1", "origin",
         f"refs/tags/{tag}:refs/tags/{tag}"],
        check=True, capture_output=True, text=True, timeout=_GIT_TIMEOUT)


def _add_worktree(upstream: Path, dest: Path, tag: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(upstream), "worktree", "prune"],
                   check=False, capture_output=True, text=True, timeout=30)
    if dest.exists():                                          # stale/partial — start clean
        shutil.rmtree(dest)
    subprocess.run(
        ["git", "-C", str(upstream), "worktree", "add", "--force", "--detach",
         str(dest), f"tags/{tag}"],
        check=True, capture_output=True, text=True, timeout=_GIT_TIMEOUT)


def materialize(name: str, tag: str, *, pipelines_dir: Path, repo_root: Path) -> SubmoduleStatus:
    """Ensure `tag` is checked out at `cache_dir(name, tag)/upstream` and return its status.
    Reuses the submodule's object store; fetches the tag only if it isn't present yet."""
    upstream = pipelines_dir / name / "upstream"
    dest = cache_dir(name, tag, pipelines_dir) / "upstream"
    if not (dest / "main.nf").exists():                       # not materialized yet
        if not _has_tag(upstream, tag):
            _fetch_tag(upstream, tag)
        _add_worktree(upstream, dest, tag)
    st = submod.resolve_at(name, dest)
    if not st.complete:
        raise NfclawError(
            ErrorCode.SUBMODULE_INCOMPLETE,
            f"Materialized tree for nf-core/{name}@{tag} is incomplete.",
            fix="The release may be missing required files; try a different version.",
            details={"missing": list(st.missing_files)})
    return replace(st, version=tag)                           # the tag is the authoritative version


# --- the single entry point the runner uses --------------------------------

def ensure(name: str, version: str | None, *, pipelines_dir: Path,
           repo_root: Path) -> SubmoduleStatus:
    """Status for the tree to run: the pinned submodule when `version` is None or equals
    the pin, otherwise the requested release materialized into the cache."""
    if version is None:
        return submod.ensure_initialized(name, pipelines_dir, repo_root)
    base = submod.ensure_initialized(name, pipelines_dir, repo_root)
    tag = resolve(name, version, pipelines_dir=pipelines_dir, repo_root=repo_root)
    if tag.lstrip("v") == base.version.lstrip("v"):
        return base                                            # requested == pin → no cache needed
    return materialize(name, tag, pipelines_dir=pipelines_dir, repo_root=repo_root)


# --- on-demand docs for a materialized version -----------------------------

def generate_docs(st: SubmoduleStatus, *, dest_dir: Path) -> tuple[Path, Path]:
    """Write `skill.md`/`reference.md` for a version's tree, reusing the librarian's
    renderer. Imported lazily so the runtime never hard-depends on the librarian."""
    from librarian import write_skill                          # lazy: avoid runner→librarian coupling
    version = st.version if is_cached(st) else None             # version-aware commands only for a cache
    skill_text, ref_text = write_skill.render_status(st, pipeline_version=version)
    dest_dir.mkdir(parents=True, exist_ok=True)
    skill_path = dest_dir / "skill.md"
    ref_path = dest_dir / "reference.md"
    skill_path.write_text(skill_text, encoding="utf-8")
    ref_path.write_text(ref_text, encoding="utf-8")
    return skill_path, ref_path
