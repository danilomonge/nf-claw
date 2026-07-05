from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


@dataclass(frozen=True)
class Param:
    name: str
    type: str
    default: Any
    enum: tuple[str, ...] | None
    description: str
    fmt: str | None          # "file-path" | "directory-path" | None
    required: bool
    group: str
    hidden: bool = False      # nf-core marks generic/boilerplate params (email, validation*, …) hidden
    # Value-shape constraints nf-schema enforces at runtime (enum has its own field above).
    pattern: str | None = None
    minimum: int | float | None = None
    maximum: int | float | None = None
    min_length: int | None = None
    max_length: int | None = None
    deprecated: bool = False


@dataclass(frozen=True)
class ParamSchema:
    title: str
    description: str
    params: dict[str, Param]

    def known_params(self) -> set[str]:
        return set(self.params)

    def reference_path_params(self) -> set[str]:
        return {n for n, p in self.params.items()
                if p.fmt in ("file-path", "directory-path")}

    def groups(self) -> dict[str, list[Param]]:
        out: dict[str, list[Param]] = {}
        for p in self.params.values():
            out.setdefault(p.group, []).append(p)
        return out


@dataclass(frozen=True)
class Column:
    name: str
    type: str
    required: bool
    pattern: str | None
    fmt: str | None = None          # "file-path" | "directory-path" | None — mirrors Param.fmt
    enum: tuple[str, ...] | None = None
    # Same value-shape constraints as Param, so one renderer serves both (no asymmetry).
    minimum: int | float | None = None
    maximum: int | float | None = None
    min_length: int | None = None
    max_length: int | None = None
    deprecated: bool = False

    @property
    def is_path(self) -> bool:
        """Any filesystem path (file or directory) — these values get an existence check."""
        return self.fmt in ("file-path", "directory-path")


@dataclass(frozen=True)
class InputSchema:
    columns: tuple[Column, ...]
    # Mutually-exclusive required column groups from the samplesheet's `items.oneOf`: each inner
    # tuple is one allowed set of columns, and a row must satisfy EXACTLY ONE group (e.g.
    # (("bam",), ("cram",)) for createpanelrefs, or (("sampleID","forwardReads"),
    # ("sample","fastq_1")) for ampliseq's legacy-vs-standardized formats). Empty when the schema
    # declares no such choice. nf-schema enforces the full rule (including any `not`/`anyOf`
    # exclusions) at runtime; this captures the choice so the generated docs can surface it.
    one_of: tuple[tuple[str, ...], ...] = ()
    # Conditional row rules from `items.dependentRequired`, plus `items.anyOf` branches that are
    # themselves dependentRequired maps. These are deterministic column-presence constraints, so
    # the runner can fail malformed tabular inputs before launching Nextflow.
    dependent_required: tuple[tuple[str, tuple[str, ...]], ...] = ()
    any_of_dependent_required: tuple[tuple[tuple[str, tuple[str, ...]], ...], ...] = ()


def json_scalar(value: Any) -> str:
    """A JSON scalar in its JSON literal form — `true`/`false`, not Python's `True`/`False`.
    Used wherever a schema value becomes text (enum capture, default rendering, the runner's
    enum check) so generated docs and validation match the schema byte-for-byte."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _type_of(obj: dict) -> str:
    """Render a JSON-schema type, unioning list/anyOf/oneOf variants (e.g. 'integer or string')."""
    t = obj.get("type")
    if isinstance(t, list):                       # JSON Schema allows a type array, e.g. ["boolean","string"]
        types = [str(x) for x in t if x]
        if types:
            return " or ".join(dict.fromkeys(types))
    if t:
        return str(t)
    for key in ("anyOf", "oneOf"):
        variants = obj.get(key)
        if isinstance(variants, list):
            types = [str(v["type"]) for v in variants
                     if isinstance(v, dict) and v.get("type")]
            if types:
                return " or ".join(dict.fromkeys(types))
    return "string"


def _iter_groups(data: dict) -> Iterator[tuple[str, dict]]:
    """Yield (group_name, group_object) for every parameter group.

    nf-core schemas place groups under "definitions" (older) or "$defs" (newer),
    and may also carry ungrouped top-level "properties". All are tolerated.
    """
    for key in ("definitions", "$defs"):
        defs = data.get(key)
        if isinstance(defs, dict):
            for gname, gobj in defs.items():
                if isinstance(gobj, dict):
                    yield str(gname), gobj
    if isinstance(data.get("properties"), dict):
        yield "", {"properties": data["properties"], "required": data.get("required", [])}


def load_param_schema(repo: Path) -> ParamSchema:
    data = json.loads((repo / "nextflow_schema.json").read_text(encoding="utf-8"))
    params: dict[str, Param] = {}
    for gname, gobj in _iter_groups(data):
        props = gobj.get("properties")
        if not isinstance(props, dict):
            continue
        required = set(gobj.get("required") or [])
        for pname, pobj in props.items():
            if not isinstance(pobj, dict):
                continue
            enum = pobj.get("enum")
            params[pname] = Param(
                name=pname,
                type=_type_of(pobj),
                default=pobj.get("default"),
                enum=tuple(json_scalar(e) for e in enum) if isinstance(enum, list) else None,
                description=str(pobj.get("description", "")),
                fmt=pobj.get("format"),
                required=pname in required,
                group=gname,
                hidden=bool(pobj.get("hidden", False)),
                pattern=pobj.get("pattern"),
                minimum=pobj.get("minimum"),
                maximum=pobj.get("maximum"),
                min_length=pobj.get("minLength"),
                max_length=pobj.get("maxLength"),
                deprecated=bool(pobj.get("deprecated", False)),
            )
    return ParamSchema(
        title=str(data.get("title") or repo.name),
        description=str(data.get("description") or ""),
        params=params,
    )


def load_input_schema(repo: Path) -> InputSchema | None:
    path = repo / "assets" / "schema_input.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items", {})
    props = items.get("properties", {})
    required = set(items.get("required") or [])
    # Mutually-exclusive required column groups: each `items.oneOf` branch that lists `required`
    # columns is one allowed group (a row must satisfy exactly one). Branches without a `required`
    # list carry no column choice and are skipped.
    one_of: list[tuple[str, ...]] = []
    for branch in items.get("oneOf") or []:
        if isinstance(branch, dict):
            req = branch.get("required")
            if isinstance(req, list) and req:
                one_of.append(tuple(str(r) for r in req))
    dependent_required = _dependent_required(items.get("dependentRequired"))
    any_of_dependent_required: list[tuple[tuple[str, tuple[str, ...]], ...]] = []
    for branch in items.get("anyOf") or []:
        if isinstance(branch, dict):
            deps = _dependent_required(branch.get("dependentRequired"))
            if deps:
                any_of_dependent_required.append(deps)
    cols: list[Column] = []
    if isinstance(props, dict):
        for cname, cobj in props.items():
            if not isinstance(cobj, dict):
                continue
            enum = cobj.get("enum")
            cols.append(Column(
                name=str(cname),
                type=_type_of(cobj),
                required=cname in required,
                pattern=cobj.get("pattern"),
                fmt=cobj.get("format"),
                enum=tuple(json_scalar(e) for e in enum) if isinstance(enum, list) else None,
                minimum=cobj.get("minimum"),
                maximum=cobj.get("maximum"),
                min_length=cobj.get("minLength"),
                max_length=cobj.get("maxLength"),
                deprecated=bool(cobj.get("deprecated", False)),
            ))
    return InputSchema(
        columns=tuple(cols),
        one_of=tuple(one_of),
        dependent_required=dependent_required,
        any_of_dependent_required=tuple(any_of_dependent_required),
    )


def _dependent_required(obj: Any) -> tuple[tuple[str, tuple[str, ...]], ...]:
    if not isinstance(obj, dict):
        return ()
    out: list[tuple[str, tuple[str, ...]]] = []
    for key, values in obj.items():
        if isinstance(values, list):
            reqs = tuple(str(v) for v in values if v)
            if reqs:
                out.append((str(key), reqs))
    return tuple(out)
