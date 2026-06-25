from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runner.errors import ErrorCode, NfclawError
from runner.schema import ParamSchema, json_scalar


def validate_params(cli_overrides: dict[str, Any], schema: ParamSchema) -> list[str]:
    """Deterministic, schema-driven validation of agent-supplied flags (errors, not heuristics).

    Settles the two classes the schema makes unambiguous: unknown flags (not in the schema)
    and values outside an enum's allowed set. Required-ness and types are left to nf-schema
    at runtime, which handles the schema's conditionals correctly (so we never false-positive).
    """
    known = schema.known_params()
    errors: list[str] = []
    for key, value in cli_overrides.items():
        flag = f"--{key.replace('_', '-')}"
        if key not in known:
            errors.append(f"unknown parameter '{flag}' (not in the pipeline schema)")
        else:
            param = schema.params[key]
            if param.enum and json_scalar(value) not in param.enum:
                errors.append(f"parameter '{flag}={value}' is not allowed; "
                              f"must be one of: {', '.join(param.enum)}")
    return errors


_LEAVE = object()       # sentinel: "not coercible — leave the value untouched"


def _coerce_scalar(value: str, type_: str):
    """Convert a CLI string to its schema scalar type, or `_LEAVE` if it can't be done
    unambiguously (so nf-schema reports a precise error on the original string)."""
    if type_ == "boolean":
        low = value.strip().lower()
        return True if low == "true" else False if low == "false" else _LEAVE
    if type_ == "integer":
        try:
            return int(value.strip())
        except ValueError:
            return _LEAVE
    if type_ == "number":
        try:
            return float(value.strip())
        except ValueError:
            return _LEAVE
    return _LEAVE           # string, or a union like "integer or string" — ambiguous, leave it


def coerce_to_schema(merged: dict[str, Any], schema: ParamSchema) -> dict[str, Any]:
    """Coerce CLI-string values to their schema-declared scalar type so `--skip-busco true` or
    `--max-cpus 4` reach nf-schema as a real boolean/integer/number, not a string. Only the
    unambiguous scalar types are touched; strings, union types and unparseable values are left
    as-is. Values from a params-file are already typed, so this is a no-op for them."""
    out = dict(merged)
    for key, val in merged.items():
        param = schema.params.get(key)
        if param is None or not isinstance(val, str):
            continue
        coerced = _coerce_scalar(val, param.type)
        if coerced is not _LEAVE:
            out[key] = coerced
    return out


def _load_params_file(path: Path) -> dict:
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    try:
        import yaml  # optional dependency
    except ModuleNotFoundError as exc:
        raise NfclawError(
            ErrorCode.ENVIRONMENT,
            f"Reading YAML params file '{path}' requires pyyaml.",
            fix="Use a .json params file, or `pip install pyyaml`.",
        ) from exc
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def merge(*, cli_overrides: dict[str, Any], params_file: Path | None,
          input_path: Path | None, outdir: Path) -> dict[str, Any]:
    """Build the full parameter map (params-file < --input/--outdir < CLI) without touching
    disk, so the merged result can be validated before anything is written or executed."""
    merged: dict[str, Any] = {}
    if params_file and params_file.exists():
        merged.update(_load_params_file(params_file))
    if input_path is not None:
        merged["input"] = str(input_path)
    merged["outdir"] = str(outdir)
    merged.update(cli_overrides)
    return merged


def resolve_path_params(merged: dict[str, Any], schema: ParamSchema) -> dict[str, Any]:
    """Make every file/dir-path param absolute. Nextflow runs with cwd = repo root, so a
    relative path would otherwise resolve against the repo, not the caller's directory."""
    refs = schema.reference_path_params()
    out = dict(merged)
    for key, val in out.items():
        if key in refs and isinstance(val, str) and "://" not in val:
            out[key] = Path(val).expanduser().resolve().as_posix()
    return out


def write_params_file(params: dict[str, Any], dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(params, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return dest
