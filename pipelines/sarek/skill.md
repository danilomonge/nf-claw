---
name: sarek
pipeline: nf-core/sarek
version: 3.8.1
commit: 4bd2948f98c5bf7b785c91cf6708fffccab25467
description: An open-source analysis pipeline to detect germline or somatic variants from whole genome or targeted sequencing
keywords: [sarek, nf-core, nextflow]
has_samplesheet: true
---
# sarek

An open-source analysis pipeline to detect germline or somatic variants from whole genome or targeted sequencing

## Run it
```bash
git submodule update --init pipelines/sarek/upstream   # first time only
nfclaw run sarek --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/sarek/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `patient` | string | yes |  | matches ^\S+$ |
| `sample` | string | yes |  | matches ^\S+$ |
| `sex` | string | no | XX, XY, NA |  |
| `status` | integer | no | 0, 1 |  |
| `lane` | integer or string | no |  | matches ^\S+$ |
| `fastq_1` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `spring_1` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz.spring$ |
| `spring_2` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz.spring$ |
| `table` | string (file path) | no |  | matches ^\S+\.table$ |
| `cram` | string (file path) | no |  | matches ^\S+\.cram$ |
| `crai` | string (file path) | no |  | matches ^\S+\.crai$ |
| `bam` | string (file path) | no |  | matches ^\S+\.bam$ |
| `bai` | string (file path) | no |  | matches ^\S+\.bai$ |
| `contamination` | number | no |  |  |
| `vcf` | string (file path) | no |  | matches ^\S+\.vcf(\.gz)?$ |
| `variantcaller` | string | no |  |  |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
patient,sample,sex,status,lane,fastq_1,fastq_2,spring_1,spring_2,table,cram,crai,bam,bai,contamination,vcf,variantcaller
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--step` | string | mapping, markduplicates, prepare_recalibration, recalibrate, variant_calling, annotate |  | Starting step |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
All other parameters are optional. Every one — with type, default and allowed values — is in [reference.md](reference.md), grouped as:
- `annotation` (33 parameters)
- `fastq_preprocessing` (9 parameters)
- `general_reference_genome_options` (5 parameters)
- `generic_options` (18 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (10 parameters)
- `main_options` (7 parameters)
- `post_variant_calling` (10 parameters)
- `preprocessing` (6 parameters)
- `reference_genome_options` (35 parameters)
- `umi_processing` (10 parameters)
- `variant_calling` (25 parameters)

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions).

## Demo
```bash
nfclaw run sarek --demo --outdir results   # uses upstream -profile test
```

## Full reference
Every parameter — name, type, required, allowed values, default — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/sarek/blob/3.8.1/docs/usage.md

<!-- Generated from nf-core/sarek@4bd2948f98c5bf7b785c91cf6708fffccab25467. Do not edit by hand. -->
