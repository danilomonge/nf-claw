---
name: createpanelrefs
pipeline: nf-core/createpanelrefs
version: 1.0.0
commit: 8ce86a84b5af74facf99abb76216531622b52bc8
description: Generate Panel of Normals, models or other similar references from lots of samples
summary: nf-core/createpanelrefs is a bioinformatics helper pipeline that will help in creating panel of normals and other models.
has_samplesheet: true
input: samplesheet (sample, bam, bai, cram, crai)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: CNVKIT, GATK, MultiQC
---
# createpanelrefs

nf-core/createpanelrefs is a bioinformatics helper pipeline that will help in creating panel of normals and other models.

## Run it
```bash
git submodule update --init pipelines/createpanelrefs/upstream   # first time only
nfclaw run createpanelrefs --input samplesheet.csv --outdir results --tools <tools> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/createpanelrefs/upstream -profile docker --input samplesheet.csv --outdir results --tools <tools>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions createpanelrefs` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show createpanelrefs --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `bam` | string (file path) | no |  | matches ^\S+\.bam$ |
| `bai` | string (file path) | no |  | matches ^\S+\.bai$ |
| `cram` | string (file path) | no |  | matches ^\S+\.cram$ |
| `crai` | string (file path) | no |  | matches ^\S+\.crai$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV. Each row must include **exactly one** of these mutually-exclusive column groups (providing columns from more than one group fails validation):
- `bam`
- `cram`

Fill each value per the table above and `reference.md`. Valid headers — pick the group that matches your data (optional columns from the table may be added):
```csv
sample,bam
```
```csv
sample,cram
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--tools` | string |  |  | matches ^((cnvkit\|germlinecnvcaller\|gens\|mutect2)?,?)*(?<!,)$ | Tools to use for building Panel of Normals or models. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **CNVkit options** (`cnvkit_options`) — 2 parameters
- **Generic options** (`generic_options`) — 16 parameters
- **GENS options** (`gens_options`) — 6 parameters
- **Germlinecnvcaller options** (`germlinecnvcaller_options`) — 6 parameters
- **Input/output options** (`input_output_options`) — 4 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Main options** (`main_options`) — 1 parameter
- **Mutect2 options** (`mutect2_options`) — 2 parameters
- **Reference genome options** (`reference_genome_options`) — 15 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run createpanelrefs --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/createpanelrefs/blob/1.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: CNVKIT, GATK, MultiQC.

Full list with references: https://github.com/nf-core/createpanelrefs/blob/1.0.0/CITATIONS.md

## Demo
```bash
nfclaw run createpanelrefs --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/createpanelrefs/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/createpanelrefs@8ce86a84b5af74facf99abb76216531622b52bc8. Do not edit by hand. -->
