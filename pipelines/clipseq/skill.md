---
name: clipseq
pipeline: nf-core/clipseq
version: 1.0.0
commit: 45ae3c0b9b16206b687f4a645e1643c85b3f1ab4
description: CLIP analysis pipeline
has_samplesheet: false
---
# clipseq

CLIP analysis pipeline

## Run it
```bash
git submodule update --init pipelines/clipseq/upstream   # first time only
nfclaw run clipseq --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/clipseq/upstream -profile docker --outdir results
```

## Inputs
This pipeline does not use a samplesheet; configure inputs via parameters.

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string |  |  | Input FastQ files. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `adapter_and_umi_options` (4 parameters)
- `generic_options` (10 parameters)
- `input_output_options` (3 parameters)
- `institutional_config_options` (7 parameters)
- `max_job_request_options` (3 parameters)
- `motif_finding` (2 parameters)
- `peak_calling_options` (12 parameters)
- `reference_genome_options` (10 parameters)

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

## Demo
```bash
nfclaw run clipseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/clipseq/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/clipseq@45ae3c0b9b16206b687f4a645e1643c85b3f1ab4. Do not edit by hand. -->
