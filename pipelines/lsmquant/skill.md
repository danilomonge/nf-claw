---
name: lsmquant
pipeline: nf-core/lsmquant
version: 1.0.2
commit: 6854d63d22ea0d04d4146a8639a726c9648a46ee
description: A pipeline for preprocessing and analysis of large-scale light-sheet microscopy images based on the NuMorph toolbox
summary: nf-core/lsmquant is a bioinformatics pipeline that performs preprocessing and analysis of light-sheet microscopy images of tissue cleared samples. The pipeline takes raw images from a directory or a zip archive as input. The images need to be in a 2D single-channel 16-bit tifformat.
has_samplesheet: true
input: samplesheet (sample_id, img_directory, parameter_file)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: BaSiC, elastix, MultiQC, NuMorph, 3DUnetCNN
---
# lsmquant

nf-core/lsmquant is a bioinformatics pipeline that performs preprocessing and analysis of light-sheet microscopy images of tissue cleared samples. The pipeline takes raw images from a directory or a zip archive as input. The images need to be in a 2D single-channel 16-bit tifformat.

## Run it
```bash
git submodule update --init pipelines/lsmquant/upstream   # first time only
nfclaw run lsmquant --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/lsmquant/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions lsmquant` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show lsmquant --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample_id` | string | yes |  | matches ^\S+$ |
| `img_directory` | string | yes |  | matches ^(https?://.*\.zip\|.*\.zip\|.*/)$ |
| `parameter_file` | string (file path) | yes |  | matches ^\S+\.csv$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample_id,img_directory,parameter_file
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  |  | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `generic_options` (15 parameters)
- `input_output_options` (8 parameters)
- `institutional_config_options` (6 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/lsmquant/blob/1.0.2/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: BaSiC, elastix, MultiQC, NuMorph, 3DUnetCNN.

Full list with references: https://github.com/nf-core/lsmquant/blob/1.0.2/CITATIONS.md

## Demo
```bash
nfclaw run lsmquant --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/lsmquant/blob/1.0.2/docs/usage.md

<!-- Generated from nf-core/lsmquant@6854d63d22ea0d04d4146a8639a726c9648a46ee. Do not edit by hand. -->
