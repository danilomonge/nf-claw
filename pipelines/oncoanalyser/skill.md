---
name: oncoanalyser
pipeline: nf-core/oncoanalyser
version: 2.3.0
commit: 234fd82acc16a3beb01bf301900d83346b6ec812
description: A comprehensive cancer DNA/RNA analysis and reporting pipeline
summary: nf-core/oncoanalyser is a Nextflow pipeline for the comprehensive analysis of cancer DNA and RNA sequencing data using the WiGiTS toolkit from the Hartwig Medical Foundation. The pipeline supports a wide range of experimental setups:
has_samplesheet: true
input: samplesheet (group_id, subject_id, sample_id, sample_type, sequence_type, info, filetype, filepath)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions)
tools: BCFtools, BWA, bwa-mem2, CHORD, fastp, GATK, GRIDSS2, LILAC, LINX, PURPLE, Sambamba, SAMtools, STAR, VIRUSBreakend
---
# oncoanalyser

nf-core/oncoanalyser is a Nextflow pipeline for the comprehensive analysis of cancer DNA and RNA sequencing data using the WiGiTS toolkit from the Hartwig Medical Foundation. The pipeline supports a wide range of experimental setups:

## Run it
```bash
git submodule update --init pipelines/oncoanalyser/upstream   # first time only
nfclaw run oncoanalyser --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/oncoanalyser/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions oncoanalyser` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show oncoanalyser --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `group_id` | string | yes |  | matches ^\S+$ |
| `subject_id` | string | yes |  | matches ^\S+$ |
| `sample_id` | string | yes |  | matches ^\S+$ |
| `sample_type` | string | yes | normal, tumor, donor, tumor_normal | matches ^\S+$ |
| `sequence_type` | string | yes | dna, rna, dna_rna | matches ^\S+$ |
| `info` | string | no |  | matches ^\S+$ |
| `filetype` | string | yes |  | matches ^\S+$ |
| `filepath` | string | yes |  | matches ^\S+$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
group_id,subject_id,sample_id,sample_type,sequence_type,info,filetype,filepath
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `generic_options` (12 parameters)
- `input_output_options` (2 parameters)
- `institutional_config_options` (6 parameters)
- `other_options` (28 parameters)
- `reference_data_options` (17 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/oncoanalyser/blob/2.3.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: BCFtools, BWA, bwa-mem2, CHORD, fastp, GATK, GRIDSS2, LILAC, LINX, PURPLE, Sambamba, SAMtools, STAR, VIRUSBreakend.

Full list with references: https://github.com/nf-core/oncoanalyser/blob/2.3.0/CITATIONS.md

## Demo
```bash
nfclaw run oncoanalyser --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/oncoanalyser/blob/2.3.0/docs/usage.md

<!-- Generated from nf-core/oncoanalyser@234fd82acc16a3beb01bf301900d83346b6ec812. Do not edit by hand. -->
