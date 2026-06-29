---
name: magmap
pipeline: nf-core/magmap
version: 1.1.0
commit: 5cb04769826f54752613b36c6d75d00eae126146
description: nf-core/magmap is a bioinformatics best-practice analysis pipeline for mapping reads to a (large) collections of genomes.
summary: nf-core/magmap is a bioinformatics best-practice analysis pipeline that maps reads to (large) collections of genomes. Its main output are tables with quantification of features (genes) in genomes which can be analyzed in R, Python or by other pipelines such as nf-core/differentialabundance. It is mainly meant for metatranscriptomes and metagenomes, but can be used for other types of samples where mapping to contigs is relevant. The nf-core/rnaseq pipeline is similar in purpose, but meant for single organisms with reference genomes and annotations, in practice eukaryotic model organisms.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, Trim Galore!, sourmash, Prokka, BBmap, samtools, gtdbtk, checkm, FeatureCounts, R, Tidyverse, data.table, MultiQC
---
# magmap

nf-core/magmap is a bioinformatics best-practice analysis pipeline that maps reads to (large) collections of genomes. Its main output are tables with quantification of features (genes) in genomes which can be analyzed in R, Python or by other pipelines such as nf-core/differentialabundance. It is mainly meant for metatranscriptomes and metagenomes, but can be used for other types of samples where mapping to contigs is relevant. The nf-core/rnaseq pipeline is similar in purpose, but meant for single organisms with reference genomes and annotations, in practice eukaryotic model organisms.

## Run it
```bash
git submodule update --init pipelines/magmap/upstream   # first time only
nfclaw run magmap --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/magmap/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions magmap` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show magmap --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.(csv\|tsv\|yaml\|yml\|json)$ | Path to a file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `featurecounts_option` (2 parameters)
- `generic_options` (15 parameters)
- `input_output_options` (12 parameters)
- `institutional_config_options` (6 parameters)
- `mapping_options` (6 parameters)
- `quality_control_options` (2 parameters)
- `sourmash_options` (4 parameters)
- `trimming_options` (7 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/magmap/blob/1.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, Trim Galore!, sourmash, Prokka, BBmap, samtools, gtdbtk, checkm, FeatureCounts, R, Tidyverse, data.table, MultiQC.

Full list with references: https://github.com/nf-core/magmap/blob/1.1.0/CITATIONS.md

## Demo
```bash
nfclaw run magmap --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/magmap/blob/1.1.0/docs/usage.md

<!-- Generated from nf-core/magmap@5cb04769826f54752613b36c6d75d00eae126146. Do not edit by hand. -->
