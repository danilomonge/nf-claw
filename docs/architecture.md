# Architecture

Three zones:
- **`pipelines/`** — the library content. One folder per nf-core pipeline: `upstream/` (submodule,
  pinned to a release tag) + a generated `skill.md` (run command, inputs and the schema's required
  parameters — each with its allowed values and value constraints — plus a map of its parameter
  groups) and `reference.md` (every parameter, with its required and hidden flags, allowed values,
  value constraints and default). Both are derived deterministically from the schema — never
  hand-curated, so they cannot drift from the pinned code.
- **`runner/`** — the runtime invoked as `nfclaw`. Discovers pipelines, runs deterministic
  pre-checks against the pipeline's own schema (samplesheet columns, unknown flags, scalar types,
  enum values and compatible value constraints — failing fast before Nextflow starts), composes a
  `-params-file`, runs `nextflow run`, and writes a provenance bundle. Nextflow's `nf-schema`
  plugin remains authoritative at runtime, including for conditional requirements and any schema
  constraints the lightweight pre-check cannot interpret safely.
  The bundle is written whether the run succeeds or fails — a failed run is precisely when the
  replay script is needed — and `run_manifest.json` records which it was (`outcome`).
  Every `NXF_*` variable the run saw is captured for replay, both the overrides nfclaw applied
  (`--nxf-ver`, `--nxf-env`) and those inherited from the shell (e.g. an exported `NXF_OFFLINE`),
  since Nextflow reads all of them. Values that look like credentials are redacted from the
  manifest and replay script; the script names those variables to supply externally.
  Replay is *strict*: the nf-core template defaults `trace_report_suffix` to a timestamp evaluated
  afresh on every launch, and interpolates it into the execution report/timeline/trace/DAG
  filenames. nfclaw pins it in `params.json` (only where the pinned release declares the parameter,
  and never over a caller's value), so replaying the bundle reproduces the run's outputs instead of
  writing a second, differently-named set of reports beside them.
  A resource ceiling (`--limit-cpus`/`--limit-memory`/`--limit-time`) is likewise materialised into
  the bundle as `resource_limits.config` and passed with `-c`, so it too replays.
- **`librarian/`** — maintenance (run via `make`): generates `skill.md`/`reference.md`/`catalog.*`
  from each submodule, and bumps submodules to the latest release.

Key invariant: **no code knows any pipeline specifics** — every fact derives from
`nextflow_schema.json` / `assets/schema_input.json`, so a pipeline can change without breaking nf-claw.

macOS note: keep the repo on a space-free, non-iCloud path (iCloud sync breaks git speed and Docker).
