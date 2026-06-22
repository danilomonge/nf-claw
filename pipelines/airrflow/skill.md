---
name: airrflow
pipeline: nf-core/airrflow
version: 5.1.0
commit: e69d49e3f23f11a3391755b5fb7aa4283c0a2471
description: B and T cell repertoire analysis pipeline with the Immcantation framework.
has_samplesheet: true
input: samplesheet (sample_id, subject_id, species, pcr_target_locus, tissue, sex, age, biomaterial_provider, single_cell, filename_R1, filename_R2, filename_I1, filename)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, Fastp, pRESTO, SHazaM, Change-O, IgBLAST, Alakazam, SCOPer, Dowser, IgPhyML, RAxML, MultiQC
---
# airrflow

B and T cell repertoire analysis pipeline with the Immcantation framework.

## Run it
```bash
git submodule update --init pipelines/airrflow/upstream   # first time only
nfclaw run airrflow --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/airrflow/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample_id` | string or number | yes |  | matches ^\S+$ |
| `subject_id` | string or number | yes |  | matches ^\S+$ |
| `species` | string | yes | mouse, human |  |
| `pcr_target_locus` | string | yes | TR, IG, ig, tr, Ig, Tr |  |
| `tissue` | string | yes |  |  |
| `sex` | string | yes |  |  |
| `age` | string or number | yes |  |  |
| `biomaterial_provider` | string | yes |  |  |
| `single_cell` | boolean | yes |  | matches ^\S+$ |
| `filename_R1` | string | no |  | matches ^\S+$ |
| `filename_R2` | string | no |  | matches ^\S+$ |
| `filename_I1` | string | no |  | matches ^\S+$ |
| `filename` | string | no |  | matches ^\S+$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample_id,subject_id,species,pcr_target_locus,tissue,sex,age,biomaterial_provider,single_cell,filename_R1,filename_R2,filename_I1,filename
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.tsv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `adapter_trimming` (8 parameters)
- `bulk_filtering_options` (3 parameters)
- `clonal_analysis_options` (10 parameters)
- `generic_options` (16 parameters)
- `genotyping_and_novel_alleles_options` (5 parameters)
- `input_output_options` (5 parameters)
- `institutional_config_options` (6 parameters)
- `primer_input_and_positions` (6 parameters)
- `protocol` (2 parameters)
- `reference_genome_options` (2 parameters)
- `report_options` (6 parameters)
- `rnaseq_based_analysis_options` (4 parameters)
- `sequence_assembly_options` (22 parameters)
- `single_cell_analysis_options` (1 parameter)
- `translation_and_embedding_options` (4 parameters)
- `umi_barcode_handling` (4 parameters)
- `vdj_annotation_options` (6 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/airrflow/blob/5.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, Fastp, pRESTO, SHazaM, Change-O, IgBLAST, Alakazam, SCOPer, Dowser, IgPhyML, RAxML, MultiQC.

Full list with references: https://github.com/nf-core/airrflow/blob/5.1.0/CITATIONS.md

## Demo
```bash
nfclaw run airrflow --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/airrflow/blob/5.1.0/docs/usage.md

<!-- Generated from nf-core/airrflow@e69d49e3f23f11a3391755b5fb7aa4283c0a2471. Do not edit by hand. -->
