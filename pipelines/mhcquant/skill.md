---
name: mhcquant
pipeline: nf-core/mhcquant
version: 3.2.0
commit: 6ec12c97f7889a3e1f09ab89930723045c6bac68
description: Identify and quantify peptides from mass spectrometry raw data
summary: nfcore/mhcquant is a best-practice bioinformatics pipeline to process data-dependent acquisition (DDA) immunopeptidomics data. This involves mass spectrometry-based identification and quantification of immunopeptides presented on major histocompatibility complex (MHC) molecules which mediate T cell immunosurveillance. Immunopeptidomics has central implications for clinical research, in the context of T cell-centric immunotherapies.
has_samplesheet: true
input: samplesheet (ID, Sample, Condition, ReplicateFileName, Fasta, SearchPreset)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: OpenMS, Comet, DeepLC, MS²PIP, Ionmob, MS²Rescore, Percolator, Mokapot, MultiQC
---
# mhcquant

nfcore/mhcquant is a best-practice bioinformatics pipeline to process data-dependent acquisition (DDA) immunopeptidomics data. This involves mass spectrometry-based identification and quantification of immunopeptides presented on major histocompatibility complex (MHC) molecules which mediate T cell immunosurveillance. Immunopeptidomics has central implications for clinical research, in the context of T cell-centric immunotherapies.

## Run it
```bash
git submodule update --init pipelines/mhcquant/upstream   # first time only
nfclaw run mhcquant --input samplesheet.tsv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/mhcquant/upstream -profile docker --input samplesheet.tsv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions mhcquant` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show mhcquant --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `ID` | integer | yes |  |  |
| `Sample` | string or integer | yes |  |  |
| `Condition` | string or integer | yes |  |  |
| `ReplicateFileName` | string | yes |  | matches ^\S+\.(raw\|RAW\|mzML\|mzML.gz\|d\|d.tar\|d.tar.gz\|d.zip)$ |
| `Fasta` | string | no |  | matches ^\S+\.(fasta\|fa\|fas\|fna\|faa\|ffn)$ |
| `SearchPreset` | string | no |  | matches ^[a-zA-Z0-9_]+$ |

`--input` must match `^(PXD\d{6,}|\S+\.sdrf\.tsv|\S+\.tsv)$`.

The samplesheet is a TSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```tsv
ID	Sample	Condition	ReplicateFileName	Fasta	SearchPreset
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string |  |  | matches ^(PXD\d{6,}\|\S+\.sdrf\.tsv\|\S+\.tsv)$ | Input: samplesheet TSV, SDRF file (.sdrf.tsv), or PRIDE accession (PXD...) |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `database_options` (2 parameters)
- `epicore_options` (4 parameters)
- `generic_options` (16 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `post_processing` (4 parameters)
- `preprocessing` (3 parameters)
- `quantification_options` (9 parameters)
- `rescoring_settings` (9 parameters)
- `search_settings` (22 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/mhcquant/blob/3.2.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: OpenMS, Comet, DeepLC, MS²PIP, Ionmob, MS²Rescore, Percolator, Mokapot, MultiQC.

Full list with references: https://github.com/nf-core/mhcquant/blob/3.2.0/CITATIONS.md

## Demo
```bash
nfclaw run mhcquant --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/mhcquant/blob/3.2.0/docs/usage.md

<!-- Generated from nf-core/mhcquant@6ec12c97f7889a3e1f09ab89930723045c6bac68. Do not edit by hand. -->
