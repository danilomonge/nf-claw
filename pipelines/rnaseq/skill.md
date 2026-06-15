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

## Required parameters
| parameter | type | allowed values | description |
|---|---|---|---|
| `--input` | string |  | Path to the sample sheet (CSV) containing metadata about the experimental samples. |
| `--outdir` | string |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
All other parameters are optional. Every one — with type, default and allowed values — is in [reference.md](reference.md), grouped as:
- `alignment_options` (21 parameters)
- `generic_options` (15 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `optional_outputs` (10 parameters)
- `process_skipping_options` (22 parameters)
- `quality_control` (9 parameters)
- `read_filtering_options` (7 parameters)
- `read_trimming_options` (4 parameters)
- `reference_genome_options` (25 parameters)
- `umi_options` (10 parameters)

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions).

## Demo
```bash
nfclaw run rnaseq --demo --outdir results   # uses upstream -profile test
```

## Full reference
Every parameter — name, type, required, allowed values, default — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/rnaseq/blob/3.26.0/docs/usage.md

<!-- Generated from nf-core/rnaseq@e7ca46272c8f9d5ceee3f71759f4ba551d3217a4. Do not edit by hand. -->
