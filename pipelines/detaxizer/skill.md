---
name: detaxizer
pipeline: nf-core/detaxizer
version: 1.3.0
commit: 3586921aa3a4c49271f1b2082309bdc33c819749
description: A pipeline to identify (and remove) certain sequences from raw genomic data. Default taxon to identify (and remove) is Homo sapiens. Removal is optional.
summary: nf-core/detaxizer is a bioinformatics pipeline that checks for the presence of a specific taxon in (meta)genomic fastq files and to filter out this taxon or taxonomic subtree. The process begins with quality assessment via FastQC and optional preprocessing (adapter trimming, quality cutting and optional length and quality filtering) using fastp, followed by taxonomic classification with kraken2 and/or bbduk, and optionally employs blastn for validation of the reads associated with the identified taxa. Users must provide a samplesheet to indicate the fastq files and, if utilizing bbduk in the classification and/or the validation step, fasta files for usage of bbduk and creating the blastn database to verify the targeted taxon.
has_samplesheet: true
input: samplesheet (sample, short_reads_fastq_1, short_reads_fastq_2, long_reads_fastq_1)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: bbmap, blastn, fastp, FastQC, Kraken2, MultiQC, seqkit, dnaio, Python, biopython
---
# detaxizer

nf-core/detaxizer is a bioinformatics pipeline that checks for the presence of a specific taxon in (meta)genomic fastq files and to filter out this taxon or taxonomic subtree. The process begins with quality assessment via FastQC and optional preprocessing (adapter trimming, quality cutting and optional length and quality filtering) using fastp, followed by taxonomic classification with kraken2 and/or bbduk, and optionally employs blastn for validation of the reads associated with the identified taxa. Users must provide a samplesheet to indicate the fastq files and, if utilizing bbduk in the classification and/or the validation step, fasta files for usage of bbduk and creating the blastn database to verify the targeted taxon.

## Run it
```bash
git submodule update --init pipelines/detaxizer/upstream   # first time only
nfclaw run detaxizer --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/detaxizer/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions detaxizer` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show detaxizer --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | no |  | matches ^\S+$ |
| `short_reads_fastq_1` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `short_reads_fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `long_reads_fastq_1` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,short_reads_fastq_1,short_reads_fastq_2,long_reads_fastq_1
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Reference genome
**This release resolves a reference genome remotely by default.** `--genome` defaults to `GRCh38`, which is looked up in AWS iGenomes at `s3://ngi-igenomes/igenomes/`. A run that passes no reference of its own therefore reads its references over S3 — that fails on a host without access to the bucket, and downloads tens of gigabytes on one that has it. For a self-contained run, pass your own reference instead (the `reference_genome_options` group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`). Set `--igenomes-ignore true` to disable the lookup entirely.

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **bbduk** (`bbduk`) — 2 parameters
- **blastn** (`blastn`) — 4 parameters
- **fastp options** (`fastp_options`) — 6 parameters
- **General workflow parameters** (`general_workflow_parameters`) — 11 parameters
- **Downstream pipeline samplesheet generation options** (`generate_samplesheet_options`) — 2 parameters
- **Generic options** (`generic_options`) — 16 parameters
- **Input/output options** (`input_output_options`) — 4 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **kraken2** (`kraken2`) — 11 parameters
- **Reference genome options** (`reference_genome_options`) — 4 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run detaxizer --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.04.8'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run detaxizer ... --nxf-ver 25.04.8
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/detaxizer/blob/1.3.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: bbmap, blastn, fastp, FastQC, Kraken2, MultiQC, seqkit, dnaio, Python, biopython.

Full list with references: https://github.com/nf-core/detaxizer/blob/1.3.0/CITATIONS.md

## Demo
```bash
nfclaw run detaxizer --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/detaxizer/blob/1.3.0/docs/usage.md

<!-- Generated from nf-core/detaxizer@3586921aa3a4c49271f1b2082309bdc33c819749. Do not edit by hand. -->
