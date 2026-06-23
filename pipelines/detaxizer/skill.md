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

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | no |  | matches ^\S+$ |
| `short_reads_fastq_1` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `short_reads_fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `long_reads_fastq_1` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,short_reads_fastq_1,short_reads_fastq_2,long_reads_fastq_1
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `bbduk` (2 parameters)
- `blastn` (4 parameters)
- `fastp_options` (6 parameters)
- `general_workflow_parameters` (11 parameters)
- `generate_samplesheet_options` (2 parameters)
- `generic_options` (16 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `kraken2` (11 parameters)
- `reference_genome_options` (4 parameters)

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
