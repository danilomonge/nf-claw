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
# raw equivalent:
nextflow run pipelines/fetchngs/upstream -r 1.12.0 -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required |
|---|---|---|
| `` | string | no |

Example `samplesheet.csv`:
```csv

value
```

## Key parameters
| parameter | type | description |
|---|---|---|
| `--input` | string | File containing SRA/ENA/GEO/DDBJ identifiers one per line to download their associated metadata and FastQ files. |
| `--outdir` | string | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--ena-metadata-fields` | string | Comma-separated list of ENA metadata fields to fetch before downloading data. |
| `--nf-core-pipeline` | string | Name of supported nf-core pipeline e.g. 'rnaseq'. A samplesheet for direct use with the pipeline will be created with the appropriate columns. |
| `--skip-fastq-download` | boolean | Only download metadata for public data database ids and don't download the FastQ files. |
| `--dbgap-key` | string | dbGaP repository key. |
| `--email` | string | Email address for completion summary. |
| `--config-profile-name` | string | Institutional config name. |
| `--config-profile-description` | string | Institutional config description. |
| `--config-profile-contact` | string | Institutional config contact information. |
| `--config-profile-url` | string | Institutional config URL link. |
| `--help` | boolean | Display help text. |
| `--version` | boolean | Display version and exit. |
| `--email-on-fail` | string | Email address for completion summary, only when pipeline fails. |
| `--plaintext-email` | boolean | Send plain-text email instead of HTML. |
| `--monochrome-logs` | boolean | Do not use coloured log outputs. |
| `--hook-url` | string | Incoming hook URL for messaging service |
| `--validationShowHiddenParams` | boolean | Show all params when using `--help` |
| `--validationFailUnrecognisedParams` | boolean | Validation of parameters fails when an unrecognised parameter is found. |
| `--validationLenientMode` | boolean | Validation of parameters in lenient more. |

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions).

## Demo
```bash
nfclaw run fetchngs --demo --outdir results   # uses upstream -profile test
```

## Full reference
Every parameter: [reference.md](reference.md) · upstream usage: https://github.com/nf-core/fetchngs/blob/1.12.0/docs/usage.md

<!-- Generated from nf-core/fetchngs@8ec2d934f9301c818d961b1e4fdf7fc79610bdc5. Do not edit by hand. -->
