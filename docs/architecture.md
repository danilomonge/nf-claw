# nf-claw Architecture

nf-claw is designed around a single guiding invariant: **no runtime or generator code hardcodes
pipeline specifics**. Every parameter, samplesheet column, allowed value, and constraint is derived
deterministically from each pipeline's own `nextflow_schema.json` and `assets/schema_input.json`.

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
- **`upstream/`**: A pinned git submodule pointing to a validated nf-core release tag. Unmodified and vendor-clean.
- **`skill.md`**: A concise, agentic definition of the pipeline generated deterministically from its schema. Includes:
  - YAML frontmatter with pipeline identity, description, tool list (from upstream `CITATIONS.md`), and input/output structure.
  - Run command with raw Nextflow fallback.
  - Schema-defined input parameters, allowed values, regex constraints, and required fields.
  - Parameter groups map (`groups.csv` hierarchy).
  - Upstream documentation links and chaining relationships.
- **`reference.md`**: A comprehensive reference cataloging every parameter, type, required/hidden flag, constraint, default, and description.
- **`.versions/`** (git-ignored): On-demand worktrees materialized when running specific older releases or unreleased `dev` commits.

Because `skill.md` and `reference.md` are generated strictly from the pinned schema, they can never drift from the underlying code.

---

## 2. `runner/` — The Runtime Engine (`nfclaw`)

The runner executes pipelines, validates inputs before launch, enforces runtime isolation, records
provenance, and manages multi-stage pipeline chains.

### 2.1 Schema Preflight & Fast-Fail Parameter Validation
Before invoking Nextflow, `nfclaw run` executes fast, deterministic preflight checks (`runner/preflight.py`, `runner/schema.py`, `runner/parameters.py`, `runner/inputs.py`):
- Rejects unknown flags, typos, and syntax errors.
- Validates scalar types, boolean flags, numeric bounds, and enum choices.
- Validates samplesheet existence, column headers, required fields, and path formats.
- Ensures absolute path resolution: relative samplesheet paths are made absolute against the caller's working directory before Nextflow execution.
- Translates `--input false` to an unset `input` parameter in `params.json` for pipelines that support running without a samplesheet (e.g. sarek), preventing nf-schema type validation crashes.
- Emits clean, actionable diagnostics with `ErrorCode` and suggested fixes. Nextflow's runtime `nf-schema` plugin remains the ultimate authority for conditional constraints.

### 2.2 Run Execution & Sibling Directory Locking
- **Launch Isolation:** Nextflow is executed with its working directory pointed inside `--outdir`, isolating `.nextflow/` state, session databases, and caches to that run.
- **Sibling File Locking:** On POSIX systems, `runner/locking.py` acquires an exclusive, non-blocking sibling flock (`.{outdir.name}.nfclaw.lock`) before creating or modifying `--outdir`. Overlapping or concurrent runs into the same directory fail fast with `ErrorCode.ENVIRONMENT`, preventing corrupted session states or interleaved logs.
- **Dry-Run Safety:** `--check` is strictly side-effect-free: it stages parameters in temporary directories and never writes into `--outdir`, preserving clean directories for subsequent execution.

### 2.3 Process Lifecycle & Signal Trapping
- `runner/execution.py` traps `SIGTERM`, `SIGHUP`, and `SIGINT` (Ctrl-C).
- On receiving a stop signal, nfclaw cleanly initiates shutdown of Nextflow and all child tasks, finalizes output capture, records the termination outcome in the run log, and flushes provenance before exiting.
- On Linux, child processes are bound to the parent PID via `PR_SET_PDEATHSIG`, ensuring child tasks cannot be orphaned even if nfclaw is terminated abruptly.

### 2.4 Structured Logging & Status Inspection
- **`<outdir>/provenance/logs/run.log`**: Single authoritative log containing nfclaw launch metadata (command, PID, host, advisories), followed by Nextflow's console stream.
- **Outcome Line:** The log terminates with a machine-verifiable trailer line:  
  `==> nfclaw run finished <timestamp>: <outcome>`
- **Stream Separation:** `stdout.txt` and `stderr.txt` are maintained alongside `run.log`.
- **`nfclaw status <outdir>`**: Inspects run state directly from `run.log` without requiring external database lookups or process introspection. Reports `success`, `running`, `failed`, `terminated`, or `stopped without an outcome`.

### 2.5 Provenance Bundles & Dependency Hashing
Every execution (successful or failed) produces a complete provenance bundle in `<outdir>/provenance/`:
- `run_manifest.json`: Captures pipeline name, version, commit, exact command line, duration, outcome, and all active `NXF_*` environment variables (with credentials redacted).
- `inputs.sha256`: Cryptographic manifest of local input files and data paths referenced inside samplesheets.
- `outputs.sha256`: Cryptographic manifest of all generated output files.
- `source.sha256`: Digest snapshot of tracked pipeline source files.
- `configs.sha256`: Digests of external Nextflow configuration files passed via `-c`.
- `resource_limits.config`: Generated resource ceiling configuration when `--limit-*` flags are used.
- `trace_report_suffix`: Pinned to prevent timestamp collisions across re-executions.

### 2.6 Deterministic Replay & Replay Guard
- **`provenance/commands.sh`**: Standalone reproduction script that re-runs the exact recorded execution into a fresh output directory (default `<outdir>.replay`). Replaying in place is rejected to avoid output collisions with existing published artifacts.
- **`provenance/replay_guard.py`**: A zero-dependency script executed by `commands.sh` prior to launching Nextflow. Verifies that local inputs, referenced samplesheets, external configs, and pipeline git commits match the hashes in `provenance/*.sha256`. If inputs have drifted or disappeared, replay halts immediately.
- **Dynamic Relocation:** `commands.sh` automatically discovers the original bundle directory when the bundle has been relocated on disk.

### 2.7 Verification Engine (`nfclaw verify`)
- `runner/verify.py` compares replayed output files against the original run by path.
- **Structural Equivalence:** Separates file existence from byte equality. Masks run timestamps in `pipeline_info/` (`params_<timestamp>.json`) to avoid spurious missing/extra mismatches.
- **Strict Mode (`--strict`):** Enforces byte-for-byte identity across all non-timestamped files.
- **Scientific Caveat:** Output file matching proves workflow reproducibility, but does not certify analytical or biological truth.

### 2.8 Dynamic Version Selection & Dev Tracking
- `nfclaw run <name> --pipeline-version X.Y.Z`: Materializes the requested release tag as a git worktree in `pipelines/<name>/.versions/<tag>/`. Skill documentation is generated dynamically on demand.
- `nfclaw run <name> --pipeline-version dev`: Resolves nf-core's `dev` branch to its current remote head commit and materializes an immutable worktree in `.versions/dev-<commit12>/`. Caches heads locally for offline fallback.

### 2.9 Chaining Engine (`runner/chain.py`)
- Runs multi-pipeline workflows sequentially, passing outputs from stage $k$ to inputs of stage $k+1$.
- **Chain Locking:** Locks `<outdir>/chain/.lock` against concurrent chain execution.
- **Preflight Configuration Probe:** Runs `nextflow config` under each stage's pinned engine before launching stage 1, catching parser incompatibilities immediately.
- **Handoff Output Verification:** Validates that upstream output files match recorded checksums before constructing downstream inputs.
- **Lineage Verification:** `nfclaw chain status` cryptographically verifies the unbroken chain of custody from initial inputs through all intermediate stages.

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

Invoked via `make`, the librarian automates all repository maintenance without manual curation:
- **`write_skill.py`**: Generates `pipelines/<name>/skill.md` and `reference.md` from `nextflow_schema.json` and `assets/schema_input.json`.
- **`write_catalog.py`**: Compiles `catalog.json` and `catalog.md` across all tracked pipelines.
- **`check_drift.py`**: Enforces strict synchronization across `sources.tsv`, `.gitmodules`, filesystem directories, generated skills, references, and handoff rules.
- **`update_pipelines.py`**: Scans upstream remotes for new tags and bumps submodules.
- **`discover_pipelines.py`**: Scans nf-core for new DSL2 pipelines and scaffolds initial submodules.
