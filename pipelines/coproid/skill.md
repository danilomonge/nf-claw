---
name: coproid
pipeline: nf-core/coproid
version: 2.0.1
commit: 045d569d5b01b2d1572220718e64a6d054ad57eb
description:  COPROlite host IDentification 
has_samplesheet: true
---
# coproid

 COPROlite host IDentification 

## Run it
```bash
git submodule update --init pipelines/coproid/upstream   # first time only
nfclaw run coproid --input samplesheet.csv --outdir results --genome-sheet <genome_sheet> --kraken2-db <kraken2_db> --sp-sources <sp_sources> --sp-labels <sp_labels> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/coproid/upstream -profile docker --input samplesheet.csv --outdir results --genome-sheet <genome_sheet> --kraken2-db <kraken2_db> --sp-sources <sp_sources> --sp-labels <sp_labels>
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--genome-sheet` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the reference genomes. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--kraken2-db` | string (file path) |  |  | Path to a kraken2 database, can be a directory or *.tar.gz |
| `--sp-sources` | string (file path) |  |  | Sources TAXID count table in csv format for sourcepredict |
| `--sp-labels` | string (file path) |  |  | Labels for the sources table in csv format for sourcepredict |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `generic_options` (17 parameters)
- `input_output_options` (5 parameters)
- `institutional_config_options` (6 parameters)
- `pipeline_options` (11 parameters)

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

## Demo
```bash
nfclaw run coproid --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/coproid/blob/2.0.1/docs/usage.md

<!-- Generated from nf-core/coproid@045d569d5b01b2d1572220718e64a6d054ad57eb. Do not edit by hand. -->
