# nf-claw — nf-core pipelines for agents

This repo is a library of nf-core pipelines. Each lives in `pipelines/<name>/`:
`upstream/` (the pinned pipeline code, a git submodule) and `skill.md` (how to run it).

## Setup (first time)
Install once, from the repo root, so the `nfclaw` command is on PATH: `pip install -e .`
(use a virtualenv). No-install equivalent: run `python3 -m runner <cmd>` from the repo root
anywhere this doc shows `nfclaw <cmd>`.

## To run a pipeline
1. Find it: grep `catalog.json` (or `catalog.md`) for a keyword — do NOT read it whole.
2. Read `pipelines/<name>/skill.md` — the exact command, inputs, and required parameters for the pinned version.
3. Run: `nfclaw run <name> --input samplesheet.csv --outdir results -profile docker`
   (raw fallback: `nextflow run pipelines/<name>/upstream -profile docker ...` — the submodule is
   already pinned to the release, so no `-r`).

`nfclaw run` executes the pipeline for real — there is no preview/dry-run default. To see the exact
`nextflow` command that *would* run without launching it, add `--check` (it validates inputs and
parameters, prints the command, and exits; it writes nothing into `--outdir`, so you can still use
that directory for the real run). Add `--demo` to run the pinned release's bundled test profile end
to end.

## Replaying a run
`<outdir>/provenance/commands.sh` re-runs the recorded command. It reproduces the run into a **fresh**
directory (default `<outdir>.replay`, or pass one: `./commands.sh /path/to/fresh-dir`) and refuses a
target that already holds files. That is deliberate: an nf-core pipeline publishes into `--outdir`
and cannot re-publish over a previous run's files, so replaying in place fails immediately on
`pipeline_info/execution_trace_*.txt` (and on sarek's `manifest_*.bco.json`). A replay re-executes
the pipeline — it is a reproduction, not a `--resume` — and the result can be compared against the
original bundle's `outputs.sha256`.

Trust `skill.md` / `reference.md` over your own memory — they are generated from the pinned commit.
To set any parameter beyond the essentials, look it up in `pipelines/<name>/reference.md` (the complete
list, with allowed values and value constraints) — do not invent a flag or value. `nfclaw run` rejects
unknown flags, invalid allowed values and unambiguous scalar/shape errors before it starts;
`nf-schema` remains authoritative for the complete schema (especially conditionals and complex
constraints) at runtime. Only read `upstream/` for deep dives.

## To run a specific (non-latest) version
The default is always the pinned latest release. To run any other published release instead:
1. List the releases: `nfclaw versions <name>` (the pinned latest is flagged).
2. Read that version's docs: `nfclaw show <name> --pipeline-version X.Y.Z` — it fetches the tag,
   materializes it under `pipelines/<name>/.versions/X.Y.Z/` (git-ignored), and prints the `skill.md`
   generated from *that* release's schema (a `reference.md` is written alongside it). The params, flags
   and validation all come from X.Y.Z, not from latest.
3. Run it: `nfclaw run <name> --pipeline-version X.Y.Z --input samplesheet.csv --outdir results -profile docker`.
Only real release tags are accepted (semver, with or without a leading `v`); an unknown version fails fast
and lists what is available. Provenance records the exact version that ran.

## Tuning the Nextflow engine / environment
`nfclaw run` inherits your shell environment and passes it through to Nextflow. Two run flags make the
engine and its runtime explicit and reproducible (both are recorded in `<outdir>/provenance/`):
- `--nxf-ver X.Y.Z` — pin the Nextflow engine for this run (sets `NXF_VER`). Use it when a newer
  Nextflow breaks an older pipeline release (e.g. a config-parser change in a new Nextflow major), or
  to reproduce a prior run exactly. nfclaw judges the version requirement against this pin.
- `--nxf-env KEY=VALUE` — set an `NXF_*` variable for this run (repeatable). Common fixes:
  - IPv6-only host where the JVM can't reach GitHub for remote configs:
    `--nxf-env NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true`
  - skip remote config fetches entirely: `--nxf-env NXF_OFFLINE=true`
- `--config PATH` (or `-c`, repeatable) — pass an extra Nextflow config straight through (`-c`),
  e.g. a docker host-network config (`docker { runOptions = "--network host" }`) or custom resources.

## Running on a machine smaller than the pipeline assumes
nf-core sizes every process from a label in the pipeline's `conf/base.config`, tuned for a server:
one step can request far more memory than a workstation has (`Process requirement exceeds available
memory`), and Nextflow retries a failed step with *more*. `--demo` never shows this because nf-core's
`test` profile ships its own small ceiling; a real run has none. Set one:
`nfclaw run <name> ... --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h`
These become Nextflow's `process.resourceLimits` — the ceiling nf-core documents — applied to every
process and every retry, so one flag covers whatever the pipeline asks for next. Do not chase this
with `withName:` overrides: those re-size one named process's initial request, so you must name every
step that could exceed the host, and they do not cap the retry. The generated config is written to
`<outdir>/provenance/resource_limits.config` and replayed by `commands.sh`.

Any other environment (proxies, `JAVA_HOME`, …) is inherited from your shell unchanged. Each run
launches Nextflow from its `--outdir`, so its `.nextflow/` history is isolated and `--resume` resumes
that run (use a distinct `--outdir` per pipeline).

If a pipeline's `upstream/` is empty, initialise it first:
`git submodule update --init pipelines/<name>/upstream`

## Requirements (agent environment)
git · python 3.11+ (install nfclaw with `pip install -e .`) · nextflow (Java 17+) · docker or
singularity. **Use a space-free path on macOS *and* Linux** — many bioinformatics tools and
Nextflow's work directory mishandle spaces in paths; on macOS also avoid iCloud paths.

## Checking a replay
`nfclaw verify <replay-outdir> --against <original-outdir>` compares the two runs' `outputs.sha256`
**by path** and reports `identical` / `changed` / `missing` / `extra`. A *missing* or *extra* file
means the replay did different work (exit 1); a *changed* file does not — nf-core outputs embed
timestamps (reports, gzip headers, zip entries, MultiQC HTML), so the same file re-made from the same
inputs is legitimately not byte-identical. Never diff the two `outputs.sha256` files directly: each
line is `hash  path`, so one changed file appears as both a missing and an extra one.

## Reference genomes
Some releases resolve a reference **remotely by default** — sarek defaults `--genome` to
`GATK.GRCh38`, looked up in AWS iGenomes at `s3://ngi-igenomes/igenomes/` — so a run that passes no
reference of its own reads from S3 and fails on a host without access to that bucket. Each
`skill.md` states which case its pipeline is in under "Reference genome". Pass your own reference
(`--fasta`, …) for a self-contained run, or `--igenomes-ignore true` to disable the lookup.

## Warnings are not failures
A run (and its replay, which executes the identical command) can print warnings that are **not**
faults and are **not** nf-claw's: Nextflow reporting the `validation.*` config scope as unrecognised
(its linter does not see plugin-contributed scopes — upstream nf-schema issue), a pinned release
setting a parameter its own plugin removed (scrnaseq's `validationSchemaIgnoreParams` — `nfclaw run`
neutralises this one at the config layer via nf-schema's `validation.ignoreParams` and prints an
advisory recording that it did, leaving the pinned tree untouched), or a `test` profile that deliberately sets
conflicting references (rnaseq's `--gtf` with `--gff`). They are catalogued with their real cause in
[`docs/known-issues.md`](docs/known-issues.md) under "Warnings a run prints that are not faults".
Check there before reporting one: nf-claw wraps releases **unmodified**, so an upstream warning is
reproduced faithfully by design, not introduced.

## Run-time errors
Spaces in a path break many tools, so `nfclaw run` checks the repo path, the Nextflow work
directory and `--outdir` **before** launching and **fails fast** naming the offending path (pass
`--allow-spaces` to override) — a deterministic check, not a guess. For other failures (IPv6 host,
no-network database downloads, a too-new Nextflow config parser, known upstream-pipeline bugs) the
error points at the Nextflow log; the symptom→fix map is in
[`docs/known-issues.md`](docs/known-issues.md).
