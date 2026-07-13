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
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Generic options** (`generic_options`) — 15 parameters
- **Input/output options** (`input_output_options`) — 14 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run phyloplace --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

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
