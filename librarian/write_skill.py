# librarian/write_skill.py
from __future__ import annotations

import argparse
from pathlib import Path

from runner import schema as schema_mod
from runner import submodule as submod
from runner.schema import InputSchema, Param, ParamSchema
from runner.submodule import SubmoduleStatus


def _cell(text: object) -> str:
    """Collapse all whitespace (incl. newlines/tabs) and escape pipes so free text is safe inside a markdown table cell."""
    return " ".join(str(text).split()).replace("|", "\\|")


def _load_keywords(name: str, pipelines_dir: Path) -> list[str]:
    rp = pipelines_dir / name / "routing.yml"
    if rp.exists():
        kws = [line.strip()[2:].strip()
               for line in rp.read_text(encoding="utf-8").splitlines()
               if line.strip().startswith("- ")]
        if kws:
            return kws
    return [name, "nf-core", "nextflow"]


def _example_value(col_name: str, is_path: bool) -> str:
    if is_path:
        return f"data/sample1_{col_name}.gz"
    if col_name == "sample":
        return "sample1"
    return "value"


def _inputs_section(insch: InputSchema | None) -> str:
    if insch is None:
        return "This pipeline does not use a samplesheet; configure inputs via parameters.\n"
    head = "| column | type | required |\n|---|---|---|\n"
    rows = "".join(f"| `{c.name}` | {c.type} | {'yes' if c.required else 'no'} |\n"
                   for c in insch.columns)
    cols = [c.name for c in insch.columns]
    example = ",".join(cols) + "\n" + ",".join(
        _example_value(c.name, c.is_path) for c in insch.columns)
    return f"{head}{rows}\nExample `samplesheet.csv`:\n```csv\n{example}\n```\n"


def _key_params(ps: ParamSchema) -> str:
    # Candidates = params a user most likely must set: required, or with no sensible default.
    # Preserve nf-core schema order (input/output + main options are defined before
    # reference/advanced groups), required first — so the genuinely important flags surface
    # instead of the alphabetically-earliest ones (e.g. sarek's --tools, not --ascat-alleles).
    candidates: list[Param] = [
        p for p in ps.params.values() if p.required or p.default in (None, "")
    ]
    ordered = [p for p in candidates if p.required] + [p for p in candidates if not p.required]
    if not ordered:
        return "_No required parameters; see reference.md._\n"
    out = "| parameter | type | description |\n|---|---|---|\n"
    for p in ordered[:20]:
        out += f"| `--{p.name.replace('_', '-')}` | {p.type} | {_cell(p.description)} |\n"
    return out


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
        "# raw equivalent:\n"
        f"nextflow run pipelines/{name}/upstream -r {st.version} "
        "-profile docker --input samplesheet.csv --outdir results\n```\n\n"
        f"## Inputs\n{_inputs_section(insch)}\n"
        f"## Key parameters\n{_key_params(ps)}\n"
        "## Outputs\nResults land in `--outdir`; standardized run metadata in "
        "`<outdir>/pipeline_info/` (execution report, software versions).\n\n"
        "## Demo\n```bash\n"
        f"nfclaw run {name} --demo --outdir results   # uses upstream -profile test\n```\n\n"
        "## Full reference\n"
        f"Every parameter: [reference.md](reference.md) · upstream usage: "
        f"https://github.com/nf-core/{name}/blob/{st.version}/docs/usage.md\n\n"
        f"<!-- Generated from nf-core/{name}@{st.commit}. Do not edit by hand. -->\n"
    )
    return fm + body


def _render_reference(name: str, st: SubmoduleStatus, ps: ParamSchema,
                      insch: InputSchema | None) -> str:
    out = (f"---\nname: {name}\nversion: {st.version}\ncommit: {st.commit}\n---\n\n"
           f"# {name} — full parameter reference\n\n")
    for group, params in sorted(ps.groups().items()):
        out += f"## {group or 'general'}\n\n"
        out += "| parameter | type | default | description |\n|---|---|---|---|\n"
        for p in sorted(params, key=lambda x: x.name):
            default = "" if p.default is None else str(p.default)
            enum = f" (one of: {', '.join(p.enum)})" if p.enum else ""
            out += (f"| `--{p.name.replace('_', '-')}` | {p.type} | {_cell(default)} | "
                    f"{_cell(f'{p.description}{enum}')} |\n")
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
