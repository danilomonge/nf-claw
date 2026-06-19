---
name: cageseq
pipeline: nf-core/cageseq
version: 1.0.2
commit: 838d2a5165edb86439d7ff0400bd385d6bcf6927
description: CAGE-seq pipeline
has_samplesheet: false
---
# cageseq

CAGE-seq pipeline

## Run it
```bash
git submodule update --init pipelines/cageseq/upstream   # first time only
nfclaw run cageseq --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/cageseq/upstream -profile docker --outdir results
```

## Inputs
This pipeline does not use a samplesheet; configure inputs via parameters.

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string |  |  | Input FastQ files. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `alignment_options` (2 parameters)
- `cage_tag_clustering_options` (2 parameters)
- `generic_options` (10 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)
- `process_skipping_options` (7 parameters)
- `reference_genome_options` (8 parameters)
- `ribosomal_rna_removal_options` (3 parameters)
- `trimming_options` (9 parameters)

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

## Demo
```bash
nfclaw run cageseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/cageseq/blob/1.0.2/docs/usage.md

<!-- Generated from nf-core/cageseq@838d2a5165edb86439d7ff0400bd385d6bcf6927. Do not edit by hand. -->
