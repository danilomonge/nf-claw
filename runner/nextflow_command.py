from __future__ import annotations

import shlex
from pathlib import Path


# The nf-core template's profiles for choosing a container engine or a runtime tweak. Across every
# pinned release none of them sets a required parameter (some set optional ones, e.g. `enable_conda`,
# `arm`, `use_gpu`), unlike `test*` or an institutional profile, which can set `--input` and the like.
ENGINE_PROFILES = frozenset({
    "docker", "singularity", "apptainer", "podman", "shifter", "charliecloud", "conda", "mamba",
    "wave", "arm", "arm64", "emulate_amd64", "gitpod", "gpu", "debug",
})


def may_set_params(profile: str) -> bool:
    """Whether a profile in this composition can set pipeline parameters (anything but an engine)."""
    return any(p.strip() not in ENGINE_PROFILES for p in profile.split(",") if p.strip())


def compose_profile(profile: str, *, demo: bool = False,
                    modifiers: tuple[str, ...] = ()) -> str:
    parts = [p.strip() for p in profile.split(",") if p.strip()]
    if demo:
        parts = ["test"] + [p for p in parts if p != "test"]
    for mod in modifiers:
        parts = [p for p in parts if p != mod] + [mod]
    return ",".join(dict.fromkeys(parts))


def build(*, upstream: Path, profile: str, params_file: Path,
          resume: bool = False, work_dir: Path | None = None,
          extra_configs: tuple[Path, ...] = ()) -> tuple[list[str], str]:
    cmd = ["nextflow", "run", upstream.as_posix(),
           "-profile", profile,
           "-params-file", params_file.as_posix()]
    if work_dir is not None:
        cmd += ["-work-dir", work_dir.as_posix()]
    for cfg in extra_configs:
        cmd += ["-c", cfg.as_posix()]
    if resume:
        cmd.append("-resume")
    return cmd, " ".join(shlex.quote(p) for p in cmd)
