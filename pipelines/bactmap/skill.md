---
name: bactmap
pipeline: nf-core/bactmap
version: 1.0.0
commit: 834642d8ac150ca10d705833223e7bcf15efc210
description: A mapping-based pipeline for creating a phylogeny from bacterial whole genome sequences
summary: nf-core/bactmap is a bioinformatics best-practice analysis pipeline for mapping short reads from bacterial WGS to a reference sequence, creating filtered VCF files, making pseudogenomes based on high quality positions in the VCF files and optionally creating a phylogeny from an alignment of the pseudogenomes.
has_samplesheet: false
input: parameters (no samplesheet)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions)
tools: bcftools, BWA, fastp, FastQC, FastTree2, Gubbins, IQ-TREE2, Mash, MultiQC, RapidNJ, RAxML-NG, Rasusa, samtools, SNP-sites
---
# bactmap

nf-core/bactmap is a bioinformatics best-practice analysis pipeline for mapping short reads from bacterial WGS to a reference sequence, creating filtered VCF files, making pseudogenomes based on high quality positions in the VCF files and optionally creating a phylogeny from an alignment of the pseudogenomes.

## Run it
```bash
git submodule update --init pipelines/bactmap/upstream   # first time only
nfclaw run bactmap --outdir results --reference <reference> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/bactmap/upstream -profile docker --outdir results --reference <reference>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions bactmap` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show bactmap --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
This pipeline does not use a samplesheet; configure inputs via parameters.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string |  |  |  | Path to a sample sheet describing paths to input fastq files |
| `--reference` | string |  |  |  | Path to a fasta file of the reference sequence |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Compulsory parameters** (`compulsory_parameters`) — 1 parameter
- **Generic options** (`generic_options`) — 14 parameters
- **Input/output options** (`input_output_options`) — 3 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Max job request options** (`max_job_request_options`) — 3 parameters
- **Optional pipeline steps** (`optional_pipeline_steps`) — 12 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run bactmap --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/bactmap/blob/1.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: bcftools, BWA, fastp, FastQC, FastTree2, Gubbins, IQ-TREE2, Mash, MultiQC, RapidNJ, RAxML-NG, Rasusa, samtools, SNP-sites.

Full list with references: https://github.com/nf-core/bactmap/blob/1.0.0/CITATIONS.md

## Demo
```bash
nfclaw run bactmap --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/bactmap/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/bactmap@834642d8ac150ca10d705833223e7bcf15efc210. Do not edit by hand. -->
