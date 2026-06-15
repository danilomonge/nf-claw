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

## Key parameters
| parameter | type | description |
|---|---|---|
| `--step` | string | Starting step |
| `--outdir` | string | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--input` | string | Path to comma-separated file containing information about the samples in the experiment. |
| `--intervals` | string | Path to target bed file in case of whole exome or targeted sequencing or intervals file. |
| `--no-intervals` | boolean | Disable usage of intervals. |
| `--wes` | boolean | Enable when exome or panel data is provided. |
| `--tools` | string | Tools to use for contamination removal, duplicate marking, variant calling and/or for annotation. |
| `--skip-tools` | string | Disable specified tools. |
| `--trim-fastq` | boolean | Run FastP for read trimming |
| `--trim-nextseq` | boolean | Removing poly-G tails. |
| `--save-trimmed` | boolean | Save trimmed FastQ file intermediates. |
| `--save-split-fastqs` | boolean | If set, publishes split FASTQ files. Intended for testing purposes. |
| `--umi-read-structure` | string | Specify UMI read structure for fgbio UMI consensus read generation |
| `--umi-in-read-header` | boolean | Move UMIs from fastq read headers to a tag prior to deduplication. |
| `--umi-location` | string | Location of the UMI(s) to be extracted with fastp. |
| `--umi-length` | integer | Length of the UMI(s) in the read. |
| `--umi-base-skip` | integer | Number of bases to skip after the UMI(s) in the read when extracting with fastp. |
| `--umi-tag` | string | Tag detailing where UMIs are present inside the bam/cram file (e.g. RX). |
| `--bbsplit-fasta-list` | string | Path to comma-separated file containing a list of reference genomes to filter reads against with BBSplit. You have to also explicitly set `--tools bbsplit` if you want to use BBSplit. |
| `--bbsplit-index` | string | Path to directory or tar.gz archive for pre-built BBSplit index. |

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions).

## Demo
```bash
nfclaw run sarek --demo --outdir results   # uses upstream -profile test
```

## Full reference
Every parameter: [reference.md](reference.md) · upstream usage: https://github.com/nf-core/sarek/blob/3.8.1/docs/usage.md

<!-- Generated from nf-core/sarek@4bd2948f98c5bf7b785c91cf6708fffccab25467. Do not edit by hand. -->
