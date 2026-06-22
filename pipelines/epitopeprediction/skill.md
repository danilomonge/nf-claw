---
name: epitopeprediction
pipeline: nf-core/epitopeprediction
version: 3.1.0
commit: 4c13c15b46ec69e959faf2cf338e9ceb795a19d5
description: A fully reproducible and state of the art epitope prediction pipeline.
has_samplesheet: true
input: samplesheet (sample, alleles, mhc_class, filename)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: MultiQC, SnpSift, Epytope (FRED2), MHCflurry, MHCnuggets, NetMHC-4.0, NetMHCpan-4.0, NetMHCpan-4.1, NetMHCII-2.3, NetMHCIIpan-4.0
---
# epitopeprediction

A fully reproducible and state of the art epitope prediction pipeline.

## Run it
```bash
git submodule update --init pipelines/epitopeprediction/upstream   # first time only
nfclaw run epitopeprediction --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/epitopeprediction/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `alleles` | string | yes |  |  |
| `mhc_class` | string | yes |  | matches ^(I\|II)$ |
| `filename` | string (file path) | yes |  | matches ^\S+\.(vcf\|vcf.gz\|tsv\|fasta\|fa)$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,alleles,mhc_class,filename
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  |  | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `external_software` (4 parameters)
- `generic_options` (16 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `peptide_prediction_options` (11 parameters)
- `reference_options` (2 parameters)
- `run_optimisation` (5 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/epitopeprediction/blob/3.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: MultiQC, SnpSift, Epytope (FRED2), MHCflurry, MHCnuggets, NetMHC-4.0, NetMHCpan-4.0, NetMHCpan-4.1, NetMHCII-2.3, NetMHCIIpan-4.0.

Full list with references: https://github.com/nf-core/epitopeprediction/blob/3.1.0/CITATIONS.md

## Demo
```bash
nfclaw run epitopeprediction --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/epitopeprediction/blob/3.1.0/docs/usage.md

<!-- Generated from nf-core/epitopeprediction@4c13c15b46ec69e959faf2cf338e9ceb795a19d5. Do not edit by hand. -->
