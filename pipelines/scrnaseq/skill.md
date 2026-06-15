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
# raw equivalent:
nextflow run pipelines/scrnaseq/upstream -r 4.1.0 -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required |
|---|---|---|
| `sample` | string | yes |
| `fastq_1` | string | yes |
| `fastq_2` | string | yes |
| `fastq_barcode` | string | no |
| `expected_cells` | integer | no |
| `seq_center` | string | no |
| `sample_type` | string | no |
| `feature_type` | string | no |

Example `samplesheet.csv`:
```csv
sample,fastq_1,fastq_2,fastq_barcode,expected_cells,seq_center,sample_type,feature_type
sample1,data/sample1_fastq_1.gz,data/sample1_fastq_2.gz,value,value,value,value,value
```

## Key parameters
| parameter | type | description |
|---|---|---|
| `--input` | string | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--email` | string | Email address for completion summary. |
| `--multiqc-title` | string | MultiQC report title. Printed as page header, used for filename if not otherwise specified. |
| `--barcode-whitelist` | string | If not using the 10X Genomics platform, a custom barcode whitelist can be used with `--barcode_whitelist`. |
| `--skip-multiqc` | boolean | Skip MultiQC Report |
| `--skip-fastqc` | boolean | Skip FastQC |
| `--skip-cellbender` | boolean | Skip cellbender empty drops filter subworkflow |
| `--skip-emptydrops` | boolean |  |
| `--genome` | string | Name of iGenomes reference. |
| `--fasta` | string | Path to FASTA genome file. |
| `--transcript-fasta` | string | A cDNA FASTA file |
| `--gtf` | string | Reference GTF annotation file |
| `--save-reference` | boolean | Specify this parameter to save the indices created (STAR, Kallisto, Simpleaf) to the results. |
| `--save-align-intermeds` | boolean | Specify this parameter to save the intermediate alignment files (STAR, CellRanger) to the results. |
| `--txp2gene` | string | Path to transcript to gene mapping file. This allows the specification of a transcript to gene mapping file for Kallisto/BUS and Alevin-fry with AlevinQC. |
| `--simpleaf-index` | string | Path to pre-built Simpleaf index. |
| `--star-index` | string | Specify a path to the precomputed STAR index. |
| `--star-ignore-sjdbgtf` | string | Ignore the SJDB GTF file. |
| `--seq-center` | string | Name of sequencing center for BAM read group tag. |

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions).

## Demo
```bash
nfclaw run scrnaseq --demo --outdir results   # uses upstream -profile test
```

## Full reference
Every parameter: [reference.md](reference.md) · upstream usage: https://github.com/nf-core/scrnaseq/blob/4.1.0/docs/usage.md

<!-- Generated from nf-core/scrnaseq@f7bf36d7c7e4bddc5302c3facd8d19ca83e22226. Do not edit by hand. -->
