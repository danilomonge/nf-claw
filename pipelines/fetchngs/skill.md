---
name: fetchngs
pipeline: nf-core/fetchngs
version: 1.12.0
commit: 8ec2d934f9301c818d961b1e4fdf7fc79610bdc5
description: Pipeline to fetch metadata and raw FastQ files from public databases
keywords: [fetchngs, nf-core, nextflow]
has_samplesheet: true
---
# fetchngs

Pipeline to fetch metadata and raw FastQ files from public databases

## Run it
```bash
git submodule update --init pipelines/fetchngs/upstream   # first time only
nfclaw run fetchngs --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/fetchngs/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
Input is a plain text file with one value per line (no header). Each value must match the pattern `^(((SR|ER|DR)[APRSX])|(SAM(N|EA|D))|(PRJ(NA|EB|DB))|(GS[EM]))(\d+)$`.

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.(csv\|tsv\|txt)$ | File containing SRA/ENA/GEO/DDBJ identifiers one per line to download their associated metadata and FastQ files. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
All other parameters are optional. Every one — with type, default and allowed values — is in [reference.md](reference.md), grouped as:
- `deprecated_options` (1 parameters)
- `generic_options` (11 parameters)
- `input_output_options` (10 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions).

## Demo
```bash
nfclaw run fetchngs --demo --outdir results   # uses upstream -profile test
```

## Full reference
Every parameter — name, type, required, allowed values, default — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/fetchngs/blob/1.12.0/docs/usage.md

<!-- Generated from nf-core/fetchngs@8ec2d934f9301c818d961b1e4fdf7fc79610bdc5. Do not edit by hand. -->
