# Compatibility

nf-claw wraps each nf-core pipeline **unmodified**, pinned to a release. What a pipeline
needs to run is therefore decided by that pinned release, not by nf-claw. Two rules follow.

## Only DSL2 pipelines are supported

Nextflow removed the original DSL1 syntax in **22.03**, so a DSL1 pipeline cannot run on any
currently-supported engine. nf-claw only includes **DSL2** pipelines:

- Auto-discovery (`librarian/discover_pipelines.py`) skips any pipeline whose nf-core entry is
  not DSL2, so DSL1 pipelines are never onboarded.
- If you add a pipeline by hand, it must be DSL2.

## Each pipeline runs with the Nextflow version it declares

There is **no single Nextflow version that runs every pipeline**. Each nf-core release declares
a minimum in its manifest (`nextflowVersion`, e.g. `!>=23.04.0` or `!>=26.04.0`) and is written
for the configuration parser that ships with that version:

- Older releases use config syntax that the **legacy** parser accepts.
- Newer releases (Nextflow **26.x** onward, where the **strict** parser became the default)
  use syntax the legacy parser rejects, and may require that newer engine outright.

So the only correct version for a given pipeline is the one **it declares**. nf-claw honours this:

- **`nfclaw run`** invokes the pinned pipeline directly; run it with a Nextflow that satisfies the
  release's declared minimum (a recent Nextflow that meets `nextflowVersion` is the safe choice).
  If your installed Nextflow is older than the pipeline's declared minimum, `nfclaw run` prints a
  non-blocking advisory before launching — Nextflow itself remains the authority and enforces the
  requirement at startup.
- **`.github/workflows/nextflow-validate.yml`** reads each pipeline's declared `nextflowVersion`
  and runs `-preview` with exactly that version — which both satisfies the requirement and matches
  the parser the release targets. Releases whose declared minimum predates `-preview`
  (Nextflow 22.06) are floored to a recent lenient-parser version that still runs their code.

`reference.md` and the website always show the **pinned version** of each pipeline; trust those
over any single global assumption.

## What the automation verifies

- **`smoke.yml`** builds and preflights each pipeline's demo command through `nfclaw`
  (schema parse, parameter validation, command assembly) — no Nextflow execution.
- **`nextflow-validate.yml`** runs each pipeline through `nextflow -preview`: Nextflow compiles
  it, resolves its config/profile, validates parameters and builds the task DAG, then stops
  before executing. A pipeline is **accepted** when it compiles, its config resolves and its
  parameters validate; a real **rejection** is a parse/version/parameter/DSL error. (`-preview`
  does not stage remote test inputs, so the rare pipeline that reads files while building its
  graph is still counted as accepted — staging data is part of running the analysis, which is
  left to nf-core's own per-release CI.)

## Environment

git · Python 3.11+ · **Nextflow (Java 17+)** · Docker or Singularity. On macOS, use a
space-free, non-iCloud path (Docker fails on paths with spaces).
