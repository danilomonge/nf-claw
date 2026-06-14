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
| `lane` | string | no |
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
| `--outdir` | string | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--step` | string | Starting step |
| `--ascat-alleles` | string | Path to ASCAT allele zip file. |
| `--ascat-genome` | string | ASCAT genome. |
| `--ascat-loci` | string | Path to ASCAT loci zip file. |
| `--ascat-loci-gc` | string | Path to ASCAT GC content correction file. |
| `--ascat-loci-rt` | string | Path to ASCAT RT (replictiming) correction file. |
| `--ascat-ploidy` | number | Overwrite ASCAT ploidy. |
| `--ascat-purity` | number | Overwrite ASCAT purity. |
| `--bbsplit-fasta-list` | string | Path to comma-separated file containing a list of reference genomes to filter reads against with BBSplit. You have to also explicitly set `--tools bbsplit` if you want to use BBSplit. |
| `--bbsplit-index` | string | Path to directory or tar.gz archive for pre-built BBSplit index. |
| `--bcftools-annotations` | string | A vcf file containing custom annotations to be used with bcftools annotate. Needs to be bgzipped. |
| `--bcftools-annotations-tbi` | string | Index file for `bcftools_annotations` |
| `--bcftools-columns` | string | Optional text file with list of columns to use from `bcftools_annotations`, one name per row |
| `--bcftools-header-lines` | string | Text file with the header lines of `bcftools_annotations` |
| `--build-only-index` | boolean | Only built references. |
| `--bwa` | string | Path to BWA mem indices. |
| `--bwamem2` | string | Path to bwa-mem2 mem indices. |
| `--cf-chrom-len` | string | Specify a custom chromosome length file. |
| `--cf-contamination-adjustment` | boolean | Overwrite Control-FREEC contaminationAdjustement |

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions).

## Demo
```bash
nfclaw run sarek --demo --outdir results   # uses upstream -profile test
```

## Full reference
Every parameter: [reference.md](reference.md) · upstream usage: https://github.com/nf-core/sarek/blob/3.8.1/docs/usage.md

<!-- Generated from nf-core/sarek@4bd2948f98c5bf7b785c91cf6708fffccab25467. Do not edit by hand. -->
