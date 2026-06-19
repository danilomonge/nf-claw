---
name: demultiplex
pipeline: nf-core/demultiplex
version: 1.7.1
commit: fbec8e442f0599f8b74876e62263af05b9a41d33
description: Demultiplexing pipeline for Illumina sequencing data
has_samplesheet: true
---
# demultiplex

Demultiplexing pipeline for Illumina sequencing data

## Run it
```bash
git submodule update --init pipelines/demultiplex/upstream   # first time only
nfclaw run demultiplex --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/demultiplex/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `id` | string | yes |  | matches ^\S+$ |
| `samplesheet` | string (file path) | yes |  | matches ^\S+\.csv$ |
| `lane` | integer | no |  | ≥ 1; ≤ 8 |
| `flowcell` | string | yes |  |  |
| `per_flowcell_manifest` | string (file path) | no |  |  |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
id,samplesheet,lane,flowcell,per_flowcell_manifest
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--demultiplexer` | string | bases2fastq, bcl2fastq, bclconvert, fqtk, sgdemux, mkfastq, mgikit |  | Demultiplexer to use. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `checkqc_options` (1 parameter)
- `demultiplex_options` (1 parameter)
- `downstream_csv_options` (1 parameter)
- `generic_options` (17 parameters)
- `input_output_options` (10 parameters)
- `institutional_config_options` (6 parameters)
- `workflow_options` (8 parameters)

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

## Demo
```bash
nfclaw run demultiplex --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/demultiplex/blob/1.7.1/docs/usage.md

<!-- Generated from nf-core/demultiplex@fbec8e442f0599f8b74876e62263af05b9a41d33. Do not edit by hand. -->
