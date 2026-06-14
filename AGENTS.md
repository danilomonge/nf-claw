# nf-claw — nf-core pipelines for agents

This repo is a library of nf-core pipelines. Each lives in `pipelines/<name>/`:
`upstream/` (the pinned pipeline code, a git submodule) and `skill.md` (how to run it).

## To run a pipeline
1. Find it: grep `catalog.json` (or `catalog.md`) for a keyword — do NOT read it whole.
2. Read `pipelines/<name>/skill.md` — it has the exact command and inputs for the pinned version.
3. Run: `nfclaw run <name> --input samplesheet.csv --outdir results -profile docker`
   (raw fallback: `nextflow run pipelines/<name>/upstream -r <version> -profile docker ...`).

Trust `skill.md` / `reference.md` over your own memory — they are generated from the pinned
commit. Full parameters live in `pipelines/<name>/reference.md`. Only read `upstream/` for deep dives.

If a pipeline's `upstream/` is empty, initialise it first:
`git submodule update --init pipelines/<name>/upstream`

## Requirements (agent environment)
git · nextflow (Java 17+) · docker or singularity. On macOS, use a space-free, non-iCloud path.
