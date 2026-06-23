---
name: cutandrun
pipeline: nf-core/cutandrun
version: 3.2.2
commit: 6e1125d4fee4ea7c8b70ed836bb0e92a89e3305f
description: Analysis pipeline for CUT&RUN and CUT&TAG experiments that includes sequencing QC, spike-in normalisation, IgG control normalisation, peak calling and downstream peak analysis.
summary: nf-core/cutandrun is a best-practice bioinformatic analysis pipeline for CUT&RUN, CUT&Tag, and TIPseq experimental protocols that were developed to study protein-DNA interactions and epigenomic profiling.
has_samplesheet: true
input: samplesheet (group, replicate, fastq_1, fastq_2, control)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, MultiQC, bedtools, samtools, bowtie2, deeptools, seacr, macs2, picard
---
# cutandrun

nf-core/cutandrun is a best-practice bioinformatic analysis pipeline for CUT&RUN, CUT&Tag, and TIPseq experimental protocols that were developed to study protein-DNA interactions and epigenomic profiling.

## Run it
```bash
git submodule update --init pipelines/cutandrun/upstream   # first time only
nfclaw run cutandrun --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/cutandrun/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `group` | string | yes |  | matches ^\S+$ |
| `replicate` | integer | yes |  | matches ^[0-9]*$ |
| `fastq_1` | string | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `control` | string | yes |  | matches ^\S+$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
group,replicate,fastq_1,fastq_2,control
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to store on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `flow_switching_options` (16 parameters)
- `generic_options` (16 parameters)
- `input_output_options` (11 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)
- `pipeline_options` (25 parameters)
- `reference_data_options` (10 parameters)
- `reporting_options` (11 parameters)
- `trimming_options` (5 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/cutandrun/blob/3.2.2/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, MultiQC, bedtools, samtools, bowtie2, deeptools, seacr, macs2, picard.

Full list with references: https://github.com/nf-core/cutandrun/blob/3.2.2/CITATIONS.md

## Demo
```bash
nfclaw run cutandrun --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/cutandrun/blob/3.2.2/docs/usage.md

<!-- Generated from nf-core/cutandrun@6e1125d4fee4ea7c8b70ed836bb0e92a89e3305f. Do not edit by hand. -->
