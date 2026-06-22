---
name: denovotranscript
pipeline: nf-core/denovotranscript
version: 1.2.1
commit: 9ab0f57785c37f77e05a03c8c327e35c63c8432b
description: A pipeline for de novo transcriptome assembly of short reads from bulk RNA-seq
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: BUSCO, Evidential Gene, fastp, FastQC, gawk, MultiQC, rnaQUAST, rnaSPAdes, Salmon, SortMeRNA, TransRate, Trinity
---
# denovotranscript

A pipeline for de novo transcriptome assembly of short reads from bulk RNA-seq

## Run it
```bash
git submodule update --init pipelines/denovotranscript/upstream   # first time only
nfclaw run denovotranscript --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/denovotranscript/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `assembly_options` (6 parameters)
- `busco_options` (4 parameters)
- `fastqc_fastp_options` (6 parameters)
- `generic_options` (13 parameters)
- `input_output_options` (5 parameters)
- `institutional_config_options` (6 parameters)
- `reference_genome_options` (3 parameters)
- `rnaquast_options` (2 parameters)
- `salmon_options` (1 parameter)
- `sortmerna_options` (3 parameters)
- `transrate_options` (1 parameter)
- `workflow_options` (2 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/denovotranscript/blob/1.2.1/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: BUSCO, Evidential Gene, fastp, FastQC, gawk, MultiQC, rnaQUAST, rnaSPAdes, Salmon, SortMeRNA, TransRate, Trinity.

Full list with references: https://github.com/nf-core/denovotranscript/blob/1.2.1/CITATIONS.md

## Demo
```bash
nfclaw run denovotranscript --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/denovotranscript/blob/1.2.1/docs/usage.md

<!-- Generated from nf-core/denovotranscript@9ab0f57785c37f77e05a03c8c327e35c63c8432b. Do not edit by hand. -->
