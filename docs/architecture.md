# Architecture

Three zones:
- **`pipelines/`** — the library content. One folder per nf-core pipeline: `upstream/` (submodule,
  pinned to a release tag) + a generated `skill.md` (run command, inputs, the schema's required
  parameters, and a map of its parameter groups) and `reference.md` (every parameter, with its
  required flag and allowed values). Both are derived deterministically from the schema — never
  hand-curated, so they cannot drift from the pinned code.
- **`runner/`** — the runtime invoked as `nfclaw`. Discovers pipelines, runs deterministic
  pre-checks against the pipeline's own schema (samplesheet columns, unknown flags, enum values —
  failing fast before Nextflow starts), composes a `-params-file`, runs `nextflow run`, and writes
  a provenance bundle. Full parameter validation (types, conditional requirements) is delegated to
  Nextflow's `nf-schema` plugin at runtime.
- **`librarian/`** — maintenance (run via `make`): generates `skill.md`/`reference.md`/`catalog.*`
  from each submodule, and bumps submodules to the latest release.

Key invariant: **no code knows any pipeline specifics** — every fact derives from
`nextflow_schema.json` / `assets/schema_input.json`, so a pipeline can change without breaking nf-claw.

macOS note: keep the repo on a space-free, non-iCloud path (iCloud sync breaks git speed and Docker).
