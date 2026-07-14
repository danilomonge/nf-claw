# librarian/write_skill.py
from __future__ import annotations

import argparse
import re
from pathlib import Path

from runner import engine_version
from runner import schema as schema_mod
from runner import submodule as submod
from runner.schema import InputSchema, Param, ParamSchema, json_scalar
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


def _samplesheet_format(ps: ParamSchema | None) -> tuple[str, str, str]:
    """Return (extension, display name, delimiter) for generated samplesheet examples.

    nf-schema chooses the parser from the `--input` filename extension. Some upstream schemas
    require `.tsv` while their prose still says "comma-separated", so prefer the schema pattern
    over descriptions."""
    input_param = ps.params.get("input") if ps else None
    pattern = input_param.pattern if input_param else None
    if pattern and r"\.tsv" in pattern and r"\.csv" not in pattern:
        return "tsv", "TSV", "\t"
    return "csv", "CSV", ","


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


def _resources_section(name: str, ps: ParamSchema, insch: InputSchema | None,
                       pipeline_version: str | None = None) -> str:
    """How to run this pipeline on a machine smaller than its defaults assume.

    nf-core sizes every process from a resource label in `conf/base.config`, and those labels are
    written for a server: the stock `process_high` asks for tens of gigabytes, and Nextflow retries a
    failed task with *more*. On a workstation the run dies at the first such task — the failure the
    `test` profile never shows, because it ships its own small `resourceLimits` ceiling. The fix
    nf-core documents is that same ceiling, applied to a real run."""
    ext, _, _ = _samplesheet_format(ps)
    inp = f" --input samplesheet.{ext}" if insch is not None else ""
    ver = f" --pipeline-version {pipeline_version}" if pipeline_version else ""
    return (
        "A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks "
        "for, which are sized for a server — a single step can request far more memory than a "
        "workstation has, and Nextflow retries a failed step with more still. If a run fails with "
        "`Process requirement exceeds available memory` (or CPUs), cap every request, and every "
        "retry, at what this machine actually has:\n\n"
        "```bash\n"
        f"nfclaw run {name}{inp} --outdir results{ver} -profile docker \\\n"
        "  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h\n"
        "```\n\n"
        "nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` "
        "config — the mechanism nf-core prescribes for exactly this "
        "([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). "
        "Set them to the machine's real capacity. The generated config is kept in "
        "`<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.\n"
    )


def _reference_section(ps: ParamSchema) -> str:
    """Where the pipeline gets its reference genome when the caller does not say.

    nf-core resolves references through AWS iGenomes: `--genome <id>` is looked up under
    `igenomes_base`, which defaults to the S3 bucket `s3://ngi-igenomes/igenomes/`. When a release
    also gives `--genome` a **non-null default** (sarek defaults it to `GATK.GRCh38`), a run that
    passes no reference of its own silently resolves one over S3 — which fails on any host without
    access to that bucket, and pulls tens of gigabytes on one that has it. The schema says all of
    this; the docs did not, so the basic recipe looked runnable when it was not.

    Both facts are read straight from the schema, so this stays correct as releases change."""
    genome = ps.params.get("genome")
    base = ps.params.get("igenomes_base")
    if genome is None and base is None:
        return ""
    where = f" at `{base.default}`" if base is not None and base.default else ""
    ignore = " Set `--igenomes-ignore true` to disable the lookup entirely." \
        if "igenomes_ignore" in ps.params else ""
    if genome is not None and genome.default:
        return (
            f"**This release resolves a reference genome remotely by default.** `--genome` defaults "
            f"to `{genome.default}`, which is looked up in AWS iGenomes{where}. A run that passes no "
            f"reference of its own therefore reads its references over S3 — that fails on a host "
            f"without access to the bucket, and downloads tens of gigabytes on one that has it. For "
            f"a self-contained run, pass your own reference instead (the `reference_genome_options` "
            f"group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`)."
            f"{ignore}\n"
        )
    return (
        f"No reference genome is set by default: supply your own (the `reference_genome_options` "
        f"group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`). Passing "
        f"`--genome <id>` instead resolves the references from AWS iGenomes{where}, which needs "
        f"access to that bucket and downloads them.{ignore}\n"
    )


def _engine_section(name: str, st: SubmoduleStatus) -> str:
    """The Nextflow version this release declares, and how to run exactly that one.

    The engine is not a neutral detail: a release is written against the Nextflow line it declares,
    and a newer *major* changes the config parser. Running nf-core/scrnaseq 4.2.0 (which declares
    `!>=25.10.4`) on Nextflow 26.04.6 adds `Unrecognized config option 'validation.*'` warnings that
    the same run on 25.10.4 does not produce — verified by running both. The declared version is a
    fact in the pinned manifest, so it is surfaced here with the flag that pins it."""
    spec = engine_version.required_spec(st.path / "nextflow.config")
    if not spec:
        return ""
    pin = engine_version.minimum_version(spec)
    pin_line = ""
    if pin:
        pin_line = (f"\n\nTo run the engine this release targets — worth doing if a newer Nextflow "
                    f"emits config-parser warnings the release never saw:\n```bash\n"
                    f"nfclaw run {name} ... --nxf-ver {pin}\n```\n"
                    "`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same "
                    "engine. See [known-issues](../../docs/known-issues.md).")
    return f"This release declares `nextflowVersion = '{spec}'`.{pin_line}\n"


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


def _inputs_section(insch: InputSchema | None, ps: ParamSchema | None = None) -> str:
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
    ext, label, delimiter = _samplesheet_format(ps)
    input_note = _input_pattern_note(ps)
    tabular_intro = _tabular_intro(label, ps)
    if insch.one_of:
        # Mutually-exclusive column groups (items.oneOf): there is no single canonical header, so
        # list each allowed group and show one valid header per group (always-required columns +
        # that group). Surfacing this is exactly the signal an agent needs not to fill, say, both
        # `bam` and `cram`, or to mix ampliseq's legacy and standardized columns.
        base = [c.name for c in named if c.required]               # always-required columns
        groups = "\n".join("- " + ", ".join(f"`{col}`" for col in grp) for grp in insch.one_of)
        headers = "".join(
            f"```{ext}\n{delimiter.join(list(dict.fromkeys(base + list(grp))))}\n```\n"
            for grp in insch.one_of)
        return (f"{head}{rows}\n"
                f"{input_note}"
                f"The samplesheet is a {label}. Each row must include **exactly one** of these "
                "mutually-exclusive column groups (providing columns from more than one group "
                f"fails validation):\n{groups}\n\n"
                f"{_dependent_rules_section(insch)}"
                "Fill each value per the table above and `reference.md`. Valid headers — pick the "
                f"group that matches your data (optional columns from the table may be added):\n{headers}")
    # The header lists the columns the schema *requires*, not every column it allows. A pipeline can
    # declare optional columns that only apply to one aligner/mode (scrnaseq's `sample_type` and
    # `feature_type` are cellranger-arc/multi only), and emitting them all produces a header whose
    # extra fields an agent then has to fill or blank out. The required set is the one header that
    # is always valid; the optional columns are named right below it, so nothing is hidden.
    required_cols = [c.name for c in named if c.required]
    optional_cols = [c.name for c in named if not c.required]
    header_cols = required_cols or [c.name for c in named]     # no required column → show them all
    header_line = delimiter.join(header_cols)
    optional_note = ""
    if required_cols and optional_cols:
        cols = ", ".join(f"`{c}`" for c in optional_cols)
        optional_note = ("\nAny of the optional columns above may be appended to the header when "
                         f"your data needs them: {cols}.\n")
    required_note = " (the columns the schema requires)" if required_cols else ""
    return (f"{head}{rows}\n"
            f"{input_note}"
            f"{_dependent_rules_section(insch)}"
            f"{tabular_intro}{required_note}; fill each value per the table above "
            f"and `reference.md` (no example value is invented here):\n```{ext}\n{header_line}\n```\n"
            f"{optional_note}")


def _input_pattern_note(ps: ParamSchema | None) -> str:
    input_param = ps.params.get("input") if ps else None
    if input_param and input_param.pattern:
        return f"`--input` must match `{input_param.pattern}`.\n\n"
    return ""


def _tabular_intro(label: str, ps: ParamSchema | None) -> str:
    input_param = ps.params.get("input") if ps else None
    pattern = input_param.pattern if input_param else ""
    if pattern and "csv" in pattern and "tsv" in pattern:
        return "For tabular CSV/TSV input, use this header"
    return f"The samplesheet is a {label} with this header"


def _dependent_rules_section(insch: InputSchema) -> str:
    lines: list[str] = []
    for trigger, required in insch.dependent_required:
        reqs = ", ".join(f"`{req}`" for req in required)
        lines.append(f"- When `{trigger}` is set, also provide {reqs}.")
    options: list[str] = []
    for branch in insch.any_of_dependent_required:
        parts: list[str] = []
        for trigger, required in branch:
            reqs = ", ".join(f"`{req}`" for req in required)
            parts.append(f"{reqs} when `{trigger}` is set")
        options.append(" and ".join(parts))
    if options:
        lines.append(
            "- At least one of these conditional requirements must be satisfied: "
            + "; ".join(options)
            + "."
        )
    if not lines:
        return ""
    return "Additional row validation rules from the schema:\n" + "\n".join(lines) + "\n\n"


def _param_table(params: list[Param]) -> str:
    out = ("| parameter | type | default | allowed values | constraints | description |\n"
           "|---|---|---|---|---|---|\n")
    for p in params:
        allowed = ", ".join(p.enum) if p.enum else ""
        default = "" if p.default is None else json_scalar(p.default)
        out += (f"| `--{p.name.replace('_', '-')}` | {_type_with_fmt(p.type, p.fmt)} | "
                f"{_cell(default)} | {_cell(allowed)} | {_constraints(p)} | "
                f"{_cell(p.description)} |\n")
    return out


def _required_params(ps: ParamSchema) -> str:
    """Only the parameters the schema itself marks required — a fact, not a heuristic guess."""
    required = [p for p in ps.params.values() if p.required]
    if not required:
        return ("_The schema marks no parameter required; the pipeline runs with defaults. "
                "See reference.md to customise._\n")
    return _param_table(required)


def _is_mandatory_group(title: str) -> bool:
    """Whether a schema group is the authors' own 'these must be set' group.

    nf-core schemas mark required-ness in two independent places, and they do not always agree: the
    JSON-schema `required` list (what nf-schema enforces) and the group *title*. A parameter that
    carries a default is never in `required` — nf-schema has a value, so it cannot fail — yet the
    authors may still group it under "Mandatory arguments" because the pipeline itself rejects the
    default. nf-core/scrnaseq's `--protocol` is exactly that: it defaults to `auto`, and the
    workflow aborts on `auto` for every aligner but cellranger. Reading only `required` therefore
    understates the interface, so the group title is surfaced too."""
    t = title.strip().lower()
    return "mandator" in t or t.startswith("required")


def _mandatory_params(ps: ParamSchema) -> str:
    """Parameters the schema groups as mandatory but does not list in `required` (see above)."""
    params = [p for p in ps.params.values()
              if _is_mandatory_group(p.group_title) and not p.required]
    if not params:
        return ""
    return (
        "The schema groups these under **Mandatory arguments** — the pipeline authors' own label. "
        "They are absent from the `required` list above only because each carries a default, so "
        "nf-schema will not stop a run that omits them — but the pipeline itself can reject the "
        "default at runtime. Set them deliberately.\n\n"
        + _param_table(sorted(params, key=lambda p: p.name))
    )


def _param_groups(ps: ParamSchema) -> str:
    """The schema's own parameter groups (titles + full counts) — a deterministic map, no curation."""
    groups = sorted(ps.groups().items())
    if not groups:
        return "_No additional parameters._\n"
    lines = []
    for g, params in groups:
        title = next((p.group_title for p in params if p.group_title), "")
        label = f"**{title}** (`{g or 'general'}`)" if title else f"`{g or 'general'}`"
        lines.append(f"- {label} — {len(params)} parameter{'' if len(params) == 1 else 's'}")
    return ("Every parameter not listed above is optional as far as the schema is concerned. "
            "[reference.md](reference.md) documents them all — type, default, allowed values and "
            "constraints — organised into these groups (counts are full group sizes, so they "
            "include any parameter already listed above):\n" + "\n".join(lines) + "\n")


def _run_invocation(name: str, ps: ParamSchema, insch: InputSchema | None,
                    pipeline_version: str | None = None) -> tuple[str, str]:
    """The (nfclaw, raw nextflow) example commands. `--input` appears only when the pipeline
    has a samplesheet, and every schema-required param beyond input/outdir that has NO default
    is shown as an explicit `<placeholder>` (those carrying a default are filled by nf-schema, so
    the one-liner stays runnable as printed). When rendering a non-pinned version, the nfclaw
    command carries `--pipeline-version <tag>` and the raw command targets that version's tree."""
    ext, _, _ = _samplesheet_format(ps)
    inp = f" --input samplesheet.{ext}" if insch is not None else ""
    extra = "".join(f" --{p.name.replace('_', '-')} <{p.name}>"
                    for p in ps.params.values()
                    if p.required and p.name not in ("input", "outdir") and p.default is None)
    ver = f" --pipeline-version {pipeline_version}" if pipeline_version else ""
    upstream = (f"pipelines/{name}/.versions/{pipeline_version}/upstream"
                if pipeline_version else f"pipelines/{name}/upstream")
    nfclaw = f"nfclaw run {name}{inp} --outdir results{extra}{ver} -profile docker"
    raw = f"nextflow run {upstream} -profile docker{inp} --outdir results{extra}"
    return nfclaw, raw


def _render_skill(name: str, st: SubmoduleStatus, ps: ParamSchema,
                  insch: InputSchema | None, pipeline_version: str | None = None) -> str:
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
    nfclaw_cmd, raw_cmd = _run_invocation(name, ps, insch, pipeline_version)
    if pipeline_version:
        first_line = (f"# nfclaw fetches and materializes nf-core/{name}@{pipeline_version} "
                      "on first use; the default (no --pipeline-version) is the latest release.")
        raw_comment = f"# raw equivalent (runs the materialized {pipeline_version} tree directly):"
        demo_line = (f"nfclaw run {name} --demo --outdir results --pipeline-version {pipeline_version}"
                     "   # adds the upstream test profile (-profile test,docker)")
        version_note = ""                                     # the Run-it comment already explains the default
    else:
        first_line = f"git submodule update --init pipelines/{name}/upstream   # first time only"
        raw_comment = "# raw equivalent (the submodule is already pinned to this release, so no -r is needed):"
        demo_line = (f"nfclaw run {name} --demo --outdir results"
                     "   # adds the upstream test profile (-profile test,docker)")
        version_note = (f"This is the pinned latest release. To run a different one, list the available "
                        f"releases with `nfclaw versions {name}` and add `--pipeline-version X.Y.Z` to the "
                        f"command above (`nfclaw show {name} --pipeline-version X.Y.Z` prints that release's "
                        "docs).\n\n")
    reference = _reference_section(ps)
    reference_block = f"## Reference genome\n{reference}\n" if reference else ""
    engine = _engine_section(name, st)
    engine_block = f"## Nextflow engine\n{engine}\n" if engine else ""
    mandatory = _mandatory_params(ps)
    mandatory_block = f"## Mandatory arguments\n{mandatory}\n" if mandatory else ""
    body = (
        f"# {name}\n\n{summary}\n\n"
        "## Run it\n```bash\n"
        f"{first_line}\n"
        f"{nfclaw_cmd}\n"
        f"{raw_comment}\n"
        f"{raw_cmd}\n```\n\n"
        f"{version_note}"
        f"## Inputs\n{_inputs_section(insch, ps)}\n"
        f"## Required parameters\n{_required_params(ps)}\n"
        f"{mandatory_block}"
        f"{reference_block}"
        f"## Other parameters\n{_param_groups(ps)}\n"
        f"## Resources\n{_resources_section(name, ps, insch, pipeline_version)}\n"
        f"{engine_block}"
        f"## Outputs\n{_outputs_section(name, st)}\n"
        f"{tools_block}"
        "## Demo\n```bash\n"
        f"{demo_line}\n```\n\n"
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


def render_status(st: SubmoduleStatus, *, pipeline_version: str | None = None) -> tuple[str, str]:
    """Return the (skill.md, reference.md) text for an already-resolved tree — works for the
    pinned submodule and for any materialized version worktree alike. Nothing is written.
    `pipeline_version` makes the skill's run commands target that specific release; leave it
    None for the pinned default so the committed docs stay byte-stable."""
    ps = schema_mod.load_param_schema(st.path)
    insch = schema_mod.load_input_schema(st.path)
    # nf-core convention: a samplesheet is consumed via the `--input` parameter. A pipeline can
    # ship assets/schema_input.json without declaring an `input` param (it is parameter-driven —
    # e.g. drugresponseeval). There the file is not a `--input` samplesheet, so the skill must not
    # tell the agent to pass `--input` (the runner rejects unknown flags and would fail fast).
    samplesheet = insch if (insch is not None and "input" in ps.params) else None
    return (_render_skill(st.name, st, ps, samplesheet, pipeline_version),
            _render_reference(st.name, st, ps, samplesheet))


def render(name: str, *, pipelines_dir: Path) -> tuple[str, str]:
    """Return the (skill.md, reference.md) text for a pipeline WITHOUT writing anything, so the
    drift gate can compare against the committed files without mutating them."""
    return render_status(submod.resolve(name, pipelines_dir))


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
