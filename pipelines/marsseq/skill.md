---
name: marsseq
pipeline: nf-core/marsseq
version: 1.0.3
commit: b02ede773092f8a8a5999400acda6894d51b4d26
description: MARS-seq v2 preprocessing pipeline
summary: nf-core/marsseq is a bioinformatics single-cell preprocessing pipeline for MARS-seq v2.0 experiments. MARS-seq is a plate-based technique that can be combined with FACS in order to study rare populations of cells. On top of the pre-existing pipeline, we have developed an RNA velocity workflow that can be used to study cell dynamics using StarSolo. We do so by converting the raw FASTQ reads into 10X v2 format.
has_samplesheet: true
input: samplesheet (batch, fastq_1, fastq_2, amp_batches, seq_batches, well_cells)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: cutadapt, FastQC, fastp, STAR, STARsolo, MultiQC
---
# marsseq

nf-core/marsseq is a bioinformatics single-cell preprocessing pipeline for MARS-seq v2.0 experiments. MARS-seq is a plate-based technique that can be combined with FACS in order to study rare populations of cells. On top of the pre-existing pipeline, we have developed an RNA velocity workflow that can be used to study cell dynamics using StarSolo. We do so by converting the raw FASTQ reads into 10X v2 format.

## Run it
```bash
git submodule update --init pipelines/marsseq/upstream   # first time only
nfclaw run marsseq --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/marsseq/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions marsseq` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show marsseq --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `batch` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string | yes |  |  |
| `amp_batches` | string | yes |  | matches ^\S+.xlsx$ |
| `seq_batches` | string | yes |  | matches ^\S+.xlsx$ |
| `well_cells` | string | yes |  | matches ^\S+.xlsx$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
batch,fastq_1,fastq_2,amp_batches,seq_batches,well_cells
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `generic_options` (15 parameters)
- `input_output_options` (6 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)
- `reference_genome_options` (5 parameters)
- `rna_velocity` (2 parameters)
- `skip_steps` (1 parameter)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/marsseq/blob/1.0.3/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: cutadapt, FastQC, fastp, STAR, STARsolo, MultiQC.

Full list with references: https://github.com/nf-core/marsseq/blob/1.0.3/CITATIONS.md

## Demo
```bash
nfclaw run marsseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/marsseq/blob/1.0.3/docs/usage.md

<!-- Generated from nf-core/marsseq@b02ede773092f8a8a5999400acda6894d51b4d26. Do not edit by hand. -->
