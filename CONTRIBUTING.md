# Contributing to nf-claw

Welcome! nf-claw provides AI agents and bioinformaticians with a token-minimal, deterministic, and drift-free interface to nf-core workflows. Contributions are welcome across pipeline curation, chaining rules, runtime features, and documentation.

---

### Navigation

[Core Tenets](#core-development-tenets) • [Adding Pipelines](#adding-a-new-pipeline) • [Chaining Handoff Rules](#adding-a-chaining-handoff-rule) • [Code Quality & Testing](#development--code-quality) • [Makefile Targets](#makefile-targets) • [Agent Sync](#agent-guidance-sync)

---

## Core Development Tenets

All contributions must uphold four architectural invariants:

| Tenet | Rule & Invariant |
|---|---|
| **1. Pipeline-Agnostic Design** | Neither `runner/` (execution runtime) nor `librarian/` (maintenance) may hardcode pipeline names, parameter keys, or samplesheet column headers. All schema logic is derived dynamically from `nextflow_schema.json` and `assets/schema_input.json`. Pipeline-specific relationships exist solely as declarative data in `handoffs/*.json`. |
| **2. Deterministic Outputs** | Generated markdown and JSON documents must remain bit-identical across repeated runs on the same commits. Timestamps are forbidden in generated context; git commit hashes serve as immutable version anchors. |
| **3. Test-Driven Development (TDD)** | Every bugfix or new feature must be paired with regression tests. Write the failing test first, implement the minimal fix, and verify with `make test`. |
| **4. Zero-Drift Invariant** | Committed context (`skill.md`, `reference.md`, `catalog.*`) must always match pinned submodule code. Any discrepancy between context files and pinned submodules is rejected by the drift gate (`python3 -m librarian.check_drift`). |

---

## Adding a New Pipeline

All pipelines in nf-claw must be **DSL2** (DSL1 was removed in Nextflow 22.12 and cannot run).

### Step 1: Validate the Pipeline Name
Pipeline names must consist solely of ASCII letters, digits, dots, hyphens, and underscores, beginning and ending with an alphanumeric character:
```regex
^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$
```

| Candidate Name | Status | Rationale |
|---|---|---|
| `rnaseq` | Valid | Pure alphanumeric string. |
| `viral-recon_v2` | Valid | Alphanumeric with hyphens and underscores. |
| `../evil` | Invalid | Directory traversal attempt; rejected by sanitization. |
| `.hidden` | Invalid | Begins with a dot; special path component. |

### Step 2: Register in `sources.tsv`
Add a tab-separated entry to `sources.tsv`:
```tsv
<name>	https://github.com/nf-core/<name>.git	latest-release
```
The repository remote must point to official nf-core infrastructure (`https://github.com/nf-core/<name>.git`). The version tracking policy is `latest-release`.

### Step 3: Add and Pin the Git Submodule
```bash
git submodule add https://github.com/nf-core/<name>.git pipelines/<name>/upstream
git -C pipelines/<name>/upstream fetch --tags
git -C pipelines/<name>/upstream checkout tags/<X.Y.Z>   # Pin to a published release tag (e.g. 1.2.0)
```

> [!NOTE]
> Never leave the submodule pointing to `main`, `master`, or `dev`. An unpinned submodule causes context generation to record a branch commit rather than an immutable release tag.

### Step 4: Build Context Files
```bash
make build
```
This generates `pipelines/<name>/skill.md` and `pipelines/<name>/reference.md`, and recompiles `catalog.json` and `catalog.md`.

### Step 5: Verify Schema Drift and Tests
```bash
make check
```
Both `librarian.check_drift` and the full pytest suite must pass with 0 errors.

---

## Adding a Chaining Handoff Rule

Handoff rules describe how outputs published by an upstream pipeline are adapted into inputs for a downstream pipeline. Rules reside in `handoffs/<upstream>/<downstream>.json`.

### 1. Author the Rule File
Inspect the upstream pipeline's `docs/output.md` to identify output file paths, and the downstream pipeline's `assets/schema_input.json` to identify required samplesheet columns.

Example: `handoffs/fetchngs/rnaseq.json`:
```json
{
  "description": "Feed fetched FASTQ samplesheet into rnaseq",
  "upstream_params": {
    "nf_core_pipeline": "rnaseq"
  },
  "params": {
    "input": {
      "samplesheet": "samplesheet/samplesheet.csv",
      "provides": ["sample", "fastq_1", "fastq_2", "strandedness"]
    }
  }
}
```

### 2. Supported Source Mappings

| Source Type | Mapping Key | Description | Example |
|---|---|---|---|
| **Samplesheet** | `"samplesheet"` | Direct copy and transformation of an upstream samplesheet. `"provides"` asserts required columns. | `fetchngs` → `rnaseq` |
| **File** | `"file"` | Maps a single published output file to a downstream parameter. Globs must match exactly 1 file. | `rnaseq` → `differentialabundance` |
| **Build** | `"build"` | Synthesizes a new samplesheet from matching output files using `{placeholders}` for grouping. | `bamtofastq` → `rnaseq` |
| **Upstream Param** | `"upstream_param"` | Propagates a parameter value used in the upstream run to the downstream stage. | `rnaseq` `--gtf` → downstream `--gtf` |

### 3. Samplesheet Transformations
When mapping via `"samplesheet"`, transformations apply in strict sequential order:
- `"rename"`: `{"old_col": "new_col"}` — renames existing column headers.
- `"set"`: `{"column": "literal or {template}"}` — sets fixed values or templates per row.
- `"add_empty"`: `["column"]` — inserts missing columns with empty values.
- `"drop_rows_not_allowed"`: `["column"]` — filters out rows containing invalid enum values.
- `"require_values"`: `["column"]` — asserts that specified columns must not be empty.

### 4. Verify and Test Handoffs
```bash
# Verify static schema compatibility across both participating pipelines
python3 -m librarian.check_drift

# Rebuild catalog and test chaining specification in check-only mode
make build
nfclaw chain run spec.json --outdir /tmp/test-chain --check
```

---

## Development & Code Quality

### Environment Setup
Install the repository in editable mode within a Python 3.11+ virtual environment located on a space-free path:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Running Tests
```bash
make test                      # Run full pytest test suite
pytest tests/test_chain.py     # Run focused test module
pytest -k "test_verify"        # Run tests matching an expression
```

### Static Analysis & Linting
We enforce Ruff for code formatting and linting:
```bash
ruff check runner librarian
```

---

## Makefile Targets

| Target | Command | Description |
|---|---|---|
| `make build` | `write_skill --all && write_catalog` | Regenerate skills, references, and catalog files from pinned submodules. |
| `make update`| `update_pipelines && make build` | Discover newest release tags, bump submodules, and rebuild context. |
| `make check` | `check_drift && pytest` | Run schema drift verification followed by the complete pytest suite. |
| `make test`  | `pytest` | Execute all unit, regression, and integration tests. |

---

## Agent Guidance Sync

> [!IMPORTANT]
> **100% Byte-for-Byte Parity Required:**
> `AGENTS.md` and `CLAUDE.md` provide agent guidelines for Claude Code and other agentic runtimes. **They must remain 100% byte-identical.** The test `tests/test_agent_docs.py` enforces this equality. Whenever updating agent instructions, always mirror changes across both files.
