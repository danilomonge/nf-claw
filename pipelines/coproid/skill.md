---
name: coproid
pipeline: nf-core/coproid
version: 2.0.1
commit: 045d569d5b01b2d1572220718e64a6d054ad57eb
description:  COPROlite host IDentification 
summary: nf-core/coproid is a bioinformatics pipeline that helps you identify the "true maker" of Illumina sequenced (Paleo)faeces by checking the microbiome composition and the endogenous host DNA.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: BBnorm/BBTools, Bowtie2, damageprofiler, FastP, FastQC, Kraken2, MultiQC, PyDamage, Quarto, Sam2lca, SAMtools, sourcepredict
---
# coproid

nf-core/coproid is a bioinformatics pipeline that helps you identify the "true maker" of Illumina sequenced (Paleo)faeces by checking the microbiome composition and the endogenous host DNA.

## Run it
```bash
git submodule update --init pipelines/coproid/upstream   # first time only
nfclaw run coproid --input samplesheet.csv --outdir results --genome-sheet <genome_sheet> --kraken2-db <kraken2_db> --sp-sources <sp_sources> --sp-labels <sp_labels> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/coproid/upstream -profile docker --input samplesheet.csv --outdir results --genome-sheet <genome_sheet> --kraken2-db <kraken2_db> --sp-sources <sp_sources> --sp-labels <sp_labels>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions coproid` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show coproid --pipeline-version X.Y.Z` prints that release's docs).

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
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--genome-sheet` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the reference genomes. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--kraken2-db` | string (file path) |  |  | Path to a kraken2 database, can be a directory or *.tar.gz |
| `--sp-sources` | string (file path) |  |  | Sources TAXID count table in csv format for sourcepredict |
| `--sp-labels` | string (file path) |  |  | Labels for the sources table in csv format for sourcepredict |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `generic_options` (17 parameters)
- `input_output_options` (5 parameters)
- `institutional_config_options` (6 parameters)
- `pipeline_options` (11 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/coproid/blob/2.0.1/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: BBnorm/BBTools, Bowtie2, damageprofiler, FastP, FastQC, Kraken2, MultiQC, PyDamage, Quarto, Sam2lca, SAMtools, sourcepredict.

Full list with references: https://github.com/nf-core/coproid/blob/2.0.1/CITATIONS.md

## Demo
```bash
nfclaw run coproid --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/coproid/blob/2.0.1/docs/usage.md

<!-- Generated from nf-core/coproid@045d569d5b01b2d1572220718e64a6d054ad57eb. Do not edit by hand. -->
