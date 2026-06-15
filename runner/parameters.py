from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runner.errors import ErrorCode, NfclawError
from runner.schema import ParamSchema


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
            if param.enum and str(value) not in param.enum:
                errors.append(f"parameter '{flag}={value}' is not allowed; "
                              f"must be one of: {', '.join(param.enum)}")
    return errors


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


def compose(*, cli_overrides: dict[str, Any], params_file: Path | None,
            schema: ParamSchema, outdir: Path, input_path: Path | None,
            dest: Path) -> Path:
    merged: dict[str, Any] = {}
    if params_file and params_file.exists():
        merged.update(_load_params_file(params_file))
    if input_path is not None:
        merged["input"] = str(input_path)
    merged["outdir"] = str(outdir)
    merged.update(cli_overrides)
    refs = schema.reference_path_params()
    for key, val in list(merged.items()):
        if key in refs and isinstance(val, str) and "://" not in val:
            merged[key] = Path(val).expanduser().as_posix()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return dest
