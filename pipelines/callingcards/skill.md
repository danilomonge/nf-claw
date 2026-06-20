---
name: callingcards
pipeline: nf-core/callingcards
version: 1.0.0
commit: 20b66e785a822028eaa125583aad0747d55bba61
description: An automated processing pipeline for mammalian bulk calling cards experiments
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2, barcode_details)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
---
# callingcards

An automated processing pipeline for mammalian bulk calling cards experiments

## Run it
```bash
git submodule update --init pipelines/callingcards/upstream   # first time only
nfclaw run callingcards --input samplesheet.csv --outdir results --datatype <datatype> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/callingcards/upstream -profile docker --input samplesheet.csv --outdir results --datatype <datatype>
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  |  |
| `barcode_details` | string (file path) | yes |  | matches ^\S+\.json$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2,barcode_details
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--datatype` | string | yeast, mammals |  | This determines which workflow to run based on the organism and method from which the data originates. Current options are 'yeast' and 'mammals' |
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `alignment_options` (1 parameter)
- `generic_options` (16 parameters)
- `hops_counting_options` (1 parameter)
- `input_output_options` (8 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)
- `qc_options` (1 parameter)
- `read_processing_options` (6 parameters)
- `reference_genome_options` (11 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/callingcards/blob/1.0.0/docs/output.md

## Demo
```bash
nfclaw run callingcards --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/callingcards/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/callingcards@20b66e785a822028eaa125583aad0747d55bba61. Do not edit by hand. -->
