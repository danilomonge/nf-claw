---
name: fastquorum
pipeline: nf-core/fastquorum
version: 2.0.0
commit: 074b201d8ca6a38717da7dca58921a2cae9e21f0
description: fgbio Best Practices FASTQ to Consensus Pipeline
summary: nf-core/fastquorum is a bioinformatics pipeline that implements the pipeline implements the fgbio Best Practices FASTQ to Consensus Pipeline to produce consensus reads using unique molecular indexes/barcodes (UMIs). nf-core/fastquorum can produce consensus reads from single or multi UMI reads, and even Duplex Sequencing reads.
has_samplesheet: true
input: samplesheet (sample, library_id, lane, flowcell, fastq_1, fastq_2, fastq_3, fastq_4, read_structure, umi_file)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: Bwa, FastQC, FGBio, MultiQC, SAMtools
---
# fastquorum

nf-core/fastquorum is a bioinformatics pipeline that implements the pipeline implements the fgbio Best Practices FASTQ to Consensus Pipeline to produce consensus reads using unique molecular indexes/barcodes (UMIs). nf-core/fastquorum can produce consensus reads from single or multi UMI reads, and even Duplex Sequencing reads.

## Run it
```bash
git submodule update --init pipelines/fastquorum/upstream   # first time only
nfclaw run fastquorum --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/fastquorum/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions fastquorum` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show fastquorum --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `library_id` | string | no |  | matches ^\S+$ |
| `lane` | string or integer | no |  | matches ^[A-Za-z0-9]+$ |
| `flowcell` | string | no |  | matches ^[A-Za-z0-9]+$ |
| `fastq_1` | string (file path) | yes |  | matches ^\S+\.f(ast)?q(\.gz)?$ |
| `fastq_2` | string (file path) | no |  | matches ^\S+\.f(ast)?q(\.gz)?$ |
| `fastq_3` | string (file path) | no |  | matches ^\S+\.f(ast)?q(\.gz)?$ |
| `fastq_4` | string (file path) | no |  | matches ^\S+\.f(ast)?q(\.gz)?$ |
| `read_structure` | string | yes |  | matches ^.*$ |
| `umi_file` | string (file path) | no |  | matches ^\S+$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,library_id,lane,flowcell,fastq_1,fastq_2,fastq_3,fastq_4,read_structure,umi_file
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `consensus_calling` (2 parameters)
- `consensus_filtering` (3 parameters)
- `generic_options` (17 parameters)
- `grouping` (2 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `main_options` (2 parameters)
- `reference_genome_options` (8 parameters)
- `umi_correction` (2 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/fastquorum/blob/2.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: Bwa, FastQC, FGBio, MultiQC, SAMtools.

Full list with references: https://github.com/nf-core/fastquorum/blob/2.0.0/CITATIONS.md

## Demo
```bash
nfclaw run fastquorum --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/fastquorum/blob/2.0.0/docs/usage.md

<!-- Generated from nf-core/fastquorum@074b201d8ca6a38717da7dca58921a2cae9e21f0. Do not edit by hand. -->
