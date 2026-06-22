---
name: fastqrepair
pipeline: nf-core/fastqrepair
version: 1.0.0
commit: 5f102cae4cfaa1d9281b9702ccc3738d9974e388
description: A pipeline that can be used to recover corrupted FASTQ.gz files, drop or fix uncompliant reads, remove unpaired reads, and settle reads that became disordered
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
---
# fastqrepair

A pipeline that can be used to recover corrupted FASTQ.gz files, drop or fix uncompliant reads, remove unpaired reads, and settle reads that became disordered

## Run it
```bash
git submodule update --init pipelines/fastqrepair/upstream   # first time only
nfclaw run fastqrepair --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/fastqrepair/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^\S+\.f(ast)?q(\.gz)?$ |
| `fastq_2` | string (file path) | no |  | matches ^\S+\.f(ast)?q(\.gz)?$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `generic_options` (17 parameters)
- `input_output_options` (7 parameters)
- `institutional_config_options` (6 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/fastqrepair/blob/1.0.0/docs/output.md

## Demo
```bash
nfclaw run fastqrepair --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/fastqrepair/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/fastqrepair@5f102cae4cfaa1d9281b9702ccc3738d9974e388. Do not edit by hand. -->
