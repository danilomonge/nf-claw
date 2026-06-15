# nf-claw — nf-core pipelines for agents

This repo is a library of nf-core pipelines. Each lives in `pipelines/<name>/`:
`upstream/` (the pinned pipeline code, a git submodule) and `skill.md` (how to run it).

## To run a pipeline
1. Find it: grep `catalog.json` (or `catalog.md`) for a keyword — do NOT read it whole.
2. Read `pipelines/<name>/skill.md` — the exact command, inputs, and required parameters for the pinned version.
3. Run: `nfclaw run <name> --input samplesheet.csv --outdir results -profile docker`
   (raw fallback: `nextflow run pipelines/<name>/upstream -r <version> -profile docker ...`).

Trust `skill.md` / `reference.md` over your own memory — they are generated from the pinned commit.
To set any parameter beyond the essentials, look it up in `pipelines/<name>/reference.md` (the complete
list, with allowed values) — do not invent a flag or value. `nfclaw run` rejects unknown flags and
out-of-range values before it starts, and `nf-schema` validates the rest at runtime. Only read
`upstream/` for deep dives.

If a pipeline's `upstream/` is empty, initialise it first:
`git submodule update --init pipelines/<name>/upstream`

## Requirements (agent environment)
git · nextflow (Java 17+) · docker or singularity. On macOS, use a space-free, non-iCloud path.
