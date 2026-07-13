from __future__ import annotations

import re
from pathlib import Path


# nf-validation 1.x set these as *params*; nf-schema 2.x replaced them with options in the
# `validation` config scope. The mapping is the official migration guide's, verbatim:
# https://nextflow-io.github.io/nf-schema/latest/migration_guide/
_REMOVED_PARAMS = {
    "validationSchemaIgnoreParams": "validation.defaultIgnoreParams",
    "validationIgnoreParams": "validation.ignoreParams",
    "validationMonochromeLogs": "validation.monochromeLogs",
    "validationLenientMode": "validation.lenientMode",
    "validationFailUnrecognisedParams": "validation.failUnrecognisedParams",
    "validationShowHiddenParams": "validation.showHiddenParams",
}
_ASSIGNMENT = re.compile(
    r"^\s*(" + "|".join(_REMOVED_PARAMS) + r")\s*=", re.MULTILINE)
# `plugins { id 'nf-schema@2.5.1' }` — the plugin (and major version) the release actually declares.
_PLUGIN = re.compile(r"id\s+['\"]nf-(schema|validation)@(\d+)")


def _declares_nf_schema_v2(config: Path) -> bool:
    """True when the release declares nf-schema 2.x (where the 1.x params below no longer exist)."""
    try:
        text = config.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    m = _PLUGIN.search(text)
    return bool(m) and m.group(1) == "schema" and int(m.group(2)) >= 2


def check(upstream: Path) -> list[str]:
    """Advisory: a pinned release that declares nf-schema 2.x but still sets an nf-validation 1.x param.

    nf-schema 2.x does not know these params, and the pipeline's own schema does not declare them
    either, so Nextflow reports the parameter as invalid — a warning the run then carries for no
    reason anyone reading the log can see. It is inert: the option does nothing and results are
    unaffected. nf-claw wraps each release **unmodified**, so this cannot be fixed here; surfacing it
    up front is what stops the warning being re-reported as an nf-claw defect every time someone
    reads a log.

    Deterministic, and narrow by construction: a release that declares nf-validation 1.x is using
    these params *correctly* and is never flagged. Only the nf-schema-2.x-plus-1.x-param combination
    — the actual defect — is reported.
    """
    main_config = upstream / "nextflow.config"
    if not _declares_nf_schema_v2(main_config):
        return []
    configs = [main_config] + sorted((upstream / "conf").glob("*.config"))
    # One advisory per offending parameter, naming every config that sets it — the same release
    # typically repeats the option across its test profiles, and repeating the whole explanation
    # once per file would bury the run's own output.
    where: dict[str, list[str]] = {}
    for config in configs:
        try:
            text = config.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for name in dict.fromkeys(_ASSIGNMENT.findall(text)):
            where.setdefault(name, []).append(config.relative_to(upstream).as_posix())
    return [
        f"the pinned release sets `{name}` in {', '.join(files)}: an nf-validation 1.x parameter "
        f"removed in nf-schema 2.x, which this release declares (the replacement is the "
        f"`{_REMOVED_PARAMS[name]}` config option). Nextflow will warn that the parameter is "
        f"invalid — it is inert and does not affect results. Upstream bug; nf-claw wraps releases "
        f"unmodified. See docs/known-issues.md."
        for name, files in where.items()
    ]
