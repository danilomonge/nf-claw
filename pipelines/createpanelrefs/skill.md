---
name: createpanelrefs
pipeline: nf-core/createpanelrefs
version: 1.0.0
commit: 8ce86a84b5af74facf99abb76216531622b52bc8
description: Generate Panel of Normals, models or other similar references from lots of samples
has_samplesheet: true
input: samplesheet (sample, bam, bai, cram, crai)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
---
# createpanelrefs

Generate Panel of Normals, models or other similar references from lots of samples

## Run it
```bash
git submodule update --init pipelines/createpanelrefs/upstream   # first time only
nfclaw run createpanelrefs --input samplesheet.csv --outdir results --tools <tools> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/createpanelrefs/upstream -profile docker --input samplesheet.csv --outdir results --tools <tools>
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `bam` | string (file path) | no |  | matches ^\S+\.bam$ |
| `bai` | string (file path) | no |  | matches ^\S+\.bai$ |
| `cram` | string (file path) | no |  | matches ^\S+\.cram$ |
| `crai` | string (file path) | no |  | matches ^\S+\.crai$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,bam,bai,cram,crai
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--tools` | string |  | matches ^((cnvkit\|germlinecnvcaller\|gens\|mutect2)?,?)*(?<!,)$ | Tools to use for building Panel of Normals or models. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `cnvkit_options` (2 parameters)
- `generic_options` (16 parameters)
- `gens_options` (6 parameters)
- `germlinecnvcaller_options` (6 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `main_options` (1 parameter)
- `mutect2_options` (2 parameters)
- `reference_genome_options` (15 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/createpanelrefs/blob/1.0.0/docs/output.md

## Demo
```bash
nfclaw run createpanelrefs --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/createpanelrefs/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/createpanelrefs@8ce86a84b5af74facf99abb76216531622b52bc8. Do not edit by hand. -->
