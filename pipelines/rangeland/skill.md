---
name: rangeland
pipeline: nf-core/rangeland
version: 1.0.0
commit: 7c5cb9593b80d2a3cdc8bcb14137722351644435
description: Long-term vegetation trend analysis pipeline for rangeland systems using satellite imagery.
summary: nf-core/rangeland is a geographical best-practice analysis pipeline for remotely sensed imagery. The pipeline processes satellite imagery alongside auxiliary data in multiple steps to arrive at a set of trend files related to land-cover changes. The main pipeline steps are:
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FORCE, MultiQC
---
# rangeland

nf-core/rangeland is a geographical best-practice analysis pipeline for remotely sensed imagery. The pipeline processes satellite imagery alongside auxiliary data in multiple steps to arrive at a set of trend files related to land-cover changes. The main pipeline steps are:

## Run it
```bash
git submodule update --init pipelines/rangeland/upstream   # first time only
nfclaw run rangeland --input samplesheet.csv --outdir results --dem <dem> --wvdb <wvdb> --data-cube <data_cube> --aoi <aoi> --endmember <endmember> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/rangeland/upstream -profile docker --input samplesheet.csv --outdir results --dem <dem> --wvdb <wvdb> --data-cube <data_cube> --aoi <aoi> --endmember <endmember>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions rangeland` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show rangeland --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string |  |  |  | Root directory or tarball of all satellite imagery. |
| `--dem` | string |  |  |  | Digital elevation model. |
| `--wvdb` | string |  |  |  | Water vapor dataset. |
| `--data-cube` | string (file path) |  |  | matches ^\S+\.prj$ | Datacube definition. |
| `--aoi` | string (file path) |  |  | matches ^\S+\.(gpkg\|shp)$ | Area of interest. |
| `--endmember` | string (file path) |  |  | matches ^\S+\.txt$ | Endmember definition. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `generic_options` (13 parameters)
- `higher_level_processing_modification` (2 parameters)
- `input_output_options` (9 parameters)
- `institutional_config_options` (6 parameters)
- `remote_sensing_image_options` (4 parameters)
- `visualization` (2 parameters)
- `workflow_configuration` (4 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/rangeland/blob/1.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FORCE, MultiQC.

Full list with references: https://github.com/nf-core/rangeland/blob/1.0.0/CITATIONS.md

## Demo
```bash
nfclaw run rangeland --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/rangeland/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/rangeland@7c5cb9593b80d2a3cdc8bcb14137722351644435. Do not edit by hand. -->
