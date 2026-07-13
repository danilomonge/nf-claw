---
name: phyloplace
pipeline: nf-core/phyloplace
version: 2.0.1
commit: 3e37f9d7aa8d9fcca04a4d9661b8cffdb25027fa
description: Performs phylogenetic placement with EPA-NG
summary: nf-core/phyloplace is a bioinformatics best-practice analysis pipeline that performs phylogenetic placement with EPA-NG.
has_samplesheet: false
input: parameters (no samplesheet)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: HMMER, Clustal Omega, MAFFT, EPA-NG, Gappa, MultiQC
---
# phyloplace

nf-core/phyloplace is a bioinformatics best-practice analysis pipeline that performs phylogenetic placement with EPA-NG.

## Run it
```bash
git submodule update --init pipelines/phyloplace/upstream   # first time only
nfclaw run phyloplace --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/phyloplace/upstream -profile docker --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions phyloplace` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show phyloplace --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
This pipeline does not use a samplesheet; configure inputs via parameters.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `generic_options` (15 parameters)
- `input_output_options` (14 parameters)
- `institutional_config_options` (6 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/phyloplace/blob/2.0.1/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: HMMER, Clustal Omega, MAFFT, EPA-NG, Gappa, MultiQC.

Full list with references: https://github.com/nf-core/phyloplace/blob/2.0.1/CITATIONS.md

## Demo
```bash
nfclaw run phyloplace --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/phyloplace/blob/2.0.1/docs/usage.md

<!-- Generated from nf-core/phyloplace@3e37f9d7aa8d9fcca04a4d9661b8cffdb25027fa. Do not edit by hand. -->
