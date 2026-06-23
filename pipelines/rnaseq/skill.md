---
name: rnaseq
pipeline: nf-core/rnaseq
version: 3.26.0
commit: e7ca46272c8f9d5ceee3f71759f4ba551d3217a4
description: RNA sequencing analysis pipeline for gene/isoform quantification and extensive quality control.
summary: nf-core/rnaseq is a bioinformatics pipeline that can be used to analyse RNA sequencing data obtained from organisms with a reference genome and annotation. It takes a samplesheet with FASTQ files or pre-aligned BAM files as input, performs quality control (QC), trimming and (pseudo-)alignment, and produces a gene expression matrix and extensive QC report.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2, strandedness, seq_platform, seq_center, genome_bam, transcriptome_bam, percent_mapped)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: BBMap, BEDTools, Bowtie2, Bracken, fastp, FastQC, featureCounts, fq, GffRead, HISAT2, Kallisto, Kraken2, MultiQC, picard-tools, preseq, Qualimap 2, RiboDetector, RSEM, RustQC, RSeQC, Salmon, SeqKit, SAMtools, SortMeRNA, STAR, StringTie2, Sylph, Trim Galore!, tximport, UCSC tools, UMI-tools, UMICollapse, R, DESeq2, dupRadar, ggplot2, optparse, pheatmap, RColorBrewer, SummarizedExperiment, Tximeta
---
# rnaseq

nf-core/rnaseq is a bioinformatics pipeline that can be used to analyse RNA sequencing data obtained from organisms with a reference genome and annotation. It takes a samplesheet with FASTQ files or pre-aligned BAM files as input, performs quality control (QC), trimming and (pseudo-)alignment, and produces a gene expression matrix and extensive QC report.

## Run it
```bash
git submodule update --init pipelines/rnaseq/upstream   # first time only
nfclaw run rnaseq --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/rnaseq/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q(\.gz)?$ |
| `fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q(\.gz)?$ |
| `strandedness` | string | yes | forward, reverse, unstranded, auto |  |
| `seq_platform` | string | no |  | matches ^\S+$ |
| `seq_center` | string | no |  | matches ^\S+$ |
| `genome_bam` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.(bam\|BAM)$ |
| `transcriptome_bam` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.(bam\|BAM)$ |
| `percent_mapped` | number | no |  | ≥ 0; ≤ 100 |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2,strandedness,seq_platform,seq_center,genome_bam,transcriptome_bam,percent_mapped
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to the sample sheet (CSV) containing metadata about the experimental samples. |
| `--outdir` | string (directory path) |  | length ≥ 1 | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
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
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/rnaseq/blob/3.26.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: BBMap, BEDTools, Bowtie2, Bracken, fastp, FastQC, featureCounts, fq, GffRead, HISAT2, Kallisto, Kraken2, MultiQC, picard-tools, preseq, Qualimap 2, RiboDetector, RSEM, RustQC, RSeQC, Salmon, SeqKit, SAMtools, SortMeRNA, STAR, StringTie2, Sylph, Trim Galore!, tximport, UCSC tools, UMI-tools, UMICollapse, R, DESeq2, dupRadar, ggplot2, optparse, pheatmap, RColorBrewer, SummarizedExperiment, Tximeta.

Full list with references: https://github.com/nf-core/rnaseq/blob/3.26.0/CITATIONS.md

## Demo
```bash
nfclaw run rnaseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/rnaseq/blob/3.26.0/docs/usage.md

<!-- Generated from nf-core/rnaseq@e7ca46272c8f9d5ceee3f71759f4ba551d3217a4. Do not edit by hand. -->
