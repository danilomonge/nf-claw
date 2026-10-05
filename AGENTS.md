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
parameters, prints the command, and exits). Add `--demo` to run the pinned release's bundled test
profile end to end.

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
Only real release tags are accepted (semver, with or without a leading `v`) — plus `dev`, below; an
unknown version fails fast and lists what is available. Provenance records the exact version that ran.

## To run unreleased development code (`dev`)
Every nf-core pipeline develops on a `dev` branch and releases from it, so `dev` holds the changes
that are not in any release yet. To run it (the `nextflow run nf-core/<name> -r dev` equivalent):
`nfclaw run <name> --pipeline-version dev --input samplesheet.csv --outdir results -profile docker`
— every other flag works as for a release, e.g.
`nfclaw run fetchngs --pipeline-version dev --input ids.csv --outdir /path/to/out -profile binac2 --nxf-ver 25.10.4`.
- `dev` moves, so each run resolves it to the branch's **current head commit** and materializes that
  commit under `pipelines/<name>/.versions/dev-<commit12>/` (git-ignored, one immutable tree per commit,
  so a replay or a concurrent run never sees the code change). The run prints a warning naming the
  commit; provenance records `version: dev` plus that exact commit, and `commands.sh` replays it.
- Read its docs first — params can differ from the release: `nfclaw show <name> --pipeline-version dev`
  prints the `skill.md` generated from that commit (`reference.md` is written beside it).
- `nfclaw versions <name>` lists `dev` (with its head commit) after the releases.
- Offline, nfclaw falls back to the last `dev` head it fetched and says so; a pipeline with no `dev`
  branch fails fast. `--resume` warns when `dev` moved since the run it continues (Nextflow then
  re-runs only the tasks the change touched).
Prefer a release for results you need to reproduce from a version number; use `dev` for fixes or
features that are not released yet.

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

Any other environment (proxies, `JAVA_HOME`, …) is inherited from your shell unchanged. Each run
launches Nextflow from its `--outdir`, so its `.nextflow/` history is isolated and `--resume` resumes
that run (use a distinct `--outdir` per pipeline).

If a pipeline's `upstream/` is empty, initialise it first:
`git submodule update --init pipelines/<name>/upstream`

## Requirements (agent environment)
git · python 3.11+ (install nfclaw with `pip install -e .`) · nextflow (Java 17+) · docker or
singularity. **Use a space-free path on macOS *and* Linux** — many bioinformatics tools and
Nextflow's work directory mishandle spaces in paths; on macOS also avoid iCloud paths.

## Run-time errors
Spaces in a path break many tools, so `nfclaw run` checks the repo path, the Nextflow work
directory and `--outdir` **before** launching and **fails fast** naming the offending path (pass
`--allow-spaces` to override) — a deterministic check, not a guess. For other failures (IPv6 host,
no-network database downloads, a too-new Nextflow config parser, known upstream-pipeline bugs) the
error points at the Nextflow log; the symptom→fix map is in
[`docs/known-issues.md`](docs/known-issues.md).
