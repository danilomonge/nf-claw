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

- **`nfclaw run`** invokes the pinned pipeline directly. Run it with a Nextflow that satisfies the
  release's declared minimum **and isn't so new that its stricter config parser rejects the
  release** — e.g. an older release such as sarek 3.8.1 fails on Nextflow 26.x, which made the
  strict parser the default. When the installed engine doesn't fit (too old *or* too new), pin the
  engine the release was written for with **`--nxf-ver X.Y.Z`** (sets `NXF_VER`; Nextflow then
  bootstraps that exact version for the run, and it is recorded in provenance). If your installed
  Nextflow is older than the declared minimum, `nfclaw run` prints a non-blocking advisory before
  launching — with `--nxf-ver` the advisory judges the pinned version instead. Nextflow itself
  remains the authority and enforces the requirement at startup.

  Beyond the engine version, **`--nxf-env KEY=VALUE`** (repeatable) sets any `NXF_*` variable for a
  run — e.g. `NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true` on an IPv6-only host whose JVM
  can't reach GitHub for remote configs, or `NXF_OFFLINE=true` to skip remote config fetches. The
  rest of the environment is inherited from your shell. Both flags are recorded in
  `<outdir>/provenance/` for replay.
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
