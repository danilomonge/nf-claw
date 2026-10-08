# Architecture

Four zones:
- **`pipelines/`** — the library content. One folder per nf-core pipeline: `upstream/` (submodule,
  pinned to a release tag) + a generated `skill.md` (run command, inputs and the schema's required
  parameters — each with its allowed values and value constraints — plus a map of its parameter
  groups) and `reference.md` (every parameter, with its required and hidden flags, allowed values,
  value constraints and default). Both are derived deterministically from the schema — never
  hand-curated, so they cannot drift from the pinned code.
- **`runner/`** — the runtime invoked as `nfclaw`. Discovers pipelines, runs deterministic
  pre-checks against the pipeline's own schema (samplesheet columns, unknown flags, scalar types,
  enum values and compatible value constraints — failing fast before Nextflow starts), composes a
  `-params-file`, runs `nextflow run` from `--outdir`, records the launch in
  `<outdir>/provenance/logs/run.log` (`runner/runlog.py`: nfclaw's header with host and pids,
  Nextflow's console in order, and a final outcome line written after the bundle; appended on
  `--resume` and for a relaunch refused before starting; on failure the error quotes Nextflow's
  report and the `Caused by:` chain of its log's last error, and names `run.log`, `.nextflow.log`
  and the failing task's `.command.err` by absolute path). `nfclaw status <outdir>` reads the state
  back from that log alone — the last line, or whether the recorded nfclaw is still running.
  SIGTERM/SIGHUP stop a run the way Ctrl-C does, and on Linux Nextflow is set to die with nfclaw
  even on SIGKILL. It then writes a provenance bundle. Nextflow's `nf-schema`
  plugin remains authoritative at runtime, including for conditional requirements and any schema
  constraints the lightweight pre-check cannot interpret safely.
  The bundle is written whether the run succeeds or fails — a failed run is precisely when the
  replay script is needed — and `run_manifest.json` records which it was (`outcome`).
  Every `NXF_*` variable the run saw is captured for replay, both the overrides nfclaw applied
  (`--nxf-ver`, `--nxf-env`) and those inherited from the shell (e.g. an exported `NXF_OFFLINE`),
  since Nextflow reads all of them. Values that look like credentials are redacted from the
  manifest and replay script; the script names those variables to supply externally.
  Replay preserves the declared launch settings: the nf-core template defaults `trace_report_suffix` to a timestamp evaluated
  afresh on every launch, and interpolates it into the execution report/timeline/trace/DAG
  filenames. nfclaw pins it in `params.json` (only where the pinned release declares the parameter,
  and never over a caller's value), so replaying the bundle reproduces the run's outputs instead of
  writing a second, differently-named set of reports beside them.
  A resource ceiling (`--limit-cpus`/`--limit-memory`/`--limit-time`) is likewise materialised into
  the bundle as `resource_limits.config` and passed with `-c`, so it too replays.
  Before launch, provenance snapshots local inputs (including schema-declared CSV/TSV data paths),
  configuration files, generated parameters, and tracked pipeline source bytes. A standalone Python
  guard refuses replay if these dependencies, their inventories or the pipeline commit changed.
  The replay pins the observed Nextflow version. Bundle files are replaced atomically and the
  manifest is published last; incomplete bundles cannot replay. Remote data, indirect configuration
  includes, non-tabular referenced payloads, untracked pipeline files and container image digests
  are not frozen. Identical launch settings do not guarantee identical scientific results.
  `commands.sh` reproduces the run into a **fresh** output directory (default `<outdir>.replay`,
  overridable by argument) and refuses a target that already holds files: an nf-core pipeline
  publishes into `--outdir` and cannot re-publish over a previous run's files, so replaying in place
  fails on contact. `--check` is side-effect-free for the same reason — it stages its params file in
  a temp directory, never in `--outdir`, so a dry run cannot spoil the directory the real run needs.
  Real runs hold a persistent sibling file lock on POSIX systems, preventing overlapping launches
  into the same output directory from replacing an active run's parameters or provenance.
  `--pipeline-version` selects another release (materialized as a git worktree of that tag under
  the git-ignored `pipelines/<name>/.versions/<tag>/`) or `dev`, nf-core's development branch. A
  branch moves, so `dev` is resolved to its head commit on every request and materialized per commit
  (`.versions/dev-<commit12>/`): once checked out a tree never changes, which keeps `commands.sh`
  replays faithful and lets two runs on different `dev` heads proceed side by side. The run warns
  that the code is unreleased, provenance records `version: dev` with the exact commit, and the
  last-resolved head is kept as `origin/dev` in the submodule clone as the offline fallback.
  `nfclaw chain run` (`runner/chain.py`) runs several pipelines in sequence: every stage is an
  ordinary run in `<outdir>/NN-<stage>/`, started only after the one before it succeeded, and
  `runner/handoff.py` prepares its parameters from that run's outputs — a samplesheet snapshot with
  absolute paths, validated against the next pipeline's samplesheet schema, each value traced to the
  digests in the upstream's `outputs.sha256`. Before the first stage launches, every stage's
  parameters, every handoff and every stage's config (`nextflow config`, with its own engine) are
  checked. The chain's record — spec, state, snapshots, a log whose last line is the outcome — lives
  in `<outdir>/chain/`; each stage's manifest links back to it. See [`chaining.md`](chaining.md).
- **`handoffs/`** — the rules for chaining: `handoffs/<upstream>/<downstream>.json`, hand-written data
  like `sources.tsv`. Each says where the upstream publishes what the downstream reads (fetchngs's
  `samplesheet/samplesheet.csv`) and how to adapt it; the drift gate checks every rule against both
  pipelines' pinned schemas, and the generated docs list them.
- **`librarian/`** — maintenance (run via `make`): generates `skill.md`/`reference.md`/`catalog.*`
  from each submodule, and bumps submodules to the latest release.

Key invariant: **no code knows any pipeline specifics** — every fact about one pipeline derives from
`nextflow_schema.json` / `assets/schema_input.json`, so a pipeline can change without breaking nf-claw.
The one kind of fact no schema carries — where one pipeline publishes input for another — lives as
data in `handoffs/`, and every claim it makes about parameters and samplesheet columns is checked
against the pinned schemas.

macOS note: keep the repo on a space-free, non-iCloud path (iCloud sync breaks git speed and Docker).
