# nf-claw — nf-core pipelines for agents

This repo is a library of nf-core pipelines. Each lives in `pipelines/<name>/`:
`upstream/` (the pinned pipeline code, a git submodule) and `skill.md` (how to run it).

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

If a pipeline's `upstream/` is empty, initialise it first:
`git submodule update --init pipelines/<name>/upstream`

## Requirements (agent environment)
git · python 3.11+ · nextflow (Java 17+) · docker or singularity. On macOS, use a space-free, non-iCloud path.
