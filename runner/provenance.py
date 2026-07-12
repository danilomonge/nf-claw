from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from runner.outputs import is_nextflow_internal
from runner.submodule import SubmoduleStatus


_SENSITIVE_KEY_PARTS = ("TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "API_KEY",
                        "ACCESS_KEY", "PRIVATE_KEY", "AUTH")
_SENSITIVE_VALUE_RE = re.compile(
    r"(?i)(?:token|secret|password|credential|api[_-]?key|access[_-]?key|private[_-]?key)\s*[=:]"
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _nextflow_version(env_extra: dict[str, str] | None = None) -> str:
    # Probe with the same env overlay the run used, so a pinned NXF_VER reports the version that
    # actually ran, not the launcher default.
    env = {**os.environ, **env_extra} if env_extra else None
    try:
        r = subprocess.run(["nextflow", "-version"], capture_output=True,
                           text=True, timeout=30, env=env)
        return (r.stdout or r.stderr).strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return ""


def _sensitive_env(key: str, value: str) -> bool:
    upper = key.upper()
    return any(part in upper for part in _SENSITIVE_KEY_PARTS) or bool(
        _SENSITIVE_VALUE_RE.search(value)
    )


def _safe_env(env: dict[str, str] | None) -> tuple[dict[str, str], list[str]]:
    """Return provenance-safe values and the names whose values were redacted."""
    recorded: dict[str, str] = {}
    redacted: list[str] = []
    for key, value in sorted((env or {}).items()):
        if _sensitive_env(key, value):
            recorded[key] = "<redacted>"
            redacted.append(key)
        else:
            recorded[key] = value
    return recorded, redacted


def effective_nxf_env(env_extra: dict[str, str] | None = None) -> dict[str, str]:
    """Every NXF_* variable the run actually saw: inherited from the shell, then the overlay.

    Nextflow reads its settings from the ambient environment, so an exported NXF_OFFLINE or NXF_VER
    shapes the run just as much as `--nxf-env`/`--nxf-ver` does. Recording only the overlay would
    leave the replay script silently missing whatever made the run work.
    """
    env = {k: v for k, v in os.environ.items() if k.startswith("NXF_")}
    env.update(env_extra or {})        # the overlay wins, exactly as it does at launch
    return env


def write(*, outdir: Path, pipeline: str, command_str: str,
          submodule: SubmoduleStatus, input_paths: list[Path],
          env_extra: dict[str, str] | None = None,
          outcome: str = "success") -> Path:
    prov = outdir / "provenance"
    prov.mkdir(parents=True, exist_ok=True)

    nxf_env = effective_nxf_env(env_extra)
    recorded_env, redacted_env = _safe_env(nxf_env)
    manifest = {
        "pipeline": pipeline,
        "version": submodule.version,
        "commit": submodule.commit,
        "command": command_str,
        "outcome": outcome,
        "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nextflow": _nextflow_version(env_extra),
        "nextflow_env": recorded_env,
        "redacted_nextflow_env": redacted_env,
        "os": platform.platform(),
    }
    (prov / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    in_lines = [f"{_sha256(p)}  {p}" for p in input_paths if p.is_file()]
    (prov / "inputs.sha256").write_text("\n".join(in_lines) + ("\n" if in_lines else ""),
                                        encoding="utf-8")

    out_lines = [f"{_sha256(p)}  {rel}"
                 for p in sorted(outdir.rglob("*"))
                 if p.is_file() and prov not in p.parents
                 and not is_nextflow_internal(rel := p.relative_to(outdir))]
    (prov / "outputs.sha256").write_text("\n".join(out_lines) + ("\n" if out_lines else ""),
                                         encoding="utf-8")

    sv = outdir / "pipeline_info" / "software_versions.yml"
    if sv.exists():
        shutil.copy2(sv, prov / "software_versions.yml")

    # A faithful, self-contained replay:
    #  - `cd` to the outdir first: nfclaw launches Nextflow from there, so re-running this lands the
    #    engine state (.nextflow/) in the same place;
    #  - re-export every NXF_* variable the run actually saw: the overlay nfclaw applied (--nxf-ver,
    #    --nxf-env) *and* whatever the shell already exported (NXF_OFFLINE, NXF_VER, …). Nextflow
    #    reads all of them, so a run that only succeeds with a pinned engine, an IPv6 flag or offline
    #    mode would not reproduce unless the script carries them — the manifest alone is not enough.
    # `--config` files are already in `command_str` (as `-c <path>`), so they replay as-is.
    env_exports = "".join(
        f"export {key}={shlex.quote(value)}\n"
        for key, value in sorted(nxf_env.items())
        if key not in redacted_env
    )
    if redacted_env:
        names = " ".join(redacted_env)
        env_exports += ("# Sensitive values were omitted from provenance. Export these before "
                        f"replay: {names}\n")
    commands = prov / "commands.sh"
    commands.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\n"
        f"cd {shlex.quote(str(outdir))}\n"
        f"{env_exports}{command_str}\n", encoding="utf-8")
    commands.chmod(0o755)                             # so the documented replay works as `./commands.sh`
    return prov
