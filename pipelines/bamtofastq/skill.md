---
name: bamtofastq
pipeline: nf-core/bamtofastq
version: 2.2.1
commit: 8a295860c0c9221337dec7f2620709a47cea254d
description: Workflow converts one or multiple bam/cram files to fastq format
has_samplesheet: true
---
# bamtofastq

Workflow converts one or multiple bam/cram files to fastq format

## Run it
```bash
git submodule update --init pipelines/bamtofastq/upstream   # first time only
nfclaw run bamtofastq --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/bamtofastq/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample_id` | string | yes |  | matches ^\S+$ |
| `mapped` | string (file path) | yes |  | matches ^\S+\.(bam\|cram)$ |
| `index` | string (file path) | no |  | matches ^\S+\.(bai\|crai)$ |
| `file_type` | string | yes | bam, cram |  |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample_id,mapped,index,file_type
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `generic_options` (17 parameters)
- `input_output_options` (2 parameters)
- `institutional_config_options` (6 parameters)
- `main_options` (5 parameters)
- `reference_genome_options` (5 parameters)

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

## Demo
```bash
nfclaw run bamtofastq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/bamtofastq/blob/2.2.1/docs/usage.md

<!-- Generated from nf-core/bamtofastq@8a295860c0c9221337dec7f2620709a47cea254d. Do not edit by hand. -->
