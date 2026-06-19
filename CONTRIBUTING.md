# Contributing

## Add a pipeline
1. Append to `sources.tsv`:  `name<TAB>https://github.com/nf-core/name.git<TAB>latest-release`
2. `git submodule add <url> pipelines/<name>/upstream`
3. Pin it to a release tag (the submodule lands on the default branch otherwise, so the
   generated `version` would be a branch commit): `git -C pipelines/<name>/upstream fetch --tags`
   then `git -C pipelines/<name>/upstream checkout tags/<X.Y.Z>` — or run `make update`, which
   pins every `latest-release` pipeline to its newest tag.
4. `make build` — generates `pipelines/<name>/skill.md` + `reference.md` and refreshes `catalog.*`
5. `make check` — drift gate + tests must pass

No per-pipeline Python is ever required: all context derives from the pipeline's own
`nextflow_schema.json` / `assets/schema_input.json`.

Pipelines must be **DSL2** (DSL1 was removed in Nextflow 22.03 and cannot run) and are run
with the Nextflow version each release declares in its manifest — there is no single global
version. See [`docs/compatibility.md`](docs/compatibility.md).

## Code
- `runner/` (runtime) and `librarian/` (maintenance) are pipeline-agnostic. Never hardcode
  pipeline names, parameter lists, or sample columns.
- TDD: write the failing test first. `make test`.
- Generated files must be deterministic (no volatile timestamps; the `commit` field is the stamp).
