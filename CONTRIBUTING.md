# Contributing to nf-claw

Welcome! nf-claw is designed to provide AI agents and bioinformaticians with a token-minimal,
deterministic, and drift-free interface to nf-core workflows. Contributions are welcome across
pipeline curation, chaining rules, runtime features, and documentation.

---

## Core Development Tenets

1. **Pipeline-Agnostic Code:** Neither `runner/` (runtime) nor `librarian/` (maintenance) may ever
   hardcode pipeline names, parameter keys, or samplesheet column headers. All pipeline logic is derived
   dynamically from upstream `nextflow_schema.json` and `assets/schema_input.json`. Pipeline-specific
   relationships exist solely as data files in `handoffs/*.json`.
2. **Deterministic Outputs:** Generated markdown and JSON documents must remain bit-identical across
   repeated runs on the same commits. Volatile timestamps are forbidden in context generation; git commit
   hashes serve as immutable version anchors.
3. **Test-Driven Development (TDD):** Every bugfix or new feature must be paired with regression tests.
   Write the failing test first, implement the minimal fix, and verify with `make test`.
4. **Zero-Drift Invariant:** The library context (`skill.md`, `reference.md`, `catalog.*`) must always
   match the pinned submodule code. Any discrepancy between committed context and pinned submodules is
   caught and rejected by the drift gate (`python3 -m librarian.check_drift`).

---

## Adding a New Pipeline

All pipelines in nf-claw must be **DSL2** (DSL1 was removed in Nextflow 22.12 and cannot run).
To onboard a new pipeline:

### 1. Validate the Pipeline Name
Pipeline names must consist solely of ASCII letters, digits, dots, hyphens, and underscores,
and must begin and end with an alphanumeric character (`^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$`).
Special path components (`.`, `..`, `/`, `\`) are strictly prohibited.

### 2. Append to `sources.tsv`
Add a tab-separated entry to `sources.tsv`:
```tsv
<name>	https://github.com/nf-core/<name>.git	latest-release
```
The repository remote must point to `https://github.com/nf-core/<name>.git`. The version policy column
is typically `latest-release`.

### 3. Add and Pin the Git Submodule
```bash
git submodule add https://github.com/nf-core/<name>.git pipelines/<name>/upstream
git -C pipelines/<name>/upstream fetch --tags
git -C pipelines/<name>/upstream checkout tags/<X.Y.Z>   # Pin to a published release tag (e.g., 1.2.0)
```
*Note: Never leave the submodule on `master`, `main`, or `dev`. An unpinned submodule causes generation
to record a branch commit instead of a formal release version.*

### 4. Build Context Files
```bash
make build
```
This generates `pipelines/<name>/skill.md` and `pipelines/<name>/reference.md`, and regenerates
`catalog.json` and `catalog.md`.

### 5. Verify Drift and Test Suite
```bash
make check
```
Both `librarian.check_drift` and the full pytest suite must pass with 0 errors.

---

## Adding a Chaining Handoff Rule

Handoff rules define how the outputs of an upstream pipeline are transformed into the inputs of a
downstream pipeline. Rules live in `handoffs/<upstream>/<downstream>.json`.

### 1. Author the Rule File
Inspect the upstream pipeline's `docs/output.md` to identify output file paths, and the downstream
pipeline's `assets/schema_input.json` to identify required samplesheet columns.

Example `handoffs/upstream_pipe/downstream_pipe.json`:
```json
{
  "description": "Short summary of the handoff shown in skill.md and CLI",
  "upstream_params": {
    "nf_core_pipeline": "downstream_pipe"
  },
  "params": {
    "input": {
      "samplesheet": "samplesheet/samplesheet.csv",
      "provides": ["sample", "fastq_1", "fastq_2"]
    }
  }
}
```

### Supported Source Mappings
- **`samplesheet`**: Direct copy of an upstream samplesheet. Optional transforms:
  - `"rename": {"old_col": "new_col"}`
  - `"set": {"column": "literal or {template}"}`
  - `"add_empty": ["column"]`
  - `"drop_rows_not_allowed": ["column"]`
  - `"require_values": ["column"]`
- **`build`**: Synthesizes a new samplesheet from matching output files via glob placeholders.
- **`file`**: Maps a single output file path to a downstream parameter.
- **`upstream_param`**: Propagates a parameter value used in the upstream run to the downstream stage.

### 2. Verify Schema Compatibility
```bash
python3 -m librarian.check_drift
```
The drift checker validates that all parameters and columns declared in the handoff rule exist and
conform to both pipelines' pinned schemas.

### 3. Rebuild and Test
```bash
make build
nfclaw chain run spec.json --outdir /tmp/test-chain --check
```

---

## Development & Code Quality

### Environment Setup
Install the repository in editable mode within a Python 3.11+ virtual environment located on a
space-free path:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Running Tests
```bash
make test                      # Run full pytest suite
pytest tests/test_chain.py     # Run focused test module
pytest -k "test_verify"        # Run tests matching an expression
```

### Code Formatting and Linting
We use Ruff for static analysis. Configuration is defined in `pyproject.toml`:
```bash
ruff check runner librarian
```

### Makefile Targets
| Target | Command | Purpose |
|---|---|---|
| `make build` | `write_skill --all && write_catalog` | Regenerate skills, references, and catalog |
| `make update`| `update_pipelines && make build` | Bump submodules to newest release tags and rebuild |
| `make check` | `check_drift && pytest` | Run schema drift gate followed by test suite |
| `make test`  | `pytest` | Execute all unit and regression tests |

---

## Agent Guidance Sync

`AGENTS.md` and `CLAUDE.md` provide agent guidelines for Claude Code and other agentic environments.
**They must remain 100% byte-identical.** The test `tests/test_agent_docs.py` enforces this equality.
Whenever updating agent documentation, ensure changes are mirrored identically across both files.
