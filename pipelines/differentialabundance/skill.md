---
name: differentialabundance
pipeline: nf-core/differentialabundance
version: 1.5.0
commit: 3dd360fed0dca1780db1bdf5dce85e5258fa2253
description: Differential abundance analysis
has_samplesheet: true
input: samplesheet (sample)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: GSEA
---
# differentialabundance

Differential abundance analysis

## Run it
```bash
git submodule update --init pipelines/differentialabundance/upstream   # first time only
nfclaw run differentialabundance --input samplesheet.csv --outdir results --contrasts <contrasts> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/differentialabundance/upstream -profile docker --input samplesheet.csv --outdir results --contrasts <contrasts>
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | no |  | matches ^\S+$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--study-name` | string |  |  | A string to identify results in the output directory |
| `--study-type` | string | rnaseq, affy_array, maxquant, geo_soft_file |  | A string identifying the technology used to produce the data |
| `--input` | string (file path) |  | matches ^\S+\.(csv\|tsv\|txt)$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--contrasts` | string (file path) |  | matches ^\S+\.(csv\|tsv\|txt)$ | A CSV file describing sample contrasts |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--study-abundance-type` | string |  |  | Type of abundance measure used, platform-dependent |
| `--observations-id-col` | string |  |  | Column in the samples sheet to be used as the primary sample identifier |
| `--observations-type` | string |  |  | Type of observation |
| `--features-id-col` | string |  |  | Feature ID attribute in the abundance table as well as in the GTF file (e.g. the gene_id field) |
| `--features-name-col` | string |  |  | Feature name attribute in the abundance table as well as in the GTF file (e.g. the gene symbol field) |
| `--features-type` | string |  |  | Type of feature we have, often 'gene' |
| `--filtering-min-abundance` | number |  |  | Minimum abundance value |
| `--exploratory-clustering-method` | string |  |  | Clustering method used in dendrogram creation |
| `--exploratory-cor-method` | string |  |  | Correlation method used in dendrogram creation |
| `--exploratory-n-features` | integer |  |  | Number of features selected before certain exploratory analyses. If -1, will use all features. |
| `--exploratory-main-variable` | string |  |  | How should the main grouping variable be selected? 'auto_pca', 'contrasts', or a valid column name from the observations table. |
| `--exploratory-palette-name` | string |  |  | Valid R palette name |
| `--differential-feature-id-column` | string |  |  | The feature identifier column in differential results tables |
| `--differential-fc-column` | string |  |  | The fold change column in differential results tables |
| `--differential-qval-column` | string |  |  | The q value column in differential results tables. |
| `--differential-min-fold-change` | number |  |  | Minimum fold change used to calculate differential feature numbers |
| `--differential-max-pval` | number |  |  | Maximum p value used to calculate differential feature numbers |
| `--differential-max-qval` | number |  |  | Maximum q value used to calculate differential feature numbers |
| `--differential-palette-name` | string |  |  | Valid R palette name |
| `--report-file` | string (file path) |  | matches ^\S+\.Rmd$ | Rmd report template from which to create the pipeline report |
| `--logo-file` | string |  |  | A logo to display in the report instead of the generic pipeline logo |
| `--css-file` | string |  |  | CSS to use to style the output, in lieu of the default nf-core styling |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `abundance_values` (4 parameters)
- `affy_input_options` (9 parameters)
- `deseq2_specific_options_rna_seq_only` (16 parameters)
- `differential_analysis` (12 parameters)
- `exploratory_analysis` (10 parameters)
- `features_options` (9 parameters)
- `filtering` (6 parameters)
- `gene_set_options` (1 parameter)
- `generic_options` (11 parameters)
- `gprofiler2` (14 parameters)
- `gsea` (18 parameters)
- `input_output_options` (6 parameters)
- `institutional_config_options` (6 parameters)
- `limma_specific_options_microarray_only` (14 parameters)
- `max_job_request_options` (3 parameters)
- `observations_options` (3 parameters)
- `proteus_input_options` (5 parameters)
- `reference_genome_options` (3 parameters)
- `reporting_options` (11 parameters)
- `shiny_app_settings` (5 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/differentialabundance/blob/1.5.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: GSEA.

Full list with references: https://github.com/nf-core/differentialabundance/blob/1.5.0/CITATIONS.md

## Demo
```bash
nfclaw run differentialabundance --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/differentialabundance/blob/1.5.0/docs/usage.md

<!-- Generated from nf-core/differentialabundance@3dd360fed0dca1780db1bdf5dce85e5258fa2253. Do not edit by hand. -->
