---
name: scrnaseq
pipeline: nf-core/scrnaseq
version: 4.1.0
commit: f7bf36d7c7e4bddc5302c3facd8d19ca83e22226
description: Pipeline for processing 10x Genomics single cell rnaseq data
keywords: [scrnaseq, nf-core, nextflow]
has_samplesheet: true
---
# scrnaseq

Pipeline for processing 10x Genomics single cell rnaseq data

## Run it
```bash
git submodule update --init pipelines/scrnaseq/upstream   # first time only
nfclaw run scrnaseq --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/scrnaseq/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | yes |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `fastq_barcode` | string | no |  |  |
| `expected_cells` | integer | no |  |  |
| `seq_center` | string | no |  |  |
| `sample_type` | string | no | atac, gex |  |
| `feature_type` | string | no | gex, vdj, ab, crispr, cmo |  |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2,fastq_barcode,expected_cells,seq_center,sample_type,feature_type
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `cellranger_multi_options` (9 parameters)
- `cellranger_options` (2 parameters)
- `cellrangerarc_options` (3 parameters)
- `generic_options` (16 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `kallisto_bus_options` (4 parameters)
- `mandatory_arguments` (3 parameters)
- `reference_genome_options` (9 parameters)
- `simpleaf_options` (2 parameters)
- `skip_tools` (4 parameters)
- `starsolo_options` (4 parameters)

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions).

## Demo
```bash
nfclaw run scrnaseq --demo --outdir results   # uses upstream -profile test
```

## Full reference
Every parameter — name, type, required, allowed values, default — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/scrnaseq/blob/4.1.0/docs/usage.md

<!-- Generated from nf-core/scrnaseq@f7bf36d7c7e4bddc5302c3facd8d19ca83e22226. Do not edit by hand. -->
