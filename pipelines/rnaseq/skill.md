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
| `--additional-fasta` | string | FASTA file to concatenate to genome FASTA file e.g. containing spike-in sequences. |
| `--arm` | boolean | Use ARM architecture containers. |
| `--bam-csi-index` | boolean | Create a CSI index for BAM files instead of the traditional BAI index. This will be required for genomes with larger chromosome sizes. |
| `--bbsplit-fasta-list` | string | Path to comma-separated file containing a list of reference genomes to filter reads against with BBSplit. You have to also explicitly set `--skip_bbsplit false` if you want to use BBSplit. |
| `--bbsplit-index` | string | Path to directory or tar.gz archive for pre-built BBSplit index. |
| `--bowtie2-index` | string | Path to directory or tar.gz archive for pre-built Bowtie2 index. |
| `--config-profile-contact` | string | Institutional config contact information. |
| `--config-profile-description` | string | Institutional config description. |
| `--config-profile-name` | string | Institutional config name. |
| `--config-profile-url` | string | Institutional config URL link. |
| `--contaminant-screening` | string | Tool to use for detecting contaminants in the selected screening reads - available options are 'sylph', 'kraken2', or 'kraken2_bracken' |
| `--email` | string | Email address for completion summary. |
| `--email-on-fail` | string | Email address for completion summary, only when pipeline fails. |
| `--extra-bowtie2-align-args` | string | Extra arguments to pass to Bowtie2 alignment command in addition to defaults defined by the pipeline. Only available when using --aligner bowtie2_salmon. |
| `--extra-fastp-args` | string | Extra arguments to pass to fastp command in addition to defaults defined by the pipeline. |
| `--extra-kallisto-quant-args` | string | Extra arguments to pass to Kallisto quant command in addition to defaults defined by the pipeline. |
| `--extra-salmon-quant-args` | string | Extra arguments to pass to Salmon quant command in addition to defaults defined by the pipeline. |
| `--extra-star-align-args` | string | Extra arguments to pass to STAR alignment command in addition to defaults defined by the pipeline. Only available for the STAR-Salmon route. |

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions).

## Demo
```bash
nfclaw run rnaseq --demo --outdir results   # uses upstream -profile test
```

## Full reference
Every parameter: [reference.md](reference.md) · upstream usage: https://github.com/nf-core/rnaseq/blob/3.26.0/docs/usage.md

<!-- Generated from nf-core/rnaseq@e7ca46272c8f9d5ceee3f71759f4ba551d3217a4. Do not edit by hand. -->
