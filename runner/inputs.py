"""What a pipeline's `--input` value is: a samplesheet, another local path, or a plain value.

nf-core pipelines do not all take a samplesheet. Releases in this library also take a directory or
tarball (rangeland), an SDRF file or a PRIDE accession (mhcquant), and `--input false` to run without
one (sarek). The pipeline's own `nextflow_schema.json` says which, so nfclaw reads it from
there instead of assuming: a value is only resolved to a local path, and only pre-checked as a
samplesheet, when the schema (or the file system) says that is what it is.

nf-schema validates `--input` against a samplesheet schema named by the parameter's `schema` key,
possibly inside an `if`/`then` branch. Older releases name no schema on the parameter yet ship the
conventional `assets/schema_input.json` and read it themselves; that convention is honoured only
when the parameter is declared a file (rangeland ships the template file but takes a directory).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runner.schema import PATH_FORMATS, iter_param_groups

DEFAULT_SAMPLESHEET_SCHEMA = "assets/schema_input.json"
# Keywords that describe a value without constraining it; anything else in an `if` is not decided.
_ANNOTATIONS = ("description", "errorMessage", "title", "$comment", "help_text", "fa_icon")


@dataclass(frozen=True)
class ResolvedInput:
    value: Any                           # the params-file value; False = leave `input` unset
    local_path: Path | None              # the local file/directory the value names, if any
    samplesheet_schema: str | None       # schema file (relative to the pipeline) to pre-check it with
    must_exist: bool = False             # the schema declares `exists: true` for this value


def input_param(repo: Path) -> dict | None:
    """The `input` parameter's raw schema object, or None when the pipeline declares no `--input`."""
    data = json.loads((repo / "nextflow_schema.json").read_text(encoding="utf-8"))
    for _, group in iter_param_groups(data):
        props = group.get("properties")
        if isinstance(props, dict) and isinstance(props.get("input"), dict):
            return props["input"]
    return None


def _schema_ref(obj: dict) -> str | None:
    ref = obj.get("schema")
    return ref.lstrip("/") if isinstance(ref, str) and ref.strip("/") else None


def _branches(param: dict) -> list[dict]:
    out = [param.get(k) for k in ("then", "else")]
    for key in ("anyOf", "oneOf", "allOf"):
        if isinstance(param.get(key), list):
            out += param[key]
    return [b for b in out if isinstance(b, dict)]


def _legacy_samplesheet(repo: Path, param: dict) -> str | None:
    """The conventional samplesheet schema, for a release that names none on the parameter."""
    if any(_schema_ref(b) for b in [param, *_branches(param)]):
        return None                                      # the release says which schema applies
    if param.get("format") != "file-path":
        return None                                      # e.g. a directory or tarball, never a sheet
    return DEFAULT_SAMPLESHEET_SCHEMA if (repo / DEFAULT_SAMPLESHEET_SCHEMA).is_file() else None


def samplesheet_schema(repo: Path) -> str | None:
    """The samplesheet schema `--input` is documented against, in any of its input modes.

    None when `--input` is not a samplesheet at all (or there is no `--input`), so the generated docs
    never present a template `schema_input.json` the release does not use."""
    param = input_param(repo)
    if param is None:
        return None
    for part in (param, *_branches(param)):
        ref = _schema_ref(part)
        if ref:
            return ref if (repo / ref).is_file() else None
    return _legacy_samplesheet(repo, param)


def _satisfies(sub: object, value: str) -> bool | None:
    """Whether `value` satisfies an `if` subschema — True/False, or None when it cannot be decided.

    Deliberately tiny: `pattern`, `not`, `allOf`/`anyOf` and a string `type`. Anything else is left
    to nf-schema at runtime rather than guessed."""
    if not isinstance(sub, dict):
        return None
    result = True
    for key, rule in sub.items():
        if key in _ANNOTATIONS:
            continue
        if key == "pattern" and isinstance(rule, str):
            try:
                ok: bool | None = re.search(rule, value) is not None
            except re.error:
                return None
        elif key == "not":
            inner = _satisfies(rule, value)
            ok = None if inner is None else not inner
        elif key in ("allOf", "anyOf") and isinstance(rule, list):
            parts = [_satisfies(r, value) for r in rule]
            if None in parts:
                return None
            ok = all(parts) if key == "allOf" else any(parts)
        elif key == "type":
            ok = rule == "string" or (isinstance(rule, list) and "string" in rule)
        else:
            return None
        if ok is None:
            return None
        result = result and ok
    return result


def _applicable(param: dict, value: str) -> list[dict] | None:
    """The parts of the `input` schema that apply to a string `value`, or None if undecidable."""
    parts = [param]
    if "if" in param:
        cond = _satisfies(param["if"], value)
        if cond is None:
            return None
        branch = param.get("then" if cond else "else")
        if isinstance(branch, dict):
            parts.append(branch)
    for key in ("anyOf", "oneOf"):
        for branch in param.get(key) or []:
            if isinstance(branch, dict) and branch.get("type", "string") in ("string", ["string"]):
                parts.append(branch)
    for branch in param.get("allOf") or []:
        if isinstance(branch, dict):
            parts.append(branch)
    return parts


def resolve(raw: Any, repo: Path) -> ResolvedInput | None:
    """Interpret an `--input` value the way the pipeline's schema declares it.

    The value is the `--input` flag or, without one, the params-file `input` — the same value means
    the same thing from either source. A params file can also hold a non-string:
    - a YAML/JSON boolean `false` is `--input false`;
    - any other non-string value is forwarded unchanged, for parameter validation to report;
    and a string is interpreted as follows:
    - an empty value is forwarded unchanged, so a required `--input` is reported missing;
    - a URL is forwarded unchanged (Nextflow stages it, nf-schema validates it);
    - `false` means "no input" — sarek's documented way to run without a samplesheet. It is returned
      as the value `False`, which `parameters.merge` turns into an unset `input`: a boolean false is
      rejected by nf-schema 2.7 for a string `input`, an unset one passes every version;
    - a local path is made absolute against the caller's directory (Nextflow runs from `--outdir`),
      when the schema declares a path or the value names an existing file or directory;
    - anything else (e.g. a PRIDE accession) is forwarded unchanged.
    The samplesheet pre-check applies only where the schema says the value is a samplesheet."""
    if raw is None:
        return None
    if raw is False:
        return ResolvedInput(False, None, None)
    if not isinstance(raw, (str, Path)):
        return ResolvedInput(raw, None, None)
    text = str(raw)
    if not text.strip():
        return ResolvedInput(text, None, None)           # "not set": never the caller's directory
    if "://" in text:
        return ResolvedInput(text, None, None)
    if text.strip().lower() == "false":
        return ResolvedInput(False, None, None)
    param = input_param(repo) or {}
    parts = _applicable(param, text) if param else []
    sheet = None
    if parts is not None:
        sheet = next((ref for ref in map(_schema_ref, parts) if ref), None)
        if sheet is None and param:
            sheet = _legacy_samplesheet(repo, param)
    declared = parts or []
    path_like = sheet is not None or any(p.get("format") in PATH_FORMATS for p in declared)
    if not (isinstance(raw, Path) or path_like or Path(text).expanduser().exists()):
        return ResolvedInput(text, None, None)
    local = Path(text).expanduser().resolve()
    return ResolvedInput(str(local), local, sheet,
                         must_exist=any(p.get("exists") is True for p in declared))
