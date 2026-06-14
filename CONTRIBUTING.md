# Contributing

## Add a pipeline
1. Append to `sources.tsv`:  `name<TAB>https://github.com/nf-core/name.git<TAB>latest-release`
2. `git submodule add <url> pipelines/<name>/upstream` (pin to the latest release tag)
3. `make build` — generates `pipelines/<name>/skill.md` + `reference.md` and refreshes `catalog.*`
4. `make check` — drift gate + tests must pass

No per-pipeline Python is ever required: all context derives from the pipeline's own
`nextflow_schema.json` / `assets/schema_input.json`.

## Code
- `runner/` (runtime) and `librarian/` (maintenance) are pipeline-agnostic. Never hardcode
  pipeline names, parameter lists, or sample columns.
- TDD: write the failing test first. `make test`.
- Generated files must be deterministic (no volatile timestamps; the `commit` field is the stamp).
