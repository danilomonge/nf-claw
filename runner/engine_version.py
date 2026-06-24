from __future__ import annotations

import re
import subprocess
from pathlib import Path

# nf-core pins the engine in the manifest, e.g. `nextflowVersion = '!>=25.04.3'`.
# We surface a NON-blocking advisory when the installed engine is clearly too old;
# Nextflow itself is the authority and enforces this at launch. To avoid ever
# contradicting it with a false positive, we judge only the unambiguous `>=`/`>`
# constraint and stay silent on anything we cannot parse with confidence.

_REQUIRED_RE = re.compile(r"""nextflowVersion\s*=\s*['"]([^'"]+)['"]""")
_SPEC_RE = re.compile(r"^\s*!?\s*(>=?)\s*(\d+(?:\.\d+)*)\s*$")
_INSTALLED_RE = re.compile(r"version\s+(\d+(?:\.\d+)+)")


def required_spec(config_path: Path) -> str | None:
    """The `manifest.nextflowVersion` constraint declared in nextflow.config, or None."""
    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError:
        return None
    m = _REQUIRED_RE.search(text)
    return m.group(1) if m else None


def _installed_raw() -> str | None:
    try:
        r = subprocess.run(["nextflow", "-version"], capture_output=True,
                           text=True, timeout=30)
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None
    return (r.stdout or r.stderr) or None


def _tuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def warning(spec: str | None, installed: str | None) -> str | None:
    """An advisory string if `installed` clearly fails `spec`, else None (silent)."""
    if not spec or not installed:
        return None
    sm = _SPEC_RE.match(spec)
    im = _INSTALLED_RE.search(installed)
    if sm is None or im is None:               # not a constraint/version we model → stay silent
        return None
    op, req, have = sm.group(1), sm.group(2), im.group(1)
    req_t, have_t = _tuple(req), _tuple(have)
    n = max(len(req_t), len(have_t))
    req_t += (0,) * (n - len(req_t))
    have_t += (0,) * (n - len(have_t))
    satisfied = have_t >= req_t if op == ">=" else have_t > req_t
    if satisfied:
        return None
    return (f"Nextflow {have} is older than this pipeline's required {op}{req}; "
            f"Nextflow will likely reject the run "
            f"(advisory — Nextflow enforces the engine version).")


def check(upstream: Path, *, nxf_ver: str | None = None) -> list[str]:
    """Zero or one advisory about the Nextflow engine vs. the pipeline's requirement.

    When `nxf_ver` is given (the user pinned the engine via --nxf-ver / NXF_VER), that is the
    version Nextflow will actually run, so judge the requirement against it — not the installed
    launcher, which Nextflow only uses to bootstrap the requested version."""
    spec = required_spec(upstream / "nextflow.config")
    if spec is None:                           # no declared constraint → nothing to advise
        return []
    effective = f"version {nxf_ver}" if nxf_ver else _installed_raw()
    w = warning(spec, effective)
    return [w] if w else []
