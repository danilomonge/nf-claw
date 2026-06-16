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
    hidden: bool = False     # nf-core marks generic/boilerplate params (email, validation*, …) hidden


@dataclass(frozen=True)
class ParamSchema:
    title: str
    description: str
    params: dict[str, Param]

    def known_params(self) -> set[str]:
        return set(self.params)

    def required_params(self) -> set[str]:
        return {n for n, p in self.params.items() if p.required}

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

    @property
    def is_path(self) -> bool:
        """Any filesystem path (file or directory) — these values get an existence check."""
        return self.fmt in ("file-path", "directory-path")


@dataclass(frozen=True)
class InputSchema:
    columns: tuple[Column, ...]


def _type_of(obj: dict) -> str:
    """Render a JSON-schema type, unioning anyOf/oneOf variants (e.g. 'integer or string')."""
    t = obj.get("type")
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
                enum=tuple(str(e) for e in enum) if isinstance(enum, list) else None,
                description=str(pobj.get("description", "")),
                fmt=pobj.get("format"),
                required=pname in required,
                group=gname,
                hidden=bool(pobj.get("hidden", False)),
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
                enum=tuple(str(e) for e in enum) if isinstance(enum, list) else None,
            ))
    return InputSchema(columns=tuple(cols))
