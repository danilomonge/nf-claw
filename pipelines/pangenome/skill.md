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
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `community` (1 parameter)
- `generic_options` (15 parameters)
- `input_output_options` (5 parameters)
- `institutional_config_options` (6 parameters)
- `seqwish_options` (5 parameters)
- `smoothxg_options` (16 parameters)
- `vg_deconstruct_options` (1 parameter)
- `wfmash_options` (14 parameters)

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
