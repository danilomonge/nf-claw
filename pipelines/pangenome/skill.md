---
name: pangenome
pipeline: nf-core/pangenome
version: 1.1.3
commit: 3d02bd1df79f48b4bfdb4ad95d4ca0d7f6aeb337
description: The pangenome graph construction pipeline renders a collection of sequences into a pangenome graph. Its goal is to build a graph that is locally directed and acyclic while preserving large-scale variation. Maintaining local linearity is important for interpretation, visualization, mapping, comparative genomics, and reuse of pangenome graphs
summary: nf-core/pangenome is a bioinformatics best-practice analysis pipeline for pangenome graph construction. The pipeline renders a collection of sequences into a pangenome graph. Its goal is to build a graph that is locally directed and acyclic while preserving large-scale variation. Maintaining local linearity is important for interpretation, visualization, mapping, comparative genomics, and reuse of pangenome graphs.
has_samplesheet: false
input: parameters (no samplesheet)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: GFAFFIX, MultiQC, NET2COMMUNITIES, ODGI, PGGB, SAMTOOLS, SEQWISH, SMOOTHXG, VCFLIB, VG, WFMASH
---
# pangenome

nf-core/pangenome is a bioinformatics best-practice analysis pipeline for pangenome graph construction. The pipeline renders a collection of sequences into a pangenome graph. Its goal is to build a graph that is locally directed and acyclic while preserving large-scale variation. Maintaining local linearity is important for interpretation, visualization, mapping, comparative genomics, and reuse of pangenome graphs.

## Run it
```bash
git submodule update --init pipelines/pangenome/upstream   # first time only
nfclaw run pangenome --outdir results --n-haplotypes <n_haplotypes> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/pangenome/upstream -profile docker --outdir results --n-haplotypes <n_haplotypes>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions pangenome` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show pangenome --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
This pipeline does not use a samplesheet; configure inputs via parameters.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.fn?a(sta)?(\.gz)?$ | Path to BGZIPPED input FASTA to build the pangenome graph from. |
| `--n-haplotypes` | number |  |  |  | The number of haplotypes in the input FASTA. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Community** (`community`) — 1 parameter
- **Generic options** (`generic_options`) — 15 parameters
- **Input/output options** (`input_output_options`) — 5 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Seqwish Options** (`seqwish_options`) — 5 parameters
- **Smoothxg options** (`smoothxg_options`) — 16 parameters
- **Vg Deconstruct Options** (`vg_deconstruct_options`) — 1 parameter
- **Wfmash Options** (`wfmash_options`) — 14 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run pangenome --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=24.04.2'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run pangenome ... --nxf-ver 24.04.2
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/pangenome/blob/1.1.3/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: GFAFFIX, MultiQC, NET2COMMUNITIES, ODGI, PGGB, SAMTOOLS, SEQWISH, SMOOTHXG, VCFLIB, VG, WFMASH.

Full list with references: https://github.com/nf-core/pangenome/blob/1.1.3/CITATIONS.md

## Demo
```bash
nfclaw run pangenome --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/pangenome/blob/1.1.3/docs/usage.md

<!-- Generated from nf-core/pangenome@3d02bd1df79f48b4bfdb4ad95d4ca0d7f6aeb337. Do not edit by hand. -->
