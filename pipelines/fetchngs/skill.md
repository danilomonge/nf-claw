---
name: fetchngs
pipeline: nf-core/fetchngs
version: 1.12.0
commit: 8ec2d934f9301c818d961b1e4fdf7fc79610bdc5
description: Pipeline to fetch metadata and raw FastQ files from public databases
summary: nf-core/fetchngs is a bioinformatics pipeline to fetch metadata and raw FastQ files from both public databases. At present, the pipeline supports SRA / ENA / DDBJ / GEO ids (see usage docs).
has_samplesheet: true
input: id list (one value per line)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions)
tools: Aspera CLI, Python, Requests, sra-tools
---
# fetchngs

nf-core/fetchngs is a bioinformatics pipeline to fetch metadata and raw FastQ files from both public databases. At present, the pipeline supports SRA / ENA / DDBJ / GEO ids (see usage docs).

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
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `deprecated_options` (1 parameter)
- `generic_options` (11 parameters)
- `input_output_options` (10 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/fetchngs/blob/1.12.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: Aspera CLI, Python, Requests, sra-tools.

Full list with references: https://github.com/nf-core/fetchngs/blob/1.12.0/CITATIONS.md

## Demo
```bash
nfclaw run fetchngs --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/fetchngs/blob/1.12.0/docs/usage.md

<!-- Generated from nf-core/fetchngs@8ec2d934f9301c818d961b1e4fdf7fc79610bdc5. Do not edit by hand. -->
