---
name: drugresponseeval
pipeline: nf-core/drugresponseeval
version: 1.2.1
commit: 877ef94f5f0cd3597ffc5c2c3564039770f7c840
description: This pipeline evaluates drug response models in various settings on a variety of datasets.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions)
tools: DrEvalPy, CurveCurator, DIPK, MOLI, SRMF, SuperFELT
---
# drugresponseeval

This pipeline evaluates drug response models in various settings on a variety of datasets.

## Run it
```bash
git submodule update --init pipelines/drugresponseeval/upstream   # first time only
nfclaw run drugresponseeval --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/drugresponseeval/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--models` | string |  |  | Model to be tested. |
| `--baselines` | string |  |  | Baselines to be tested. |
| `--run-id` | string |  |  | Run name for the pipeline. The subdirectory in results will be named like this. |
| `--dataset-name` | string |  |  | Name of the dataset. Pre-supplied datasets are CTRPv2, CTRPv1, CCLE, GDSC1, GDSC2, TOYv1, TOYv2, BeatAML2, and PDX_Bruna. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. Default is results/ |
| `--test-mode` | string |  | matches ^((LPO\|LCO\|LTO\|LDO)?,?)*(?<!,)$ | Run the pipeline in test mode LPO (Leave-random-Pairs-Out), LCO (Leave-Cell-line-Out), or LDO (Leave-Drug-Out). |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `additional_options` (7 parameters)
- `data_options` (4 parameters)
- `generic_options` (11 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `mode_options` (1 parameter)
- `model_options` (2 parameters)
- `randomization_options` (2 parameters)
- `robustness_options` (1 parameter)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/drugresponseeval/blob/1.2.1/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: DrEvalPy, CurveCurator, DIPK, MOLI, SRMF, SuperFELT.

Full list with references: https://github.com/nf-core/drugresponseeval/blob/1.2.1/CITATIONS.md

## Demo
```bash
nfclaw run drugresponseeval --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/drugresponseeval/blob/1.2.1/docs/usage.md

<!-- Generated from nf-core/drugresponseeval@877ef94f5f0cd3597ffc5c2c3564039770f7c840. Do not edit by hand. -->
