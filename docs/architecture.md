# Architecture

Three zones:
- **`pipelines/`** — the library content. One folder per nf-core pipeline: `upstream/` (submodule,
  pinned to a release tag) + generated `skill.md` (essentials) + `reference.md` (all parameters).
- **`runner/`** — the runtime invoked as `nfclaw`. Discovers pipelines, validates inputs against the
  pipeline's own schema, composes a `-params-file`, runs `nextflow run`, and writes a provenance bundle.
  Parameter validation itself is delegated to Nextflow's `nf-schema` plugin.
- **`librarian/`** — maintenance (run via `make`): generates `skill.md`/`reference.md`/`catalog.*`
  from each submodule, and bumps submodules to the latest release.

Key invariant: **no code knows any pipeline specifics** — every fact derives from
`nextflow_schema.json` / `assets/schema_input.json`, so a pipeline can change without breaking nf-claw.

macOS note: keep the repo on a space-free, non-iCloud path (iCloud sync breaks git speed and Docker).
