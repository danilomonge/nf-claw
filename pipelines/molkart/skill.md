---
name: molkart
pipeline: nf-core/molkart
version: 1.2.0
commit: 4ec0790d80cf77f2428d33b1a8571ccb498e2170
description: An analysis pipeline for processing Molecular Cartography data.
summary: nf-core/molkart is a pipeline for processing Molecular Cartography data from Resolve Bioscience (combinatorial FISH). It takes as input a table of FISH spot positions (x,y,z,gene), a corresponding DAPI image (TIFF format) and optionally an additional staining image in the TIFF format. nf-core/molkart performs end-to-end processing of the data including image processing, QC filtering of spots, cell segmentation, spot-to-cell assignment and reports quality metrics such as the spot assignment rate, average spots per cell and segmentation mask size ranges.
has_samplesheet: true
input: samplesheet (sample, nuclear_image, spot_table, membrane_image)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: anndata, Cellpose, ilastik, Mesmer, Mindagap, MultiQC, Stardist
---
# molkart

nf-core/molkart is a pipeline for processing Molecular Cartography data from Resolve Bioscience (combinatorial FISH). It takes as input a table of FISH spot positions (x,y,z,gene), a corresponding DAPI image (TIFF format) and optionally an additional staining image in the TIFF format. nf-core/molkart performs end-to-end processing of the data including image processing, QC filtering of spots, cell segmentation, spot-to-cell assignment and reports quality metrics such as the spot assignment rate, average spots per cell and segmentation mask size ranges.

## Run it
```bash
git submodule update --init pipelines/molkart/upstream   # first time only
nfclaw run molkart --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/molkart/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions molkart` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show molkart --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `nuclear_image` | string (file path) | yes |  | matches ^\S+\.(tif\|tiff)$ |
| `spot_table` | string (file path) | yes |  | matches ^\S+\.(txt\|tsv)$ |
| `membrane_image` | string | no |  |  |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,nuclear_image,spot_table
```

Any of the optional columns above may be appended to the header when your data needs them: `membrane_image`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--segmentation-method` | string | mesmer |  |  | List of segmentation tools to apply to the image. Allowed values: mesmer, cellpose, stardist, ilastik. Use a comma-separated string without whitespaces for multiple methods. |
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Generic options** (`generic_options`) — 17 parameters
- **Image preprocessing** (`image_preprocessing`) — 11 parameters
- **Input/output options** (`input_output_options`) — 4 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Segmentation methods and options** (`segmentation_methods_and_options`) — 19 parameters
- **Training subset options** (`training_subset_options`) — 5 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run molkart --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/molkart/blob/1.2.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: anndata, Cellpose, ilastik, Mesmer, Mindagap, MultiQC, Stardist.

Full list with references: https://github.com/nf-core/molkart/blob/1.2.0/CITATIONS.md

## Demo
```bash
nfclaw run molkart --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/molkart/blob/1.2.0/docs/usage.md

<!-- Generated from nf-core/molkart@4ec0790d80cf77f2428d33b1a8571ccb498e2170. Do not edit by hand. -->
