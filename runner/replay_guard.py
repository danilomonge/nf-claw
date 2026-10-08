"""Standalone checksum handling, copied into each provenance bundle for replay guards.

This module deliberately needs only Python's standard library: a recorded replay must not import
whatever version of nfclaw happens to be installed later.
"""
from __future__ import annotations

import glob
import errno
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def host_identity() -> str | None:
    """A hashed machine identity independent of DHCP/DNS hostname changes.

    Linux also includes the PID namespace, since a copied container log's PID
    cannot be inspected from a different namespace. Unknown systems fall back
    to the legacy hostname check; never invent an identity when probing fails.
    """
    identity = None
    if sys.platform == "linux":
        for name in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
            try:
                machine = Path(name).read_text(encoding="ascii").strip().lower()
                namespace = Path("/proc/self/ns/pid").stat().st_ino
            except (OSError, UnicodeError):
                continue
            if re.fullmatch(r"[0-9a-f]{32}", machine) and machine != "0" * 32:
                identity = f"{machine}:{namespace}"
                break
    elif sys.platform == "darwin":
        try:
            result = subprocess.run(["/usr/sbin/ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                                    capture_output=True, text=True, timeout=2)
            match = re.search(r'"IOPlatformUUID"\s*=\s*"([0-9A-Fa-f-]{36})"', result.stdout)
            if result.returncode == 0 and match:
                identity = match.group(1).lower()
        except (OSError, subprocess.SubprocessError):
            pass
    return (hashlib.sha256(f"nfclaw-host-v1:{sys.platform}:{identity}".encode()).hexdigest()
            if identity is not None else None)


def read_checksums(path: Path, *, relative: bool = True) -> dict[str, str]:
    """Read a manifest; malformed/duplicate paths raise ValueError, I/O retains OSError."""
    out: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        digest, separator, name = line.partition("  ")
        parts = name.split("/")
        absolute = name.startswith("/")
        valid_path = bool(name) and "\x00" not in name and not any(
            p in (".", "..", "") for p in (parts[1:] if absolute else parts)
        ) and not (relative and absolute)
        if not separator or not re.fullmatch(r"[0-9a-fA-F]{64}", digest) or not valid_path:
            raise ValueError(f"invalid checksum record in {path} at line {number}")
        if name in out:
            raise ValueError(f"duplicate checksum path {name!r} in {path} at line {number}")
        out[name] = digest.lower()
    return out


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _glob_patterns(pattern: str) -> list[str]:
    """Expand Java/Nextflow brace alternatives and its recursive ``**.ext`` shorthand."""
    if match := re.search(r"\{([^{}]+)\}", pattern):
        return [expanded for option in match[1].split(",")
                for expanded in _glob_patterns(pattern[:match.start()] + option + pattern[match.end():])]
    return [re.sub(r"(?<=/)\*\*(?=[^/])", "**/*", pattern)]


def input_files(paths: list[Path]) -> list[Path]:
    """Expand explicit files, directories and globs, with cycle-safe symlink traversal."""
    files: set[Path] = set()

    def walk(directory: Path, ancestors: frozenset[Path]) -> None:
        real = directory.resolve()
        if real in ancestors:
            raise OSError(errno.ELOOP, "cyclic input directory symlink", str(directory))
        with os.scandir(directory) as entries:
            for entry in sorted(entries, key=lambda e: e.name):
                item = directory / entry.name
                if entry.is_dir(follow_symlinks=True):
                    walk(item, ancestors | {real})
                elif entry.is_file(follow_symlinks=True):
                    files.add(item)
                else:
                    raise FileNotFoundError(f"input is missing or not a regular file: {item}")

    for source in paths:
        source = source.expanduser().absolute()
        pattern = str(source)
        if source.exists():
            matches = [source]
        elif glob.has_magic(pattern) or "{" in pattern:
            matches = sorted({Path(p) for expanded in _glob_patterns(pattern)
                              for p in glob.glob(expanded, recursive=True)})
        else:
            matches = [source]
        if not matches:
            raise FileNotFoundError(f"input pattern matches no files: {source}")
        for path in matches:
            if path.is_file():
                files.add(path)
            elif path.is_dir():
                # Track ancestors per branch, not a global set of resolved directories: a second
                # published alias is a second logical input path and can change sample multiplicity.
                walk(path, frozenset())
            else:
                raise FileNotFoundError(f"input is missing or not a regular file: {path}")
    return sorted(files)


def hash_inputs(paths: list[Path]) -> dict[str, str]:
    """Content snapshot of local sources, including directory and glob contents."""
    return {str(path): _sha256(path) for path in input_files(paths)}


def pipeline_head(repo: Path) -> str | None:
    """HEAD only when repo is the exact working-tree root, never a surrounding repository."""
    try:
        result = subprocess.run(["git", "-C", str(repo), "rev-parse", "--show-toplevel", "HEAD"],
                                capture_output=True, text=True, check=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    lines = result.stdout.strip().splitlines()
    if len(lines) == 2 and Path(lines[0]).resolve() == repo.resolve():
        return lines[1]
    return None


def hash_pipeline(repo: Path) -> dict[str, str]:
    """Snapshot every tracked source file's working bytes, including dirty modifications.

    For fixtures without their own git repository, snapshot the directory contents except .git.
    Tracked inventory changes are detected even if HEAD stays unchanged.
    """
    if pipeline_head(repo) is not None:
        result = subprocess.run(["git", "-C", str(repo), "ls-files", "--cached", "-z"],
                                capture_output=True, text=True, check=True, timeout=30)
        paths = [repo / name for name in result.stdout.split("\x00") if name]
    else:
        paths = [path for path in input_files([repo]) if ".git" not in path.relative_to(repo).parts]
    return {path.relative_to(repo).as_posix(): _sha256(path) for path in sorted(set(paths))}


def verify_dependencies(bundle: Path) -> None:
    """Require the recorded local input inventory and config bytes before replay starts."""
    manifest = json.loads((bundle / "run_manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or not isinstance(manifest.get("outcome"), str):
        raise ValueError(f"provenance bundle is incomplete: {bundle}")
    if pipeline_path := manifest.get("pipeline_path"):
        repo = Path(pipeline_path)
        if (expected_head := manifest.get("pipeline_git_head")) is not None \
                and pipeline_head(repo) != expected_head:
            raise ValueError(f"pipeline revision changed: {repo} (expected {expected_head})")
        expected = read_checksums(bundle / "pipeline.sha256")
        current = hash_pipeline(repo)
        if current.keys() != expected.keys():
            raise ValueError(f"pipeline source inventory changed: {repo}")
        for name, digest in expected.items():
            if current[name] != digest:
                raise ValueError(f"pipeline source content changed: {repo / name}")
    for kind in ("inputs", "configs"):
        expected = read_checksums(bundle / f"{kind}.sha256", relative=False)
        sources = json.loads((bundle / f"{kind}.sources.json").read_text(encoding="utf-8"))
        if not isinstance(sources, list) or not all(isinstance(p, str) for p in sources):
            raise ValueError(f"invalid {kind} sources in {bundle}")
        # Keep original logical checksum keys, but find moved internal configs in this bundle.
        recorded_bundle = None
        if kind == "configs" and isinstance(manifest.get("outdir"), str):
            recorded_bundle = Path(manifest["outdir"]) / "provenance"
        current_files = {}
        for source in sources:
            path = Path(source)
            relocated = path
            if recorded_bundle is not None and path.is_relative_to(recorded_bundle):
                relocated = bundle / path.relative_to(recorded_bundle)
            for current in input_files([relocated]):
                logical = (recorded_bundle / current.relative_to(bundle)
                           if relocated != path else current)
                current_files[str(logical)] = current
        missing = sorted(expected.keys() - current_files.keys())
        extra = sorted(current_files.keys() - expected.keys())
        if missing or extra:
            raise ValueError(f"{kind} inventory changed; missing: {missing}; extra: {extra}")
        for name, path in current_files.items():
            if _sha256(path) != expected[name]:
                raise ValueError(f"recorded {kind} content changed: {name}")


def lock_replay(target: Path, script: Path) -> None:
    """Hold the runner's sibling flock across exec of the replay shell, with no extra parent.

    The shell keeps the inherited descriptor until its traps, logs and tasks have finished.
    Using exactly the runner's lock prevents replay/replay and replay/run writer races.
    """
    import fcntl

    target = target.expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    lock = target.parent / f".{target.name}.nfclaw.lock"
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError(f"another nfclaw run or replay is active in {target}") from None
        os.set_inheritable(fd, True)
        env = {**os.environ, "NFCLAW_REPLAY_LOCK_PID": str(os.getpid())}
        os.execvpe("bash", ["bash", str(script), str(target)], env)
    finally:
        os.close(fd)


if __name__ == "__main__":
    try:
        if sys.argv[1] == "--host-id":
            print(host_identity() or "")
        elif sys.argv[1] == "--lock":
            lock_replay(Path(sys.argv[2]), Path(sys.argv[3]))
        else:
            verify_dependencies(Path(sys.argv[1]))
    except (OSError, ValueError, IndexError) as exc:
        print(f"nfclaw replay: dependency check failed: {exc}", file=sys.stderr)
        sys.exit(1)
