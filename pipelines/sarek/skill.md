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
# raw equivalent:
nextflow run pipelines/sarek/upstream -r 3.8.1 -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required |
|---|---|---|
| `patient` | string | yes |
| `sample` | string | yes |
| `sex` | string | no |
| `status` | integer | no |
| `lane` | integer or string | no |
| `fastq_1` | string | no |
| `fastq_2` | string | no |
| `spring_1` | string | no |
| `spring_2` | string | no |
| `table` | string | no |
| `cram` | string | no |
| `crai` | string | no |
| `bam` | string | no |
| `bai` | string | no |
| `contamination` | number | no |
| `vcf` | string | no |
| `variantcaller` | string | no |

Example `samplesheet.csv`:
```csv
patient,sample,sex,status,lane,fastq_1,fastq_2,spring_1,spring_2,table,cram,crai,bam,bai,contamination,vcf,variantcaller
value,sample1,value,value,value,data/sample1_fastq_1.gz,data/sample1_fastq_2.gz,data/sample1_spring_1.gz,data/sample1_spring_2.gz,data/sample1_table.gz,data/sample1_cram.gz,data/sample1_crai.gz,data/sample1_bam.gz,data/sample1_bai.gz,value,data/sample1_vcf.gz,value
```

## Required parameters
| parameter | type | allowed values | description |
|---|---|---|---|
| `--step` | string | mapping, markduplicates, prepare_recalibration, recalibrate, variant_calling, annotate | Starting step |
| `--outdir` | string |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

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
