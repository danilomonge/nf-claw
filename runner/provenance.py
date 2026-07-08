from __future__ import annotations

import hashlib
import json
import os
import platform
import shlex
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from runner.outputs import is_nextflow_internal
from runner.submodule import SubmoduleStatus


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


def write(*, outdir: Path, pipeline: str, command_str: str,
          submodule: SubmoduleStatus, input_paths: list[Path],
          env_extra: dict[str, str] | None = None) -> Path:
    prov = outdir / "provenance"
    prov.mkdir(parents=True, exist_ok=True)

    manifest = {
        "pipeline": pipeline,
        "version": submodule.version,
        "commit": submodule.commit,
        "command": command_str,
        "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "nextflow": _nextflow_version(env_extra),
        "nextflow_env": dict(env_extra or {}),       # NXF_* overrides nfclaw applied (for replay)
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
    #  - re-export the exact NXF_* overrides the run applied (the engine pin from --nxf-ver, plus any
    #    --nxf-env such as NXF_JVM_ARGS on an IPv6 host or NXF_OFFLINE). A run that only succeeds with
    #    a pinned engine or one of these flags would not reproduce without them, so the replay script
    #    must carry them — recording them only in the manifest is not enough.
    # `--config` files are already in `command_str` (as `-c <path>`), so they replay as-is.
    env_exports = "".join(f"export {key}={shlex.quote(value)}\n"
                          for key, value in sorted((env_extra or {}).items()))
    commands = prov / "commands.sh"
    commands.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\n"
        f"cd {shlex.quote(str(outdir))}\n"
        f"{env_exports}{command_str}\n", encoding="utf-8")
    commands.chmod(0o755)                             # so the documented replay works as `./commands.sh`
    return prov
