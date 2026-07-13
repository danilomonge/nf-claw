---
name: proteinfold
pipeline: nf-core/proteinfold
version: 2.0.0
commit: 5338c24b2af62cc4c02dcd34bcc49912eebffb3a
description: Protein 3D structure prediction pipeline
summary: nf-core/proteinfold is a bioinformatics best-practice analysis pipeline for Protein 3D structure prediction.
has_samplesheet: true
input: samplesheet (sequence, id, fasta)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: AlphaFold, ColabFold, MMseqs2, ESMFold, MultiQC
---
# proteinfold

nf-core/proteinfold is a bioinformatics best-practice analysis pipeline for Protein 3D structure prediction.

## Run it
```bash
git submodule update --init pipelines/proteinfold/upstream   # first time only
nfclaw run proteinfold --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/proteinfold/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions proteinfold` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show proteinfold --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sequence` | string | no |  | matches ^\S+$ |
| `id` | string | no |  | matches ^\S+$ |
| `fasta` | string (file path) | yes |  | matches ^\S+\.(fa(sta)?\|faa\|yaml\|yml\|json)$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sequence,id,fasta
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `alphafold2_dbs_and_parameters_link_options` (12 parameters)
- `alphafold2_dbs_and_parameters_paths_options` (12 parameters)
- `alphafold2_options` (6 parameters)
- `alphafold3_dbs_and_parameters_link_options` (10 parameters)
- `alphafold3_dbs_and_parameters_path_options` (10 parameters)
- `boltz_dbs_and_model_links_options` (5 parameters)
- `boltz_dbs_and_parameters_paths_options` (6 parameters)
- `boltz_options` (3 parameters)
- `colabfold_dbs_and_parameters_link_options` (3 parameters)
- `colabfold_dbs_and_parameters_paths_options` (5 parameters)
- `colabfold_options` (7 parameters)
- `esmfold_options` (2 parameters)
- `esmfold_parameters_link_options` (3 parameters)
- `esmfold_parameters_paths_options` (2 parameters)
- `foldseek_options` (4 parameters)
- `generic_options` (16 parameters)
- `helixfold3_dbs_and_parameters_link_options` (14 parameters)
- `helixfold3_dbs_and_parameters_paths_options` (14 parameters)
- `helixfold3_options` (3 parameters)
- `input_output_options` (13 parameters)
- `institutional_config_options` (6 parameters)
- `process_skipping_options` (2 parameters)
- `rosettafold2na_dbs_and_parameters_link_options` (9 parameters)
- `rosettafold2na_dbs_and_parameters_path_options` (5 parameters)
- `rosettafold2na_options` (1 parameter)
- `rosettafold_all_atom_dbs_and_parameters_links_options` (4 parameters)
- `rosettafold_all_atom_dbs_and_parameters_paths_options` (5 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/proteinfold/blob/2.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: AlphaFold, ColabFold, MMseqs2, ESMFold, MultiQC.

Full list with references: https://github.com/nf-core/proteinfold/blob/2.0.0/CITATIONS.md

## Demo
```bash
nfclaw run proteinfold --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/proteinfold/blob/2.0.0/docs/usage.md

<!-- Generated from nf-core/proteinfold@5338c24b2af62cc4c02dcd34bcc49912eebffb3a. Do not edit by hand. -->
