---
name: proteinannotator
pipeline: nf-core/proteinannotator
version: 1.1.0
commit: cbf78d471f62d91af666e8c77bcd580b4743c6be
description: Generation of sequence-level annotations for amino acid sequences
summary: nf-core/proteinannotator is a bioinformatics pipeline that computes statistics for protein FASTA inputs and produces protein annotations based on predicted sequence features, including conserved domains, functions, and secondary structure.
has_samplesheet: true
input: samplesheet (id, fasta)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: SeqFu, SeqKit, hmmer, InterProScan, s4pred, MultiQC
---
# proteinannotator

nf-core/proteinannotator is a bioinformatics pipeline that computes statistics for protein FASTA inputs and produces protein annotations based on predicted sequence features, including conserved domains, functions, and secondary structure.

## Run it
```bash
git submodule update --init pipelines/proteinannotator/upstream   # first time only
nfclaw run proteinannotator --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/proteinannotator/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions proteinannotator` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show proteinannotator --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `id` | string | yes |  | matches ^\S+$ |
| `fasta` | string (file path) | yes |  | matches ^([\S\s]*\/)?[^\s\/]+\.(fa\|fasta\|faa\|fas)(\.gz)?$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
id,fasta
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `domain_annotation_params` (13 parameters)
- `functional_annotation_options` (5 parameters)
- `generic_options` (16 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `prediction_params` (2 parameters)
- `quality_check_params` (4 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/proteinannotator/blob/1.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: SeqFu, SeqKit, hmmer, InterProScan, s4pred, MultiQC.

Full list with references: https://github.com/nf-core/proteinannotator/blob/1.1.0/CITATIONS.md

## Demo
```bash
nfclaw run proteinannotator --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/proteinannotator/blob/1.1.0/docs/usage.md

<!-- Generated from nf-core/proteinannotator@cbf78d471f62d91af666e8c77bcd580b4743c6be. Do not edit by hand. -->
