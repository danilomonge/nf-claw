---
name: hic
pipeline: nf-core/hic
version: 2.1.0
commit: fe4ac656317d24c37e81e7940a526ed9ea812f8e
description: Analysis of Chromosome Conformation Capture data (Hi-C)
summary: nf-core/hic is a bioinformatics best-practice analysis pipeline for Analysis of Chromosome Conformation Capture data (Hi-C).
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, MultiQC
---
# hic

nf-core/hic is a bioinformatics best-practice analysis pipeline for Analysis of Chromosome Conformation Capture data (Hi-C).

## Run it
```bash
git submodule update --init pipelines/hic/upstream   # first time only
nfclaw run hic --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/hic/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions hic` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show hic --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string | no |  |  |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `alignments` (6 parameters)
- `contact_maps` (8 parameters)
- `digestion_hi_c` (6 parameters)
- `dnase_hi_c` (2 parameters)
- `downstream_analysis` (4 parameters)
- `generic_options` (14 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)
- `reference_genome_options` (5 parameters)
- `skip_options` (7 parameters)
- `valid_pairs_detection` (8 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/hic/blob/2.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, MultiQC.

Full list with references: https://github.com/nf-core/hic/blob/2.1.0/CITATIONS.md

## Demo
```bash
nfclaw run hic --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/hic/blob/2.1.0/docs/usage.md

<!-- Generated from nf-core/hic@fe4ac656317d24c37e81e7940a526ed9ea812f8e. Do not edit by hand. -->
