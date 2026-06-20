---
name: chipseq
pipeline: nf-core/chipseq
version: 2.1.0
commit: 76e2382b6d443db4dc2396e6831d1243256d80b0
description: ChIP-seq peak-calling and differential analysis pipeline.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2, replicate, antibody, control, control_replicate)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
---
# chipseq

ChIP-seq peak-calling and differential analysis pipeline.

## Run it
```bash
git submodule update --init pipelines/chipseq/upstream   # first time only
nfclaw run chipseq --input samplesheet.csv --outdir results --fasta <fasta> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/chipseq/upstream -profile docker --input samplesheet.csv --outdir results --fasta <fasta>
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string | no |  |  |
| `replicate` | integer | no |  |  |
| `antibody` | string | no |  | matches ^\S+$ |
| `control` | string | no |  | matches ^\S+$ |
| `control_replicate` | string | no |  | matches ^\S+$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2,replicate,antibody,control,control_replicate
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--fasta` | string (file path) |  | matches ^\S+\.fn?a(sta)?(\.gz)?$ | Path to FASTA genome file. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `adapter_trimming_options` (7 parameters)
- `alignment_options` (8 parameters)
- `generic_options` (17 parameters)
- `input_output_options` (7 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)
- `peak_calling_options` (9 parameters)
- `process_skipping_options` (11 parameters)
- `reference_genome_options` (14 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/chipseq/blob/2.1.0/docs/output.md

## Demo
```bash
nfclaw run chipseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/chipseq/blob/2.1.0/docs/usage.md

<!-- Generated from nf-core/chipseq@76e2382b6d443db4dc2396e6831d1243256d80b0. Do not edit by hand. -->
