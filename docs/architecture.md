# nf-claw Architecture

nf-claw derives its parameter documentation and general input validation from each pipeline's
`nextflow_schema.json` and, where present, its input schema. Curated handoff rules and documented
compatibility adjustments supplement those schemas. The pinned upstream pipeline remains the
authority for its analysis and complete runtime validation.

The repository is structured into four distinct zones:

```
                  ┌────────────────────────────────────────┐
                  │             nf-claw Core               │
                  └────────────────────────────────────────┘
                                      │
     ┌──────────────────┬─────────────┴────────────┬──────────────────┐
     ▼                  ▼                          ▼                  ▼
┌──────────────┐ ┌──────────────┐          ┌──────────────┐ ┌────────────────┐
│  pipelines/  │ │   handoffs/  │          │   runner/    │ │   librarian/   │
│ (Submodules  │ │  (Chaining   │          │ (CLI, Engine │ │ (Drift Gate,   │
│  & Skills)   │ │    Rules)    │          │  & Runtime)  │ │  Generators)   │
└──────────────┘ └──────────────┘          └──────────────┘ └────────────────┘
```

---

## 1. `pipelines/` — The Library Content

Each pipeline lives in `pipelines/<name>/`:
- **`upstream/`**: A git submodule pinned to the commit resolved from an nf-core release tag, with upstream code unmodified.
- **`skill.md`**: A concise, agentic definition of the pipeline generated deterministically from its schema. Includes:
  - YAML frontmatter with pipeline identity, description, tool list (from upstream `CITATIONS.md`), and input/output structure.
  - Run command with raw Nextflow fallback.
  - Schema-defined input parameters, allowed values, regex constraints, and required fields.
  - Parameter groups from the upstream schema.
  - Upstream documentation links and chaining relationships.
- **`reference.md`**: A comprehensive reference cataloging every parameter, type, required/hidden flag, constraint, default, and description.
- **`.versions/`** (git-ignored): On-demand worktrees materialized when running specific older releases or unreleased `dev` commits.

The drift gate regenerates `skill.md` and `reference.md` from the pinned schemas and checks them
against the committed files. This detects stale generated context; it does not prove that an
upstream schema describes every behavior of its analysis code correctly.

---

## 2. `runner/` — The Runtime Engine (`nfclaw`)

The runner executes pipelines, validates inputs before launch, enforces runtime isolation, records
provenance, and manages multi-stage pipeline chains.

### 2.1 Schema Preflight & Fast-Fail Parameter Validation
Before invoking Nextflow, `nfclaw run` executes fast, deterministic preflight checks (`runner/preflight.py`, `runner/schema.py`, `runner/parameters.py`, `runner/inputs.py`):
- Rejects unknown flags, typos, and syntax errors.
- Validates scalar types, boolean flags, numeric bounds, and enum choices.
- Validates samplesheet existence, column headers, required fields, and path formats.
- Resolves the `--input` samplesheet path against the caller's working directory. Local data paths
  inside a samplesheet must already be absolute; relative entries are rejected.
- Translates `--input false` to an unset `input` parameter in `params.json` for pipelines that support running without a samplesheet (e.g. sarek), preventing nf-schema type validation crashes.
- Emits clean, actionable diagnostics with `ErrorCode` and suggested fixes. Nextflow's runtime `nf-schema` plugin remains the ultimate authority for conditional constraints.

### 2.2 Run Execution & Sibling Directory Locking
- **Launch Isolation:** Nextflow is executed with its working directory pointed inside `--outdir`, isolating `.nextflow/` state, session databases, and caches to that run.
- **Sibling File Locking:** On POSIX systems, `runner/locking.py` acquires an exclusive, non-blocking sibling flock (`.{outdir.name}.nfclaw.lock`) before creating or modifying `--outdir`. Overlapping or concurrent runs into the same directory fail fast with `ErrorCode.ENVIRONMENT`, preventing corrupted session states or interleaved logs.
- **Check Safety:** `--check` stages parameters in temporary directories and never writes into
  `--outdir`. Resolving a requested pipeline version may fetch tags or populate its version cache.

### 2.3 Process Lifecycle & Signal Trapping
- `runner/execution.py` traps `SIGTERM`, `SIGHUP`, and `SIGINT` (Ctrl-C).
- On receiving a stop signal, nfclaw signals Nextflow's process group, captures its final output,
  and attempts to record the termination outcome and provenance before exiting.
- On Linux, `PR_SET_PDEATHSIG` signals the direct Nextflow child if nfclaw dies abruptly. It does
  not by itself guarantee cleanup of detached processes, remote tasks, or containers.

### 2.4 Structured Logging & Status Inspection
- **`<outdir>/provenance/logs/run.log`**: Single authoritative log containing nfclaw launch metadata (command, PID, host, advisories), followed by Nextflow's console stream.
- **Outcome Line:** The log terminates with a machine-verifiable trailer line:  
  `==> nfclaw run finished <timestamp>: <outcome>`
- **Stream Separation:** `stdout.txt` and `stderr.txt` are maintained alongside `run.log`.
- **`nfclaw status <outdir>`**: Reads `run.log` and, for an unfinished run on the same host,
  checks the recorded process identity. Reports `success`, `running`, `failed`, `terminated`, or
  `stopped without an outcome`. Remote unfinished runs cannot be inspected locally.

### 2.5 Provenance Bundles & Dependency Hashing
Executions attempt to record a provenance bundle in `<outdir>/provenance/`, including failed runs.
Individual records are replaced atomically and the manifest is published last. Recording errors
prevent a successful outcome; the replay guard refuses an incomplete bundle.
- `run_manifest.json`: Captures pipeline name, version, commit, command, recording time, outcome,
  observed engine, operating system, and active `NXF_*` variables (with sensitive values redacted).
  Host/process identity is recorded in `logs/run.log`.
- `inputs.sha256`: Prelaunch snapshot of declared local input files, local schema path parameters,
  and schema-declared data paths inside CSV/TSV samplesheets, including directory inventories.
- `outputs.sha256`: Snapshot of published result files, excluding provenance and Nextflow state.
- `pipeline.sha256`: Prelaunch digest snapshot of tracked pipeline source files.
- `configs.sha256`: Digests of the resolved params file, generated configs and explicit external
  Nextflow configuration files passed via `-c`.
- `resource_limits.config`: Generated resource ceiling configuration when `--limit-*` flags are used.
- `trace_report_suffix`: A pinned parameter in `params.json` when supported by the upstream schema;
  other independently timestamped metadata can still change filenames.

Missing local path parameters without an upstream `exists: true` constraint are delegated to
Nextflow: they may be output/cache destinations. They produce a warning and an
`unverified_local_paths` manifest entry rather than a false input checksum. Required missing
inputs are refused. Remote data, profile-only references, indirect configuration includes,
container digests and data referenced by non-tabular input formats are not comprehensively frozen.

### 2.6 Deterministic Replay & Replay Guard
- **`provenance/commands.sh`**: Standalone reproduction script that re-runs the exact recorded execution into a fresh output directory (default `<outdir>.replay`). Replaying in place is rejected to avoid output collisions with existing published artifacts.
- **`provenance/replay_guard.py`**: A zero-dependency script executed by `commands.sh` prior to launching Nextflow. Verifies that local inputs, referenced samplesheets, external configs, and pipeline git commits match the hashes in `provenance/*.sha256`. If inputs have drifted or disappeared, replay halts immediately.
- **Dynamic Relocation:** `commands.sh` discovers its current bundle directory and rebases
  bundle-owned params/config arguments. External dependencies retain their recorded paths.

### 2.7 Verification Engine (`nfclaw verify`)
- `runner/verify.py` compares replayed output files against the original run by path.
- **Structural Equivalence:** Separates file inventory from byte equality. Pairs timestamped
  metadata paths in `pipeline_info/` while preserving file multiplicity and reporting byte changes.
- **Strict Mode (`--strict`):** Requires byte-for-byte identity for every paired result, including metadata.
- **Scientific Scope:** Inventory agreement alone establishes no analytical agreement. Matching
  bytes demonstrate agreement of the observed artifacts, not biological accuracy or universal reproducibility.

### 2.8 Dynamic Version Selection & Dev Tracking
- `nfclaw run <name> --pipeline-version X.Y.Z`: Materializes the requested release tag as a git worktree in `pipelines/<name>/.versions/<tag>/`. Skill documentation is generated dynamically on demand.
- `nfclaw run <name> --pipeline-version dev`: Resolves nf-core's `dev` branch to its current remote head commit and materializes an immutable worktree in `.versions/dev-<commit12>/`. Caches heads locally for offline fallback.

### 2.9 Chaining Engine (`runner/chain.py`)
- Runs multi-pipeline workflows sequentially, passing outputs from stage $k$ to inputs of stage $k+1$.
- **Chain Locking:** Locks `<outdir>/chain/.lock` against concurrent chain execution.
- **Preflight Configuration Probe:** Runs `nextflow config` under each stage's engine before
  launching stage 1. Parser failures, unavailable engines and inconclusive probes stop the chain.
- **Handoff Output Verification:** Validates that upstream output files match recorded checksums before constructing downstream inputs.
- **Lineage Verification:** `nfclaw chain status` checks recorded stage identities, live stage
  outputs, and handoff files/references against upstream and downstream checksum inventories.
  This checks the recorded links; it does not independently revalidate every original input,
  configuration or algorithm, or authenticate a bundle against deliberate rewriting.

---

## 3. `handoffs/` — Chaining Rules

Chaining rules live in `handoffs/<upstream>/<downstream>.json`. They describe how to transform an
upstream stage's outputs into a downstream stage's parameter inputs:
- Declarative source mappings (`samplesheet`, `build`, `file`, `upstream_param`).
- Row- and column-level transformations (`rename`, `set`, `add_empty`, `drop_rows_not_allowed`, `require_values`).
- Metagenomic assembly safety: Rules for pipelines such as `mag` explicitly isolate individual samples (`group: {sample}`) to avoid accidental multi-sample co-assembly pooling.
- **Drift Gate Check:** The drift gate statically validates every handoff rule against the pinned schemas of both participating pipelines.

---

## 4. `librarian/` — Maintenance & Code Generation

Invoked via `make`, the librarian automates generation and release tracking for the curated library:
- **`write_skill.py`**: Generates `pipelines/<name>/skill.md` and `reference.md` from `nextflow_schema.json` and `assets/schema_input.json`.
- **`write_catalog.py`**: Compiles `catalog.json` and `catalog.md` across all tracked pipelines.
- **`check_drift.py`**: Enforces strict synchronization across `sources.tsv`, `.gitmodules`, filesystem directories, generated skills, references, and handoff rules.
- **`update_pipelines.py`**: Scans upstream remotes for new tags and bumps submodules.
- **`discover_pipelines.py`**: Scans nf-core for new DSL2 pipelines and scaffolds initial submodules.
