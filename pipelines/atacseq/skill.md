---
name: atacseq
pipeline: nf-core/atacseq
version: 2.1.2
commit: 1a1dbe52ffbd82256c941a032b0e22abbd925b8a
description: ATACSeq peak-calling and differential analysis pipeline.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2, replicate, control, control_replicate)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
---
# atacseq

ATACSeq peak-calling and differential analysis pipeline.

## Run it
```bash
git submodule update --init pipelines/atacseq/upstream   # first time only
nfclaw run atacseq --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/atacseq/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string | no |  |  |
| `replicate` | integer | yes |  | matches ^[1-9][0-9]*$ |
| `control` | string | no |  | matches ^\S+$ |
| `control_replicate` | integer | no |  | matches ^[1-9][0-9]*$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2,replicate,control,control_replicate
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `adapter_trimming_options` (8 parameters)
- `alignment_options` (9 parameters)
- `deseq_qc_options` (2 parameters)
- `generic_options` (16 parameters)
- `input_output_options` (8 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)
- `peak_calling_options` (9 parameters)
- `process_skipping_options` (9 parameters)
- `reference_genome_options` (18 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/atacseq/blob/2.1.2/docs/output.md

## Demo
```bash
nfclaw run atacseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/atacseq/blob/2.1.2/docs/usage.md

<!-- Generated from nf-core/atacseq@1a1dbe52ffbd82256c941a032b0e22abbd925b8a. Do not edit by hand. -->
