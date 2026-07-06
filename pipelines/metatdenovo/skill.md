---
name: metatdenovo
pipeline: nf-core/metatdenovo
version: 1.4.0
commit: 4d0307aa7d34575aa7891a7b4996ffe19e774cd9
description: Assembly and annotation of metatranscriptomic data, both prokaryotic and eukaryotic
summary: nf-core/metatdenovo is a bioinformatics best-practice analysis pipeline for assembly and annotation of metatranscriptomic and metagenomic data from prokaryotes, eukaryotes or viruses.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, MultiQC, Trim Galore!, khmer, Seqtk, RNAspade, Megahit, TransDecoder, Prokka, Prodigal, BBmap, FeatureCounts, Eggnog, Kofamscan, HMMsearch, EUKulele, Diamond, TaxonKit, CAT, transrate
---
# metatdenovo

nf-core/metatdenovo is a bioinformatics best-practice analysis pipeline for assembly and annotation of metatranscriptomic and metagenomic data from prokaryotes, eukaryotes or viruses.

## Run it
```bash
git submodule update --init pipelines/metatdenovo/upstream   # first time only
nfclaw run metatdenovo --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/metatdenovo/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions metatdenovo` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show metatdenovo --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q(\.gz)?$ |
| `fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q(\.gz)?$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `assembler_options` (6 parameters)
- `bbduk_options` (2 parameters)
- `digital_normalization_options` (4 parameters)
- `functional_annotation_options` (7 parameters)
- `generic_options` (15 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `mapping_options` (3 parameters)
- `orf_caller_options` (6 parameters)
- `quality_control_options` (2 parameters)
- `taxonomy_annotation_options` (6 parameters)
- `trimming_options` (7 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/metatdenovo/blob/1.4.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, MultiQC, Trim Galore!, khmer, Seqtk, RNAspade, Megahit, TransDecoder, Prokka, Prodigal, BBmap, FeatureCounts, Eggnog, Kofamscan, HMMsearch, EUKulele, Diamond, TaxonKit, CAT, transrate.

Full list with references: https://github.com/nf-core/metatdenovo/blob/1.4.0/CITATIONS.md

## Demo
```bash
nfclaw run metatdenovo --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/metatdenovo/blob/1.4.0/docs/usage.md

<!-- Generated from nf-core/metatdenovo@4d0307aa7d34575aa7891a7b4996ffe19e774cd9. Do not edit by hand. -->
