---
name: bacass
pipeline: nf-core/bacass
version: 2.6.1
commit: 5ed7c2dd9a05d2434d8ba39ace1116368a4ba570
description: Simple bacterial assembly and annotation
has_samplesheet: true
---
# bacass

Simple bacterial assembly and annotation

## Run it
```bash
git submodule update --init pipelines/bacass/upstream   # first time only
nfclaw run bacass --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/bacass/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `ID` | string | yes |  | matches ^\S+$ |
| `R1` | ['string', 'null'] or string | no |  |  |
| `R2` | ['string', 'null'] or string | no |  |  |
| `LongFastQ` | ['string', 'null'] or string | no |  |  |
| `Fast5` | ['string', 'null'] or string | no |  |  |
| `GenomeSize` | ['string', 'null'] or string | no |  |  |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
ID,R1,R2,LongFastQ,Fast5,GenomeSize
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  |  | Path to tab-separated sample sheet |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `annotation` (8 parameters)
- `assembly_parameters` (12 parameters)
- `assembly_polishing` (1 parameter)
- `busco_options` (5 parameters)
- `contamination_screening` (4 parameters)
- `generic_options` (17 parameters)
- `input_output_options` (3 parameters)
- `institutional_config_options` (6 parameters)
- `qc_and_trim` (13 parameters)
- `skipping_options` (7 parameters)

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

## Demo
```bash
nfclaw run bacass --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/bacass/blob/2.6.1/docs/usage.md

<!-- Generated from nf-core/bacass@5ed7c2dd9a05d2434d8ba39ace1116368a4ba570. Do not edit by hand. -->
