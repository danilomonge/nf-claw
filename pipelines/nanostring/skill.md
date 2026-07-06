---
name: nanostring
pipeline: nf-core/nanostring
version: 1.3.3
commit: 6f0b2d537a1f06e8fe1d6c63d7c409009141aa62
description: Nanostring nCounter analysis pipeline
summary: nf-core/nanostring is a bioinformatics pipeline that can be used to analyze NanoString data. The performed analysis steps include quality control and data normalization.
has_samplesheet: true
input: samplesheet (SAMPLE_ID, RCC_FILE, RCC_FILE_NAME, TIME, TREATMENT, INCLUDE, OTHER_METADATA)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: MultiQC, NACHO, GSVA, SINGSCORE, PLAGE, SSGSEA, SAMS
---
# nanostring

nf-core/nanostring is a bioinformatics pipeline that can be used to analyze NanoString data. The performed analysis steps include quality control and data normalization.

## Run it
```bash
git submodule update --init pipelines/nanostring/upstream   # first time only
nfclaw run nanostring --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/nanostring/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions nanostring` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show nanostring --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `SAMPLE_ID` | string | yes |  | matches ^\S+$ |
| `RCC_FILE` | string (file path) | yes |  | matches ^\S+\.RCC$ |
| `RCC_FILE_NAME` | string | yes |  | matches ^\S+\.RCC$ |
| `TIME` | string or integer | no |  |  |
| `TREATMENT` | string or integer | no |  |  |
| `INCLUDE` | integer | no | 0, 1 |  |
| `OTHER_METADATA` | string | no |  |  |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
SAMPLE_ID,RCC_FILE,RCC_FILE_NAME,TIME,TREATMENT,INCLUDE,OTHER_METADATA
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `gene_score_computation` (2 parameters)
- `generic_options` (18 parameters)
- `input_output_options` (2 parameters)
- `institutional_config_options` (6 parameters)
- `normalization_parameters` (1 parameter)
- `processing_options` (2 parameters)
- `reference_genome_options` (3 parameters)
- `skipping_options` (1 parameter)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/nanostring/blob/1.3.3/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: MultiQC, NACHO, GSVA, SINGSCORE, PLAGE, SSGSEA, SAMS.

Full list with references: https://github.com/nf-core/nanostring/blob/1.3.3/CITATIONS.md

## Demo
```bash
nfclaw run nanostring --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/nanostring/blob/1.3.3/docs/usage.md

<!-- Generated from nf-core/nanostring@6f0b2d537a1f06e8fe1d6c63d7c409009141aa62. Do not edit by hand. -->
