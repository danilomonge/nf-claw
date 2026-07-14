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

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions rnaseq` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show rnaseq --pipeline-version X.Y.Z` prints that release's docs).

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

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,strandedness
```

Any of the optional columns above may be appended to the header when your data needs them: `fastq_2`, `seq_platform`, `seq_center`, `genome_bam`, `transcriptome_bam`, `percent_mapped`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to the sample sheet (CSV) containing metadata about the experimental samples. |
| `--outdir` | string (directory path) |  |  | length ≥ 1 | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Reference genome
No reference genome is set by default: supply your own (the `reference_genome_options` group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`). Passing `--genome <id>` instead resolves the references from AWS iGenomes at `s3://ngi-igenomes/igenomes/`, which needs access to that bucket and downloads them. Set `--igenomes-ignore true` to disable the lookup entirely.

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Alignment options** (`alignment_options`) — 21 parameters
- **Generic options** (`generic_options`) — 15 parameters
- **Input/output options** (`input_output_options`) — 4 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Optional outputs** (`optional_outputs`) — 10 parameters
- **Process skipping options** (`process_skipping_options`) — 22 parameters
- **Quality Control** (`quality_control`) — 9 parameters
- **Read filtering options** (`read_filtering_options`) — 7 parameters
- **Read trimming options** (`read_trimming_options`) — 4 parameters
- **Reference genome options** (`reference_genome_options`) — 25 parameters
- **UMI options** (`umi_options`) — 10 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run rnaseq --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.04.3'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run rnaseq ... --nxf-ver 25.04.3
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

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
