---
name: pixelator
pipeline: nf-core/pixelator
version: 4.1.2
commit: 054a1c9927e07445e25fc2f05c33b723dcd61656
description: Pipeline for analysis of Proximity Network Assay data
summary: nf-core/pixelator is a bioinformatics best-practice analysis pipeline for analysis of data from the Proximity Network (PNA) assay. It takes a samplesheet as input and will process your data using pixelator to produce a PXL file containing single-cell protein abundance and protein interactomics data.
has_samplesheet: true
input: samplesheet (pool, hash_index, sample, sample_alias, condition, design, panel, panel_file, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions)
tools: pixelator, cutadapt, fastp
---
# pixelator

nf-core/pixelator is a bioinformatics best-practice analysis pipeline for analysis of data from the Proximity Network (PNA) assay. It takes a samplesheet as input and will process your data using pixelator to produce a PXL file containing single-cell protein abundance and protein interactomics data.

## Run it
```bash
git submodule update --init pipelines/pixelator/upstream   # first time only
nfclaw run pixelator --input samplesheet.csv --outdir results --technology <technology> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/pixelator/upstream -profile docker --input samplesheet.csv --outdir results --technology <technology>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions pixelator` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show pixelator --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `pool` | string | no |  | matches ^\S+$ |
| `hash_index` | integer | no |  |  |
| `sample` | string | yes |  | matches ^\S+$ |
| `sample_alias` | string | yes |  |  |
| `condition` | string | yes |  |  |
| `design` | string | yes |  | matches ^\S+$ |
| `panel` | string | no |  | matches ^\S+$ |
| `panel_file` | string | no |  | matches ^$\|^\S+\.(csv\|tsv\|ya?ml)$ |
| `fastq_1` | string | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string | no |  | matches ^\S+\.f(ast)?q\.gz$ |

`--input` must match `^\S+\.(csv|tsv|yml|yaml)$`.

For tabular CSV/TSV input, use this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
pool,hash_index,sample,sample_alias,condition,design,panel,panel_file,fastq_1,fastq_2
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.(csv\|tsv\|yml\|yaml)$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--technology` | string |  | proxiome-v1, proxiome-v2, hashed_samples, nonhashed_samples |  | The technology used to process the samples |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `experiment_summary_options` (1 parameter)
- `generic_options` (12 parameters)
- `global_config_options` (5 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `pna_amplicon_options` (9 parameters)
- `pna_analysis_options` (7 parameters)
- `pna_collapse_options` (3 parameters)
- `pna_demux_options` (7 parameters)
- `pna_denoise_options` (9 parameters)
- `pna_graph_options` (12 parameters)
- `pna_layout_options` (5 parameters)
- `pna_sample_calling_options` (4 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/pixelator/blob/4.1.2/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: pixelator, cutadapt, fastp.

Full list with references: https://github.com/nf-core/pixelator/blob/4.1.2/CITATIONS.md

## Demo
```bash
nfclaw run pixelator --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/pixelator/blob/4.1.2/docs/usage.md

<!-- Generated from nf-core/pixelator@054a1c9927e07445e25fc2f05c33b723dcd61656. Do not edit by hand. -->
