---
name: multiplesequencealign
pipeline: nf-core/multiplesequencealign
version: 1.1.1
commit: 79724dac3d240b9bb7684532d3fe238b42f6a4b4
description: Pipeline to run and benchmark multiple sequence alignment tools.
summary: More introductory material: bytesize talk, nextflow summit talk, poster.
has_samplesheet: true
input: samplesheet (id, fasta, reference, optional_data, template)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: 3DCoffee, ClustalO, csvtk, FAMSA, FoldMason, Kalign3, learnMSA, MAFFT, MAGUS, MultiQC, mTM-align, Muscle5, T-Coffee, UPP, Biopython
---
# multiplesequencealign

More introductory material: bytesize talk, nextflow summit talk, poster.

## Run it
```bash
git submodule update --init pipelines/multiplesequencealign/upstream   # first time only
nfclaw run multiplesequencealign --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/multiplesequencealign/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions multiplesequencealign` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show multiplesequencealign --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `id` | string | yes |  | matches ^\S+$ |
| `fasta` | string (file path) | no |  | matches ^\S+\.f(n\|ast)?a$ |
| `reference` | string (file path) | no |  | matches ^\S+\.(f(n\|ast)?a\|ref)$ |
| `optional_data` | string | no |  |  |
| `template` | string (file path) | no |  | matches ^\S+\.txt$ |

`--input` must match `^\S+\.(csv|tsv|yaml|yml|json)$`.

For tabular CSV/TSV input, use this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
id,fasta,reference,optional_data,template
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `align_options` (1 parameter)
- `eval_options` (6 parameters)
- `generic_options` (13 parameters)
- `global_options` (5 parameters)
- `input_output_options` (7 parameters)
- `input_tools_options` (5 parameters)
- `institutional_config_options` (6 parameters)
- `reports_options` (4 parameters)
- `stats_options` (4 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/multiplesequencealign/blob/1.1.1/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: 3DCoffee, ClustalO, csvtk, FAMSA, FoldMason, Kalign3, learnMSA, MAFFT, MAGUS, MultiQC, mTM-align, Muscle5, T-Coffee, UPP, Biopython.

Full list with references: https://github.com/nf-core/multiplesequencealign/blob/1.1.1/CITATIONS.md

## Demo
```bash
nfclaw run multiplesequencealign --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/multiplesequencealign/blob/1.1.1/docs/usage.md

<!-- Generated from nf-core/multiplesequencealign@79724dac3d240b9bb7684532d3fe238b42f6a4b4. Do not edit by hand. -->
