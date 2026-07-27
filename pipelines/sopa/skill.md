---
name: sopa
pipeline: nf-core/sopa
version: 1.0.0
commit: f42485ead97376c4f7cb70e11916f13b35e092f1
description: Technology-invariant pipeline for spatial omics analysis that scales to millions of cells
summary: nf-core/sopa is the Nextflow version of Sopa. Built on top of SpatialData, Sopa enables processing and analyses of spatial omics data with single-cell resolution (spatial transcriptomics or multiplex imaging data) using a standard data structure and output. We currently support the following technologies: Xenium, Visium HD, MERSCOPE, CosMX, PhenoCycler, MACSima, Molecural Cartography, and others. It outputs a .zarr directory containing a processed SpatialData object, and a .explorer directory for visualization.
has_samplesheet: true
input: samplesheet (sample, id, data_path, fastq_dir, cytaimage, colorizedimage, darkimage, image, slide, area, manual_alignment, slidefile)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions)
tools: AnnData, Scanpy, Space Ranger, SpatialData
---
# sopa

nf-core/sopa is the Nextflow version of Sopa. Built on top of SpatialData, Sopa enables processing and analyses of spatial omics data with single-cell resolution (spatial transcriptomics or multiplex imaging data) using a standard data structure and output. We currently support the following technologies: Xenium, Visium HD, MERSCOPE, CosMX, PhenoCycler, MACSima, Molecural Cartography, and others. It outputs a .zarr directory containing a processed SpatialData object, and a .explorer directory for visualization.

## Run it
```bash
git submodule update --init pipelines/sopa/upstream   # first time only
nfclaw run sopa --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/sopa/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions sopa` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show sopa --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | no |  | matches ^\S+$ |
| `id` | string | no |  | matches ^\S+$ |
| `data_path` | string | no |  | matches ^\S+$ |
| `fastq_dir` | string | no |  | matches ^\S+$ |
| `cytaimage` | string | no |  | matches ^\S+(tif\|tiff)$ |
| `colorizedimage` | string | no |  | matches ^\S+(tif\|tiff\|jpg\|jpeg\|btf)$ |
| `darkimage` | string | no |  | matches ^\S+(tif\|tiff\|jpg\|jpeg\|btf)$ |
| `image` | string | no |  | matches ^\S+(tif\|tiff\|jpg\|jpeg\|btf)$ |
| `slide` | string | no |  | matches ^\S+$ |
| `area` | string | no |  | matches ^\S+$ |
| `manual_alignment` | string | no |  | matches ^\S+json$ |
| `slidefile` | string | no |  | matches ^\S+json$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,id,data_path,fastq_dir,cytaimage,colorizedimage,darkimage,image,slide,area,manual_alignment,slidefile
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--technology` | string | xenium | xenium, merscope, cosmx, visium_hd, molecular_cartography, macsima, phenocycler, hyperion, ome_tif, toy_dataset |  | Technology used for the spatial data, e.g., 'xenium', 'merscope', ... |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Aggregation** (`aggregation`) — 3 parameters
- **Baysor** (`baysor`) — 9 parameters
- **Cellpose** (`cellpose`) — 9 parameters
- **Comseg** (`comseg`) — 7 parameters
- **Explorer** (`explorer`) — 3 parameters
- **Cell filtering** (`filtering`) — 4 parameters
- **Fluorescence annotation** (`fluorescence_annotation`) — 3 parameters
- **Generic options** (`generic_options`) — 12 parameters
- **Image preprocessing** (`image_preprocessing`) — 3 parameters
- **Input/output options** (`input_output_options`) — 3 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Patches** (`patches`) — 6 parameters
- **Proseg** (`proseg`) — 4 parameters
- **Reader** (`reader`) — 2 parameters
- **Scanpy preprocessing** (`scanpy_preprocessing`) — 4 parameters
- **Space Ranger options** (`spaceranger_options`) — 2 parameters
- **Stardist** (`stardist`) — 6 parameters
- **Tissue segmentation** (`tissue_segmentation`) — 4 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run sopa --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.04.0'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run sopa ... --nxf-ver 25.04.0
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/sopa/blob/1.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: AnnData, Scanpy, Space Ranger, SpatialData.

Full list with references: https://github.com/nf-core/sopa/blob/1.0.0/CITATIONS.md

## Demo
```bash
nfclaw run sopa --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/sopa/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/sopa@f42485ead97376c4f7cb70e11916f13b35e092f1. Do not edit by hand. -->
