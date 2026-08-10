---
name: seqsubmit
pipeline: nf-core/seqsubmit
version: 1.0.0
commit: 717fd19e7a40099fbe5362ec48ab8ec21f62d3f8
description: Submit sequences, assemblies, MAGs, etc., to public archives
summary: nf-core/seqsubmit is a Nextflow pipeline for submitting sequence data to ENA. The pipeline currently supports the following submission modes, each routed to a dedicated workflow:
has_samplesheet: false
input: parameters (no samplesheet)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: MultiQC, CoverM, CheckM2, CAT and BAT, tRNAscan-SE 2.0, barrnap, ENA Webin-CLI, assembly_uploader, genome_uploader
---
# seqsubmit

nf-core/seqsubmit is a Nextflow pipeline for submitting sequence data to ENA. The pipeline currently supports the following submission modes, each routed to a dedicated workflow:

## Run it
```bash
git submodule update --init pipelines/seqsubmit/upstream   # first time only
nfclaw run seqsubmit --outdir results --centre-name <centre_name> --mode <mode> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/seqsubmit/upstream -profile docker --outdir results --centre-name <centre_name> --mode <mode>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions seqsubmit` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show seqsubmit --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
This pipeline does not use a samplesheet; configure inputs via parameters.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.(csv\|tsv\|yaml\|yml\|json)$ | Path to samplesheet describing the data to be submitted (supported formats: csv, tsv, yaml, yml, json). Columns/fields depend on the pipeline mode |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--centre-name` | string |  |  |  | Name of the submitter's organisation (mandatory for broker accounts). |
| `--mode` | string |  | mags, bins, metagenomic_assemblies, reads |  | Type of the data to be submitted |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Generic options** (`generic_options`) — 15 parameters
- **Evaluation options** (`genome_evaluation_options`) — 2 parameters
- **Input/output options** (`input_output_options`) — 4 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Pipeline flow control parameters** (`pipeline_options`) — 9 parameters
- **rRNA and tRNA detection options** (`rna_detection_options`) — 2 parameters
- **Assigning NCBI taxonomy with CAT_pack** (`taxonomy_assignment_options`) — 1 parameter

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run seqsubmit --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.10.4'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run seqsubmit ... --nxf-ver 25.10.4
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/seqsubmit/blob/1.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: MultiQC, CoverM, CheckM2, CAT and BAT, tRNAscan-SE 2.0, barrnap, ENA Webin-CLI, assembly_uploader, genome_uploader.

Full list with references: https://github.com/nf-core/seqsubmit/blob/1.0.0/CITATIONS.md

## Demo
```bash
nfclaw run seqsubmit --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/seqsubmit/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/seqsubmit@717fd19e7a40099fbe5362ec48ab8ec21f62d3f8. Do not edit by hand. -->
