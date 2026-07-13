---
name: phaseimpute
pipeline: nf-core/phaseimpute
version: 1.1.0
commit: 452783d960ebd2b4d337a649e9c8eb3859611916
description: Phasing and imputation pipeline
summary: nf-core/phaseimpute is a bioinformatics pipeline to phase and impute genetic data.
has_samplesheet: true
input: samplesheet (sample, tools, file, index)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: bcftools, GLIMPSE, GLIMPSE2, MultiQC, QUILT, Shapeit, STITCH
---
# phaseimpute

nf-core/phaseimpute is a bioinformatics pipeline to phase and impute genetic data.

## Run it
```bash
git submodule update --init pipelines/phaseimpute/upstream   # first time only
nfclaw run phaseimpute --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/phaseimpute/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions phaseimpute` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show phaseimpute --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^[a-zA-Z0-9_-]+$ |
| `tools` | string | no |  | matches ^[a-zA-Z0-9_]+$ |
| `file` | string | yes |  | matches ^\S+\.(bam\|cram)\|((vcf\|bcf)(\.gz))?$ |
| `index` | string | yes |  | matches ^\S+\.(bai\|crai\|tbi\|csi)$ |

`--input` must match `^\S+\.(csv|tsv|yaml|json)$`.

For tabular CSV/TSV input, use this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,file,index
```

Any of the optional columns above may be appended to the header when your data needs them: `tools`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Generic options** (`generic_options`) — 18 parameters
- **Imputation options** (`imputation_options`) — 4 parameters
- **Input/output options** (`input_output_options`) — 10 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Panel preparation** (`panelprep`) — 5 parameters
- **QUILT parameters** (`quilt_parameters`) — 2 parameters
- **Reference genome options** (`reference_genome_options`) — 6 parameters
- **Simulate** (`simulate`) — 2 parameters
- **STITCH parameters** (`stitch_parameters`) — 1 parameter
- **Concordance analysis** (`validation`) — 4 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run phaseimpute --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/phaseimpute/blob/1.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: bcftools, GLIMPSE, GLIMPSE2, MultiQC, QUILT, Shapeit, STITCH.

Full list with references: https://github.com/nf-core/phaseimpute/blob/1.1.0/CITATIONS.md

## Demo
```bash
nfclaw run phaseimpute --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/phaseimpute/blob/1.1.0/docs/usage.md

<!-- Generated from nf-core/phaseimpute@452783d960ebd2b4d337a649e9c8eb3859611916. Do not edit by hand. -->
