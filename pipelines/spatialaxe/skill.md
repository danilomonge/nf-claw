---
name: spatialaxe
pipeline: nf-core/spatialaxe
version: 1.0.0
commit: 494cf02857bd24b2d065f938f7e96e523b5b7def
description: A pipeline to process spatialomics data from 10x Xenium In Situ or 10x Atera.
summary: nf-core/spatialaxe is a bioinformatics best-practice processing and quality control pipeline for Xenium (and soon Atera) data. The current plan for the pipeline implementation is shown in the metromap below. The pipeline is under active developement and changes might occure frequently.
has_samplesheet: true
input: samplesheet (sample, bundle, image)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: MultiQC
---
# spatialaxe

nf-core/spatialaxe is a bioinformatics best-practice processing and quality control pipeline for Xenium (and soon Atera) data. The current plan for the pipeline implementation is shown in the metromap below. The pipeline is under active developement and changes might occure frequently.

## Run it
```bash
git submodule update --init pipelines/spatialaxe/upstream   # first time only
nfclaw run spatialaxe --input samplesheet.csv --outdir results --mode <mode> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/spatialaxe/upstream -profile docker --input samplesheet.csv --outdir results --mode <mode>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions spatialaxe` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show spatialaxe --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `bundle` | string | yes |  | matches ^\S+$ |
| `image` | string | no |  | matches ^\S+$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,bundle
```

Any of the optional columns above may be appended to the header when your data needs them: `image`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the Xenium experiment. (eg; meta,path-to-xenium-bundle,path-to-morphology.ome.tif)) |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--mode` | string |  | image, coordinate, segfree, preview, qc |  | Mode in which the pipeline is to be run. Either image-based segmentation, coordinate-based segmentation, segmentation-free analysis or data preview. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Generic options** (`generic_options`) — 17 parameters
- **Input/output options** (`input_output_options`) — 19 parameters
- **Institutional config options** (`institutional_config_options`) — 7 parameters
- **Segmentation options** (`segmentation_options`) — 60 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run spatialaxe --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.04.0'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run spatialaxe ... --nxf-ver 25.04.0
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/spatialaxe/blob/1.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: MultiQC.

Full list with references: https://github.com/nf-core/spatialaxe/blob/1.0.0/CITATIONS.md

## Demo
```bash
nfclaw run spatialaxe --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/spatialaxe/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/spatialaxe@494cf02857bd24b2d065f938f7e96e523b5b7def. Do not edit by hand. -->
