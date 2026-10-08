# Engine & Version Compatibility

nf-claw wraps each nf-core pipeline **unmodified**, pinned to a commit resolved from a release tag. The runtime
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

### The Parser Transition
Nextflow 25.04 and 25.10 default to the legacy parser; the strict parser is opt-in via
`NXF_SYNTAX_PARSER=v2`. Starting with 26.04, strict syntax is the default, and the legacy parser
can be selected with `NXF_SYNTAX_PARSER=v1`. Strict configuration syntax rejects some Groovy
constructs allowed by older releases. See the official [strict syntax guide](https://docs.seqera.io/nextflow/strict-syntax)
and [26.04 migration notes](https://docs.seqera.io/nextflow/migrations/26-04).

Older pinned releases such as `chipseq` 2.1.0, `atacseq` 2.1.2 and `circdna` 1.1.0 have reproduced
parser failures with the default 26.04 parser. Pin an engine that works with that release;
a minimum-version declaration alone is not proof of compatibility with every later engine.

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
3. **Provenance Recording**: Both `--nxf-ver` and `--nxf-env` are recorded in `<outdir>/provenance/run_manifest.json`.
   Replay restores recorded non-sensitive `NXF_*` variables and pins the observed engine version;
   redacted secrets must be supplied again. Other environment variables and container digests are not frozen.

In pipeline chains (`nfclaw chain run`), each stage can declare its own `"nxf_ver"` in `spec.json`, allowing
modern and older pipelines to use different compatible engines within one chain.

---

## 3. Automated Continuous Validation

The repository validates engine and workflow compatibility using automated GitHub Actions workflows:

| Workflow | Scope & Verification Level | Failure Criteria |
|---|---|---|
| **`smoke.yml`** | Builds and preflights each pipeline's demo command via `nfclaw run --check --demo`. Validates schema parsing, CLI argument handling, and parameter composition without launching Nextflow tasks. | Any schema parsing exception, unknown parameter rejection, or invalid command assembly. |
| **`nextflow-validate.yml`** | Runs each pinned test profile with `-preview`, using the declared engine (or 24.10.5 when the declaration predates the preview-capable 22.10.0 floor). Checks configuration, applicable schema validation and DAG construction. Containers are not pulled or executed. | Any nonzero exit code, 15-minute timeout, initialization failure, or unresolvable remote staging. |
| **`tests.yml`** | Tests the wrapper on Linux/macOS, exercises a real deterministic Nextflow run/replay/chain, and audits/builds the website. | A failing test, dependency audit or build. |
| **`drift-check.yml`** | Regenerates all pinned pipeline context and checks catalog, manifest and handoff consistency. | Any detected drift. |
| **`demo-validation.yml`** | Executes the pinned demo in native Linux Docker, checks basic FastQC statistics against an independent FASTQ oracle and requires its static plot exports. | Analysis failure, incorrect checked statistics or missing/invalid plot exports. |

### Strict Exit Code Gating
Automated discovery and update workflows require **strict exit code 0** from Nextflow validation. Pipelines
with a recognized remote-input staging error are labelled `staging-unverified`; other errors and
timeouts are `rejected`. Both block automated merging. Some upstream completion handlers wait for
task results that preview never produces, so a compiled DAG can still fail the preview gate.
Reduced-output previews and actual test executions must be reported separately from default-profile acceptance.

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
