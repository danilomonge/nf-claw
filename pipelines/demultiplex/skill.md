---
name: demultiplex
pipeline: nf-core/demultiplex
version: 1.7.1
commit: fbec8e442f0599f8b74876e62263af05b9a41d33
description: Demultiplexing pipeline for Illumina sequencing data
summary: nf-core/demultiplex is a bioinformatics pipeline used to demultiplex the raw data produced by next generation sequencing machines. The following platforms are supported:
has_samplesheet: true
input: samplesheet (id, samplesheet, lane, flowcell, per_flowcell_manifest)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: fastp, Falco, MultiQC, CheckQC, samshee
---
# demultiplex

nf-core/demultiplex is a bioinformatics pipeline used to demultiplex the raw data produced by next generation sequencing machines. The following platforms are supported:

## Run it
```bash
git submodule update --init pipelines/demultiplex/upstream   # first time only
nfclaw run demultiplex --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/demultiplex/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions demultiplex` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show demultiplex --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `id` | string | yes |  | matches ^\S+$ |
| `samplesheet` | string (file path) | yes |  | matches ^\S+\.csv$ |
| `lane` | integer | no |  | ≥ 1; ≤ 8 |
| `flowcell` | string | yes |  |  |
| `per_flowcell_manifest` | string (file path) | no |  |  |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
id,samplesheet,flowcell
```

Any of the optional columns above may be appended to the header when your data needs them: `lane`, `per_flowcell_manifest`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--demultiplexer` | string | bclconvert | bases2fastq, bcl2fastq, bclconvert, fqtk, sgdemux, mkfastq, mgikit |  | Demultiplexer to use. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **CheckQC options** (`checkqc_options`) — 1 parameter
- **Demultiplexing options** (`demultiplex_options`) — 1 parameter
- **Downstream CSV options** (`downstream_csv_options`) — 1 parameter
- **Generic options** (`generic_options`) — 17 parameters
- **Input/output options** (`input_output_options`) — 10 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Workflow options** (`workflow_options`) — 8 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run demultiplex --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.10.2'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run demultiplex ... --nxf-ver 25.10.2
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/demultiplex/blob/1.7.1/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: fastp, Falco, MultiQC, CheckQC, samshee.

Full list with references: https://github.com/nf-core/demultiplex/blob/1.7.1/CITATIONS.md

## Demo
```bash
nfclaw run demultiplex --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/demultiplex/blob/1.7.1/docs/usage.md

<!-- Generated from nf-core/demultiplex@fbec8e442f0599f8b74876e62263af05b9a41d33. Do not edit by hand. -->
