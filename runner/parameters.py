from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from runner.errors import ErrorCode, NfclawError
from runner.schema import Param, ParamSchema, json_scalar

# The nf-core template parameter that suffixes the execution report/timeline/trace/DAG filenames.
_REPORT_SUFFIX = "trace_report_suffix"


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
            if not (param.enum and json_scalar(value) in param.enum):
                errors.extend(_value_shape_errors(flag, value, param))
    return errors


def missing_required_params(merged: dict[str, Any], schema: ParamSchema) -> list[str]:
    """Schema-required params without defaults must be supplied before launching Nextflow.

    Required params that carry a schema default are intentionally not flagged: nf-schema applies the
    default, and generated docs surface it so agents do not need to invent a value.
    """
    errors: list[str] = []
    for name, param in schema.params.items():
        if not param.required or param.default is not None:
            continue
        value = merged.get(name)
        if value is None or value == "":
            errors.append(f"missing required parameter '--{name.replace('_', '-')}'")
    return errors


def _value_shape_errors(flag: str, value: Any, param: Param) -> list[str]:
    errors: list[str] = []
    scalar_type = param.type
    if scalar_type == "string" and not isinstance(value, str):
        errors.append(f"parameter '{flag}' expects a string, got {type(value).__name__}")
        return errors
    if scalar_type == "boolean" and not isinstance(value, bool):
        errors.append(f"parameter '{flag}' expects a boolean, got {type(value).__name__}")
        return errors
    if scalar_type == "integer" and (not isinstance(value, int) or isinstance(value, bool)):
        errors.append(f"parameter '{flag}' expects an integer, got {type(value).__name__}")
        return errors
    if scalar_type == "number" and (
        not isinstance(value, (int, float)) or isinstance(value, bool)
    ):
        errors.append(f"parameter '{flag}' expects a number, got {type(value).__name__}")
        return errors
    if param.pattern and isinstance(value, str):
        try:
            matches = re.search(param.pattern, value) is not None
        except re.error:
            matches = True
        if not matches:
            errors.append(f"parameter '{flag}' value {value!r} must match {param.pattern}")
    if param.min_length is not None and isinstance(value, str) and len(value) < param.min_length:
        errors.append(f"parameter '{flag}' length >= {param.min_length} required")
    if param.max_length is not None and isinstance(value, str) and len(value) > param.max_length:
        errors.append(f"parameter '{flag}' length <= {param.max_length} required")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if param.minimum is not None and value < param.minimum:
            errors.append(f"parameter '{flag}' must be >= {param.minimum}")
        if param.maximum is not None and value > param.maximum:
            errors.append(f"parameter '{flag}' must be <= {param.maximum}")
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


def pin_report_suffix(merged: dict[str, Any], schema: ParamSchema,
                      *, now: datetime | None = None) -> dict[str, Any]:
    """Pin `trace_report_suffix` so the run's report filenames are fixed, not "whenever this ran".

    The nf-core template defaults this parameter to `new java.util.Date().format('yyyy-MM-dd_HH-mm-ss')`
    — a *fresh timestamp evaluated on every launch* — and interpolates it into the names of the
    execution report, timeline, trace and DAG under `pipeline_info/`. Left alone, replaying a run
    through `provenance/commands.sh` writes a second set of reports under new names instead of
    reproducing the original run's outputs, so the bundle is not a strict reproduction and
    `outputs.sha256` can never be checked against it.

    Recording the value the run actually used turns that timestamp from an implicit, unrepeatable
    default into a recorded input: it lands in `provenance/params.json`, which `commands.sh` passes
    back with `-params-file`, so a replay names its reports exactly as the original did.

    Only applied when the pinned release declares the parameter (older releases predate it) and
    never overrides a value the caller supplied. The format matches the pipeline's own, so the
    filenames look exactly as they would from a plain `nextflow run`.
    """
    if _REPORT_SUFFIX not in schema.params or merged.get(_REPORT_SUFFIX):
        return merged
    stamp = (now or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S")
    return {**merged, _REPORT_SUFFIX: stamp}


def _load_params_file(path: Path) -> dict:
    # utf-8-sig so a leading UTF-8 BOM (e.g. from a Windows editor) is stripped: json.loads rejects
    # a BOM outright, so without this a BOM'd params file fails with a cryptic parse error. No-op
    # without a BOM. A binary file (e.g. an .xlsx by mistake) raises UnicodeDecodeError — report it
    # as a clear error rather than a raw traceback.
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise NfclawError(
            ErrorCode.PARAMS_INVALID,
            f"--params-file is not valid UTF-8 text: {path}",
            fix="Pass a plain-text JSON or YAML file, not a binary one.") from exc
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise NfclawError(
                ErrorCode.PARAMS_INVALID,
                f"--params-file is not valid JSON: {path} ({exc})",
                fix="Fix the JSON syntax, or use a .yaml params file.") from exc
    else:
        try:
            import yaml  # optional dependency
        except ModuleNotFoundError as exc:
            raise NfclawError(
                ErrorCode.ENVIRONMENT,
                f"Reading YAML params file '{path}' requires pyyaml.",
                fix="Use a .json params file, or `pip install pyyaml`.",
            ) from exc
        try:
            data = yaml.safe_load(text) or {}
        except yaml.YAMLError as exc:
            raise NfclawError(
                ErrorCode.PARAMS_INVALID,
                f"--params-file is not valid YAML: {path} ({exc})",
                fix="Fix the YAML syntax, or use a .json params file.") from exc
    # A params file is a map of parameter -> value (what Nextflow's -params-file expects). A
    # top-level list or scalar is malformed; catch it here with a clear error instead of letting
    # the later `dict.update()` blow up with a cryptic TypeError.
    if not isinstance(data, dict):
        raise NfclawError(
            ErrorCode.PARAMS_INVALID,
            f"--params-file must contain an object of parameters, got {type(data).__name__}: {path}",
            fix='Use a top-level object like {"param": value}, not a list or a bare scalar.')
    return data


def merge(*, cli_overrides: dict[str, Any], params_file: Path | None,
          input_path: "Path | str | None", outdir: Path) -> dict[str, Any]:
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
