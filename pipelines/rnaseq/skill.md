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
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/rnaseq/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | pattern |
|---|---|---|---|---|
| `sample` | string | yes |  | ^\S+$ |
| `fastq_1` | string (file path) | yes |  | ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q(\.gz)?$ |
| `fastq_2` | string (file path) | no |  | ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q(\.gz)?$ |
| `strandedness` | string | yes | forward, reverse, unstranded, auto |  |
| `seq_platform` | string | no |  | ^\S+$ |
| `seq_center` | string | no |  | ^\S+$ |
| `genome_bam` | string (file path) | no |  | ^([\S\s]*\/)?[^\s\/]+\.(bam\|BAM)$ |
| `transcriptome_bam` | string (file path) | no |  | ^([\S\s]*\/)?[^\s\/]+\.(bam\|BAM)$ |
| `percent_mapped` | number | no |  |  |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2,strandedness,seq_platform,seq_center,genome_bam,transcriptome_bam,percent_mapped
```

## Required parameters
| parameter | type | allowed values | description |
|---|---|---|---|
| `--input` | string (file path) |  | Path to the sample sheet (CSV) containing metadata about the experimental samples. |
| `--outdir` | string (directory path) |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

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
