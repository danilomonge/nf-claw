# librarian/write_skill.py
from __future__ import annotations

import argparse
from pathlib import Path

from runner import schema as schema_mod
from runner import submodule as submod
from runner.schema import InputSchema, ParamSchema
from runner.submodule import SubmoduleStatus


def _cell(text: object) -> str:
    """Collapse all whitespace (incl. newlines/tabs) and escape pipes so free text is safe inside a markdown table cell."""
    return " ".join(str(text).split()).replace("|", "\\|")


def _type_with_fmt(type_: str, fmt: str | None) -> str:
    """Annotate a type with its path-ness — a schema fact (format: file-path / directory-path)."""
    if fmt in ("file-path", "directory-path"):
        return f"{type_} ({fmt.replace('-', ' ')})"
    return type_


def _constraints(obj) -> str:
    """Render the value-shape constraints nf-schema enforces — a literal fact list, no heuristics.
    `enum` is intentionally excluded (it has its own 'allowed values' column). Works for both
    Param and Column since they share these attributes."""
    parts: list[str] = []
    if obj.pattern:
        parts.append(f"matches {obj.pattern}")
    if obj.minimum is not None:
        parts.append(f"≥ {obj.minimum}")
    if obj.maximum is not None:
        parts.append(f"≤ {obj.maximum}")
    if obj.min_length is not None:
        parts.append(f"length ≥ {obj.min_length}")
    if obj.max_length is not None:
        parts.append(f"length ≤ {obj.max_length}")
    if obj.deprecated:
        parts.append("deprecated")
    return _cell("; ".join(parts))


def _load_keywords(name: str, pipelines_dir: Path) -> list[str]:
    rp = pipelines_dir / name / "routing.yml"
    if rp.exists():
        kws = [line.strip()[2:].strip()
               for line in rp.read_text(encoding="utf-8").splitlines()
               if line.strip().startswith("- ")]
        if kws:
            return kws
    return [name, "nf-core", "nextflow"]


def _inputs_section(insch: InputSchema | None) -> str:
    if insch is None:
        return "This pipeline does not use a samplesheet; configure inputs via parameters.\n"
    named = [c for c in insch.columns if c.name]
    if not named:
        # A single unnamed column (e.g. nf-core/fetchngs id list): one value per line, no header.
        c = insch.columns[0] if insch.columns else None
        constraint = f" Each value must match the pattern `{c.pattern}`." if c and c.pattern else ""
        return "Input is a plain text file with one value per line (no header)." + constraint + "\n"
    head = "| column | type | required | allowed values | constraints |\n|---|---|---|---|---|\n"
    rows = ""
    for c in named:
        typ = _type_with_fmt(c.type, c.fmt)
        allowed = ", ".join(c.enum) if c.enum else ""
        rows += (f"| `{c.name}` | {typ} | {'yes' if c.required else 'no'} | "
                 f"{_cell(allowed)} | {_constraints(c)} |\n")
    header_line = ",".join(c.name for c in named)
    return (f"{head}{rows}\n"
            "The samplesheet is a CSV with this exact header; fill each value per the table above "
            f"and `reference.md` (no example value is invented here):\n```csv\n{header_line}\n```\n")


def _required_params(ps: ParamSchema) -> str:
    """Only the parameters the schema itself marks required — a fact, not a heuristic guess."""
    required = [p for p in ps.params.values() if p.required]
    if not required:
        return ("_The schema marks no parameter required; the pipeline runs with defaults. "
                "See reference.md to customise._\n")
    out = "| parameter | type | allowed values | description |\n|---|---|---|---|\n"
    for p in required:
        allowed = ", ".join(p.enum) if p.enum else ""
        out += (f"| `--{p.name.replace('_', '-')}` | {_type_with_fmt(p.type, p.fmt)} | "
                f"{_cell(allowed)} | {_cell(p.description)} |\n")
    return out


def _param_groups(ps: ParamSchema) -> str:
    """The schema's own parameter groups (names + counts) — a deterministic map, no curation."""
    groups = sorted(ps.groups().items())
    if not groups:
        return "_No additional parameters._\n"
    lines = [f"- `{g or 'general'}` ({len(params)} parameters)" for g, params in groups]
    return ("All other parameters are optional. Every one — with type, default and allowed "
            "values — is in [reference.md](reference.md), grouped as:\n" + "\n".join(lines) + "\n")


def _render_skill(name: str, st: SubmoduleStatus, ps: ParamSchema,
                  insch: InputSchema | None, keywords: list[str]) -> str:
    desc = (ps.description.splitlines() or [name])[0]
    fm = (
        "---\n"
        f"name: {name}\n"
        f"pipeline: nf-core/{name}\n"
        f"version: {st.version}\n"
        f"commit: {st.commit}\n"
        f"description: {desc}\n"
        f"keywords: [{', '.join(keywords)}]\n"
        f"has_samplesheet: {str(insch is not None).lower()}\n"
        "---\n"
    )
    body = (
        f"# {name}\n\n{desc}\n\n"
        "## Run it\n```bash\n"
        f"git submodule update --init pipelines/{name}/upstream   # first time only\n"
        f"nfclaw run {name} --input samplesheet.csv --outdir results -profile docker\n"
        "# raw equivalent (the submodule is already pinned to this release, so no -r is needed):\n"
        f"nextflow run pipelines/{name}/upstream "
        "-profile docker --input samplesheet.csv --outdir results\n```\n\n"
        f"## Inputs\n{_inputs_section(insch)}\n"
        f"## Required parameters\n{_required_params(ps)}\n"
        f"## Other parameters\n{_param_groups(ps)}\n"
        "## Outputs\nResults land in `--outdir`; standardized run metadata in "
        "`<outdir>/pipeline_info/` (execution report, software versions).\n\n"
        "## Demo\n```bash\n"
        f"nfclaw run {name} --demo --outdir results   # uses upstream -profile test\n```\n\n"
        "## Full reference\n"
        "Every parameter — name, type, required, allowed values, default — is in "
        "[reference.md](reference.md). Use it as the source of truth; do not guess flags. "
        "Nextflow's nf-schema validates every parameter against this schema at runtime, so an "
        "unknown or invalid value fails fast. Upstream usage: "
        f"https://github.com/nf-core/{name}/blob/{st.version}/docs/usage.md\n\n"
        f"<!-- Generated from nf-core/{name}@{st.commit}. Do not edit by hand. -->\n"
    )
    return fm + body


def _render_reference(name: str, st: SubmoduleStatus, ps: ParamSchema,
                      insch: InputSchema | None) -> str:
    out = (f"---\nname: {name}\nversion: {st.version}\ncommit: {st.commit}\n---\n\n"
           f"# {name} — full parameter reference\n\n"
           f"{ps.title}. Every parameter from the pinned `nextflow_schema.json`, validated by "
           "nf-schema at runtime. `hidden` marks nf-core's generic/boilerplate parameters; "
           "`constraints` lists the value bounds the schema enforces (pattern, min/max, length).\n\n")
    for group, params in sorted(ps.groups().items()):
        out += f"## {group or 'general'}\n\n"
        out += ("| parameter | type | required | hidden | allowed values | constraints | "
                "default | description |\n|---|---|---|---|---|---|---|---|\n")
        for p in sorted(params, key=lambda x: x.name):
            default = "" if p.default is None else str(p.default)
            allowed = ", ".join(p.enum) if p.enum else ""
            req = "yes" if p.required else ""
            hid = "yes" if p.hidden else ""
            out += (f"| `--{p.name.replace('_', '-')}` | {_type_with_fmt(p.type, p.fmt)} | "
                    f"{req} | {hid} | {_cell(allowed)} | {_constraints(p)} | "
                    f"{_cell(default)} | {_cell(p.description)} |\n")
        out += "\n"
    out += f"<!-- Generated from nf-core/{name}@{st.commit}. Do not edit by hand. -->\n"
    return out


def generate(name: str, *, pipelines_dir: Path) -> tuple[Path, Path]:
    st = submod.resolve(name, pipelines_dir)
    ps = schema_mod.load_param_schema(st.path)
    insch = schema_mod.load_input_schema(st.path)
    keywords = _load_keywords(name, pipelines_dir)
    skill_path = pipelines_dir / name / "skill.md"
    ref_path = pipelines_dir / name / "reference.md"
    skill_path.write_text(_render_skill(name, st, ps, insch, keywords), encoding="utf-8")
    ref_path.write_text(_render_reference(name, st, ps, insch), encoding="utf-8")
    return skill_path, ref_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="librarian.write_skill")
    parser.add_argument("name", nargs="?")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--pipelines-dir", default="pipelines")
    args = parser.parse_args(argv)
    pdir = Path(args.pipelines_dir)
    names = ([d.name for d in sorted(pdir.iterdir()) if d.is_dir()]
             if args.all else [args.name])
    for n in names:
        skill, ref = generate(n, pipelines_dir=pdir)
        print(f"wrote {skill} and {ref}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
