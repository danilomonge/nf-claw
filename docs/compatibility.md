# Engine & Version Compatibility

nf-claw wraps each nf-core pipeline **unmodified**, pinned to a validated release tag. The runtime
requirements of any pipeline are therefore dictated by that pinned release and its upstream dependencies,
not by nf-claw.

---

## 1. Only DSL2 Pipelines Are Supported

Nextflow permanently removed legacy DSL1 workflow syntax in version **22.12** (DSL2 became the default in 22.03).
Consequently, DSL1 workflows cannot execute on modern Nextflow runtimes:

- **Automated Discovery:** `librarian/discover_pipelines.py` inspects nf-core metadata and skips any pipeline
  that is not marked as DSL2, ensuring legacy workflows are never onboarded.
- **Manual Additions:** Any pipeline contributed manually must adhere to DSL2 structure.

---

## 2. Matching Nextflow Engine to Pinned Releases

There is **no single Nextflow version that can run every pipeline release**. Each nf-core release
declares its minimum engine requirement in `nextflow.config` via `manifest.nextflowVersion`
(e.g., `!>=23.04.0` or `!>=25.10.4`), and is authored against the configuration parser of its era:

### The Parser Transition (Nextflow 25 vs. 26)
- **Legacy Parser (Nextflow ≤ 25.x):** Lenient toward Groovy constructs in configuration files, such as
  helper functions (e.g. `def check_max(obj, type)`), dynamic property access, and non-strict include statements.
- **Strict Parser (Nextflow ≥ 26.x):** Enforces strict declarative syntax before plugins load. Rejects
  Groovy function definitions, parse-time `manifest.*` / `validation.*` references, and missing include targets.
  Older pipeline releases (such as `chipseq` 2.1.0, `atacseq` 2.1.2, or `circdna` 1.1.0) fail at launch
  under Nextflow 26 with syntax errors unless an earlier engine is pinned.

### Runtime Engine Controls in `nfclaw`
To ensure reproducible execution across releases of varying ages, nf-claw provides explicit engine controls:

1. **`--nxf-ver X.Y.Z`**: Pins the Nextflow version for a run by setting `NXF_VER`. Nextflow's launcher
   automatically downloads and executes the requested version.
   - If your host Nextflow is too new for an older pipeline release, pin an engine that matches its era:
     ```bash
     nfclaw run chipseq --input samplesheet.csv --outdir results -profile docker --nxf-ver 25.10.4
     ```
   - If the installed engine is older than the pipeline's declared `nextflowVersion`, `nfclaw run` prints an
     informational advisory before launching.
2. **`--nxf-env KEY=VALUE`**: Passes `NXF_*` variables directly to Nextflow:
   - IPv6-only environments: `--nxf-env NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true`
   - Air-gapped / offline runs: `--nxf-env NXF_OFFLINE=true`
3. **Provenance Recording**: Both `--nxf-ver` and `--nxf-env` are recorded in `<outdir>/provenance/run_manifest.json`,
   and `commands.sh` reproduces the exact engine environment upon replay.

In pipeline chains (`nfclaw chain run`), each stage can declare its own `"nxf_ver"` in `spec.json`, allowing
modern and older pipelines to coexist seamlessly within a single multi-stage workflow.

---

## 3. Automated Continuous Validation

The repository validates engine and workflow compatibility using automated GitHub Actions workflows:

| Workflow | Scope & Verification Level | Failure Criteria |
|---|---|---|
| **`smoke.yml`** | Builds and preflights each pipeline's demo command via `nfclaw run --check --demo`. Validates schema parsing, CLI argument handling, and parameter composition without launching Nextflow tasks. | Any schema parsing exception, unknown parameter rejection, or invalid command assembly. |
| **`nextflow-validate.yml`** | Compiles each pipeline using `nextflow run -profile test,docker -preview` under its declared minimum Nextflow version. Validates task DAG construction, nf-schema rules, and container references without scheduling compute tasks. | Any nonzero exit code, timeout (>15 min), initialization failure, or unresolvable remote staging. |

### Strict Exit Code Gating
Automated discovery and update workflows require **strict exit code 0** from Nextflow validation. Pipelines
exhibiting remote test data staging failures or network timeouts are classified as `staging-unverified` and
are excluded from automated merging.

*Note: Successful preview and smoke verification confirms syntactic correctness and DAG construction within
the tested environment; it does not constitute execution or biological verification on experimental datasets.*

---

## 4. Host Environment Requirements

- **Operating System:** Linux (x86_64 or aarch64) or macOS.
- **Python:** Version 3.11+.
- **Java:** Java 17+ (required by Nextflow).
- **Workflow Engine:** Nextflow (installed on PATH).
- **Container Runtime:** Docker or Singularity/Apptainer.
- **Filesystem Paths:** Repository checkouts, Nextflow working directories (`work/`), and output directories
  (`--outdir`) **must not contain whitespace characters**. Many bioinformatics CLI tools mishandle unquoted
  space characters. On macOS, avoid iCloud-synchronized directories to prevent file locking delays.
