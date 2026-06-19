---
name: bactmap
pipeline: nf-core/bactmap
version: 1.0.0
commit: 834642d8ac150ca10d705833223e7bcf15efc210
description: A mapping-based pipeline for creating a phylogeny from bacterial whole genome sequences
has_samplesheet: false
---
# bactmap

A mapping-based pipeline for creating a phylogeny from bacterial whole genome sequences

## Run it
```bash
git submodule update --init pipelines/bactmap/upstream   # first time only
nfclaw run bactmap --outdir results --reference <reference> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/bactmap/upstream -profile docker --outdir results --reference <reference>
```

## Inputs
This pipeline does not use a samplesheet; configure inputs via parameters.

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string |  |  | Path to a sample sheet describing paths to input fastq files |
| `--reference` | string |  |  | Path to a fasta file of the reference sequence |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `compulsory_parameters` (1 parameter)
- `generic_options` (14 parameters)
- `input_output_options` (3 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)
- `optional_pipeline_steps` (12 parameters)

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

## Demo
```bash
nfclaw run bactmap --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/bactmap/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/bactmap@834642d8ac150ca10d705833223e7bcf15efc210. Do not edit by hand. -->
