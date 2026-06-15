---
name: rnaseq
pipeline: nf-core/rnaseq
version: 3.26.0
commit: e7ca46272c8f9d5ceee3f71759f4ba551d3217a4
description: RNA sequencing analysis pipeline for gene/isoform quantification and extensive quality control.
keywords: [rnaseq, nf-core, nextflow]
has_samplesheet: true
---
# rnaseq

RNA sequencing analysis pipeline for gene/isoform quantification and extensive quality control.

## Run it
```bash
git submodule update --init pipelines/rnaseq/upstream   # first time only
nfclaw run rnaseq --input samplesheet.csv --outdir results -profile docker
# raw equivalent:
nextflow run pipelines/rnaseq/upstream -r 3.26.0 -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required |
|---|---|---|
| `sample` | string | yes |
| `fastq_1` | string | yes |
| `fastq_2` | string | no |
| `strandedness` | string | yes |
| `seq_platform` | string | no |
| `seq_center` | string | no |
| `genome_bam` | string | no |
| `transcriptome_bam` | string | no |
| `percent_mapped` | number | no |

Example `samplesheet.csv`:
```csv
sample,fastq_1,fastq_2,strandedness,seq_platform,seq_center,genome_bam,transcriptome_bam,percent_mapped
sample1,data/sample1_fastq_1.gz,data/sample1_fastq_2.gz,value,value,value,data/sample1_genome_bam.gz,data/sample1_transcriptome_bam.gz,value
```

## Key parameters
| parameter | type | description |
|---|---|---|
| `--input` | string | Path to the sample sheet (CSV) containing metadata about the experimental samples. |
| `--outdir` | string | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--email` | string | Email address for completion summary. |
| `--multiqc-title` | string | MultiQC report title. Printed as page header, used for filename if not otherwise specified. |
| `--genome` | string | Name of a `params.genomes` catalogue entry (iGenomes or a user-defined catalogue). |
| `--fasta` | string | Path to FASTA genome file. |
| `--gtf` | string | Path to GTF annotation file. |
| `--gff` | string | Path to GFF3 annotation file. |
| `--gene-bed` | string | Path to BED file containing gene intervals. This will be created from the GTF file if not specified. |
| `--transcript-fasta` | string | Path to FASTA transcriptome file. |
| `--additional-fasta` | string | FASTA file to concatenate to genome FASTA file e.g. containing spike-in sequences. |
| `--splicesites` | string | Splice sites file required for HISAT2. |
| `--star-index` | string | Path to directory or tar.gz archive for pre-built STAR index. |
| `--hisat2-index` | string | Path to directory or tar.gz archive for pre-built HISAT2 index. |
| `--rsem-index` | string | Path to directory or tar.gz archive for pre-built RSEM index. |
| `--salmon-index` | string | Path to directory or tar.gz archive for pre-built Salmon index. |
| `--kallisto-index` | string | Path to directory or tar.gz archive for pre-built Kallisto index. |
| `--bowtie2-index` | string | Path to directory or tar.gz archive for pre-built Bowtie2 index. |
| `--gencode` | boolean | Specify if your GTF annotation is in GENCODE format. |
| `--gffread-transcript-fasta` | boolean | Use gffread to generate transcript FASTA instead of RSEM. |

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions).

## Demo
```bash
nfclaw run rnaseq --demo --outdir results   # uses upstream -profile test
```

## Full reference
Every parameter: [reference.md](reference.md) · upstream usage: https://github.com/nf-core/rnaseq/blob/3.26.0/docs/usage.md

<!-- Generated from nf-core/rnaseq@e7ca46272c8f9d5ceee3f71759f4ba551d3217a4. Do not edit by hand. -->
