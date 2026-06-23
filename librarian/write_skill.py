# librarian/write_skill.py
from __future__ import annotations

import argparse
import re
from pathlib import Path

from runner import schema as schema_mod
from runner import submodule as submod
from runner.schema import InputSchema, ParamSchema, json_scalar
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


def _input_summary(insch: InputSchema | None) -> str:
    """One-line, schema-derived description of what the pipeline consumes (for the catalog).
    Robust: comes straight from assets/schema_input.json, never guessed."""
    if insch is None:
        return "parameters (no samplesheet)"
    named = [c for c in insch.columns if c.name]
    if not named:
        return "id list (one value per line)"
    return "samplesheet (" + ", ".join(c.name for c in named) + ")"


def _produces_multiqc(upstream: Path) -> bool:
    """A MultiQC report is a near-universal nf-core output; detect it from the pinned tree."""
    return ((upstream / "assets" / "multiqc_config.yml").exists()
            or (upstream / "modules" / "nf-core" / "multiqc").is_dir())


def _output_summary(upstream: Path) -> str:
    """One-line, fact-only description of outputs (for the catalog). nf-core pins no
    machine-readable output schema, so this states the guaranteed output contract — not an
    invented per-file list. Per-release detail lives in the upstream docs/output.md (linked
    from the skill)."""
    parts = ["--outdir/ (per-module results)", "pipeline_info/ (reports, versions)"]
    if _produces_multiqc(upstream):
        parts.append("MultiQC report")
    return "; ".join(parts)


_TOOL_BULLET = re.compile(r"^\s*[-*+]\s*\[([^\]]+)\]")  # markdown allows -, * or + bullets


def _is_tool_section(header: str) -> bool:
    """Whether a CITATIONS.md `## ` section lists software the pipeline runs. True for the
    `## Pipeline tools` section and any language-specific software section (`## R packages`,
    `## Python`, ...); False for citation-link headers (`## [Name](url)` — the pipeline's own
    paper and the nf-core/Nextflow citations), the packaging/containerisation infra section,
    and test-data/external-archive sections (`## Data`, `## Pipeline resources`)."""
    t = header.strip().lower()
    if t.startswith("["):                            # `## [Name](url)` — paper/framework citation
        return False
    if "packaging" in t or "containeri" in t:        # packaging/containerisation (incl. /testing) — infra
        return False
    if t == "data" or "resource" in t:               # test data / external archives — not software
        return False
    return True


def _pipeline_tools(upstream: Path) -> list[str]:
    """The software/methods the pipeline runs, taken from the authors' own CITATIONS.md — a
    curated fact, not our invention. Collects the `[Tool](url)` bullets under every software
    section (see `_is_tool_section`), de-duplicated in document order. Empty if the file is
    absent or lists no tools."""
    try:
        text = (upstream / "CITATIONS.md").read_text(encoding="utf-8")
    except OSError:
        return []
    tools: list[str] = []
    in_section = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_section = _is_tool_section(line[3:])
            continue
        if in_section and (m := _TOOL_BULLET.match(line)):
            nm = m.group(1).strip()
            if nm and nm not in tools:
                tools.append(nm)
    return tools


def _tools_section(name: str, st: SubmoduleStatus, tools: list[str]) -> str:
    if not tools:
        return ""
    return (f"The tools/methods this pipeline runs, per the authors' own list: "
            f"{', '.join(tools)}.\n\nFull list with references: "
            f"https://github.com/nf-core/{name}/blob/{st.version}/CITATIONS.md\n")


def _summary(upstream: Path) -> str:
    """The pipeline's own one-paragraph description, taken verbatim from the first prose
    paragraph of the README `## Introduction` section — a far richer selection signal than the
    terse manifest description. Leading non-prose blocks (images, headings, blockquotes, lists)
    are skipped; markdown links are flattened to their text. Returns "" if the section or a prose
    paragraph is absent, so callers fall back to the manifest description — this can only ever add
    signal, never break."""
    try:
        text = (upstream / "README.md").read_text(encoding="utf-8")
    except OSError:
        return ""
    m = re.search(r"^##\s+Introduction\s*$(.*?)(^##\s|\Z)", text, re.M | re.S)
    if not m:
        return ""
    for block in re.split(r"\n\s*\n", m.group(1).strip()):
        s = block.strip()
        if (not s or s[0] in "#>|<" or s.startswith(("![", "- ", "* ", "+ "))
                or re.match(r"^\d+\.\s", s)):
            continue                                       # image/heading/blockquote/list lead-in
        s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)         # inline images
        s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)     # inline links -> text
        s = re.sub(r"\[([^\]]+)\]\[[^\]]*\]", r"\1", s)    # reference-style links -> text
        s = s.replace("**", "").replace("`", "")
        s = re.sub(r"\s+", " ", s).strip()
        if len(s) >= 40 and s[:1].isalpha():
            return s
    return ""


def _outputs_section(name: str, st: SubmoduleStatus) -> str:
    mq = " A MultiQC HTML report aggregates QC across steps." if _produces_multiqc(st.path) else ""
    link = ""
    if (st.path / "docs" / "output.md").exists():
        link = ("\n\nThe exact output files and directory layout for this release are documented "
                f"upstream: https://github.com/nf-core/{name}/blob/{st.version}/docs/output.md")
    return (
        "Results land in `--outdir`, organised into one sub-directory per pipeline step/module; "
        "standardized run metadata in `<outdir>/pipeline_info/` (execution report, software "
        f"versions).{mq} `nfclaw run` also writes `<outdir>/provenance/` with the exact params "
        "file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, "
        "commit and exact command), input/output SHA-256 checksums, and a replayable "
        f"`commands.sh`.{link}\n"
    )


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
    out = ("| parameter | type | allowed values | constraints | description |\n"
           "|---|---|---|---|---|\n")
    for p in required:
        allowed = ", ".join(p.enum) if p.enum else ""
        out += (f"| `--{p.name.replace('_', '-')}` | {_type_with_fmt(p.type, p.fmt)} | "
                f"{_cell(allowed)} | {_constraints(p)} | {_cell(p.description)} |\n")
    return out


def _param_groups(ps: ParamSchema) -> str:
    """The schema's own parameter groups (names + full counts) — a deterministic map, no curation."""
    groups = sorted(ps.groups().items())
    if not groups:
        return "_No additional parameters._\n"
    lines = [f"- `{g or 'general'}` ({len(params)} parameter{'' if len(params) == 1 else 's'})"
             for g, params in groups]
    return ("Beyond the required parameters above, every other parameter is optional. "
            "[reference.md](reference.md) documents them all — type, default, allowed values and "
            "constraints — organised into these groups (counts are full group sizes, so they "
            "include any required parameters already listed above):\n" + "\n".join(lines) + "\n")


def _run_invocation(name: str, ps: ParamSchema, insch: InputSchema | None) -> tuple[str, str]:
    """The (nfclaw, raw nextflow) example commands. `--input` appears only when the pipeline
    has a samplesheet, and every schema-required param beyond input/outdir that has NO default
    is shown as an explicit `<placeholder>` (those carrying a default are filled by nf-schema, so
    the one-liner stays runnable as printed)."""
    inp = " --input samplesheet.csv" if insch is not None else ""
    extra = "".join(f" --{p.name.replace('_', '-')} <{p.name}>"
                    for p in ps.params.values()
                    if p.required and p.name not in ("input", "outdir") and p.default is None)
    nfclaw = f"nfclaw run {name}{inp} --outdir results{extra} -profile docker"
    raw = f"nextflow run pipelines/{name}/upstream -profile docker{inp} --outdir results{extra}"
    return nfclaw, raw


def _render_skill(name: str, st: SubmoduleStatus, ps: ParamSchema,
                  insch: InputSchema | None) -> str:
    desc = (ps.description.splitlines() or [name])[0]
    summary = _summary(st.path) or desc
    tools = _pipeline_tools(st.path)
    fm = (
        "---\n"
        f"name: {name}\n"
        f"pipeline: nf-core/{name}\n"
        f"version: {st.version}\n"
        f"commit: {st.commit}\n"
        f"description: {desc}\n"
        f"summary: {summary}\n"
        f"has_samplesheet: {str(insch is not None).lower()}\n"
        f"input: {_input_summary(insch)}\n"
        f"output: {_output_summary(st.path)}\n"
        f"tools: {', '.join(tools)}\n"
        "---\n"
    )
    tools_md = _tools_section(name, st, tools)
    tools_block = f"## Tools this pipeline runs\n{tools_md}\n" if tools_md else ""
    nfclaw_cmd, raw_cmd = _run_invocation(name, ps, insch)
    body = (
        f"# {name}\n\n{summary}\n\n"
        "## Run it\n```bash\n"
        f"git submodule update --init pipelines/{name}/upstream   # first time only\n"
        f"{nfclaw_cmd}\n"
        "# raw equivalent (the submodule is already pinned to this release, so no -r is needed):\n"
        f"{raw_cmd}\n```\n\n"
        f"## Inputs\n{_inputs_section(insch)}\n"
        f"## Required parameters\n{_required_params(ps)}\n"
        f"## Other parameters\n{_param_groups(ps)}\n"
        f"## Outputs\n{_outputs_section(name, st)}\n"
        f"{tools_block}"
        "## Demo\n```bash\n"
        f"nfclaw run {name} --demo --outdir results   # adds the upstream test profile (-profile test,docker)\n```\n\n"
        "## Full reference\n"
        "Every parameter — name, type, required, hidden, allowed values, constraints, default and "
        "description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. "
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
           "`constraints` lists each parameter's declared value bounds (pattern, min/max, length) — "
           "conditional or composed rules (e.g. anyOf/oneOf) are enforced by nf-schema at runtime.\n\n")
    for group, params in sorted(ps.groups().items()):
        out += f"## {group or 'general'}\n\n"
        out += ("| parameter | type | required | hidden | allowed values | constraints | "
                "default | description |\n|---|---|---|---|---|---|---|---|\n")
        for p in sorted(params, key=lambda x: x.name):
            default = "" if p.default is None else json_scalar(p.default)
            allowed = ", ".join(p.enum) if p.enum else ""
            req = "yes" if p.required else ""
            hid = "yes" if p.hidden else ""
            out += (f"| `--{p.name.replace('_', '-')}` | {_type_with_fmt(p.type, p.fmt)} | "
                    f"{req} | {hid} | {_cell(allowed)} | {_constraints(p)} | "
                    f"{_cell(default)} | {_cell(p.description)} |\n")
        out += "\n"
    out += f"<!-- Generated from nf-core/{name}@{st.commit}. Do not edit by hand. -->\n"
    return out


def render(name: str, *, pipelines_dir: Path) -> tuple[str, str]:
    """Return the (skill.md, reference.md) text for a pipeline WITHOUT writing anything, so the
    drift gate can compare against the committed files without mutating them."""
    st = submod.resolve(name, pipelines_dir)
    ps = schema_mod.load_param_schema(st.path)
    insch = schema_mod.load_input_schema(st.path)
    return _render_skill(name, st, ps, insch), _render_reference(name, st, ps, insch)


def generate(name: str, *, pipelines_dir: Path) -> tuple[Path, Path]:
    skill_text, ref_text = render(name, pipelines_dir=pipelines_dir)
    skill_path = pipelines_dir / name / "skill.md"
    ref_path = pipelines_dir / name / "reference.md"
    skill_path.write_text(skill_text, encoding="utf-8")
    ref_path.write_text(ref_text, encoding="utf-8")
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
