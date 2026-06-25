# nf-claw — nf-core pipelines for agents

This repo is a library of nf-core pipelines. Each lives in `pipelines/<name>/`:
`upstream/` (the pinned pipeline code, a git submodule) and `skill.md` (how to run it).

## Setup (first time)
Install once, from the repo root, so the `nfclaw` command is on PATH: `pip install -e .`
(use a virtualenv). No-install equivalent: run `python -m runner <cmd>` from the repo root
anywhere this doc shows `nfclaw <cmd>`.

## To run a pipeline
1. Find it: grep `catalog.json` (or `catalog.md`) for a keyword — do NOT read it whole.
2. Read `pipelines/<name>/skill.md` — the exact command, inputs, and required parameters for the pinned version.
3. Run: `nfclaw run <name> --input samplesheet.csv --outdir results -profile docker`
   (raw fallback: `nextflow run pipelines/<name>/upstream -profile docker ...` — the submodule is
   already pinned to the release, so no `-r`).

Trust `skill.md` / `reference.md` over your own memory — they are generated from the pinned commit.
To set any parameter beyond the essentials, look it up in `pipelines/<name>/reference.md` (the complete
list, with allowed values and value constraints) — do not invent a flag or value. `nfclaw run` rejects
unknown flags and values outside a parameter's allowed set before it starts, and `nf-schema` validates
the rest (types, patterns, ranges) at runtime. Only read `upstream/` for deep dives.

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

Any other environment (proxies, `JAVA_HOME`, …) is inherited from your shell unchanged.

If a pipeline's `upstream/` is empty, initialise it first:
`git submodule update --init pipelines/<name>/upstream`

## Requirements (agent environment)
git · python 3.11+ (install nfclaw with `pip install -e .`) · nextflow (Java 17+) · docker or
singularity. **Use a space-free path on macOS *and* Linux** — many bioinformatics tools and
Nextflow's work directory mishandle spaces in paths; on macOS also avoid iCloud paths.

## Run-time errors
Hitting a failure during a run (path spaces, an IPv6-only host, a tool downloading a database, a
Nextflow-version parse error, or a known upstream-pipeline bug)? The symptom→fix map is in
[`docs/known-issues.md`](docs/known-issues.md).
