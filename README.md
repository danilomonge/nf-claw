# nf-claw

A self-maintaining, token-minimal library of [nf-core](https://nf-co.re) pipelines for AI agents.
Each pipeline is a git submodule plus an auto-generated `skill.md` an agent reads to run it
correctly — no external lookups, no hallucinated flags.

## Layout
- `pipelines/<name>/` — `upstream/` (submodule, pinned to a release) + generated `skill.md` + `reference.md`
- `runner/` — the `nfclaw` runtime (run a pipeline); the agent's tool
- `librarian/` — builds the context files and bumps submodules (run via `make`)
- `catalog.md` / `catalog.json` — the index of available pipelines
- `sources.tsv` — the source list (name, url, version policy)

## Use
```bash
nfclaw list                  # or: python -m runner list
nfclaw run rnaseq --input samplesheet.csv --outdir results -profile docker
```

## Maintain
```bash
make build     # regenerate skill.md/reference.md/catalog from the submodules
make update    # bump submodules to the latest release tag, then rebuild
make check     # drift gate + tests
make test
```

## Add pipelines (scales to all ~150 nf-core pipelines)
Append a line to `sources.tsv` (`name<TAB>url<TAB>latest-release`), then:
```bash
git submodule add <url> pipelines/<name>/upstream
make build
```

## How it stays current
`.github/workflows/auto-update.yml` runs on a schedule: it finds each pipeline's newest release
with `git ls-remote --tags` (pure git, no APIs), checks it out, regenerates context, and opens a PR.
The drift gate guarantees committed context always matches the pinned submodule.

Requires: git, Nextflow (Java 17+), Docker/Singularity.
