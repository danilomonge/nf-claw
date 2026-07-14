---
name: airrflow
pipeline: nf-core/airrflow
version: 5.1.0
commit: e69d49e3f23f11a3391755b5fb7aa4283c0a2471
description: B and T cell repertoire analysis pipeline with the Immcantation framework.
summary: nf-core/airrflow is a bioinformatics best-practice pipeline to analyze B-cell receptor (BCR) or T-cell receptor (TCR) repertoire sequencing data. It allows the processing of targeted bulk and single-cell adaptive immune receptor sequencing data (AIRR-seq), as well as the extraction of TCR and BCR sequences from untargeted bulk and single-cell RNA-seq data. The pipeline enables an end-to-end analysis, departing from raw reads or assembled sequences, and performs sequence assembly, V(D)J assignment, novel allele identification, genotype inference, clonal inference, repertoire analysis, lineage reconstruction and BCR/TCR sequence embedding using the Immcantation framework, as well as other immune repertoire analysis tools.
has_samplesheet: true
input: samplesheet (sample_id, subject_id, species, pcr_target_locus, tissue, sex, age, biomaterial_provider, single_cell, filename_R1, filename_R2, filename_I1, filename)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, Fastp, pRESTO, SHazaM, Change-O, IgBLAST, Alakazam, SCOPer, Dowser, IgPhyML, RAxML, MultiQC
---
# airrflow

nf-core/airrflow is a bioinformatics best-practice pipeline to analyze B-cell receptor (BCR) or T-cell receptor (TCR) repertoire sequencing data. It allows the processing of targeted bulk and single-cell adaptive immune receptor sequencing data (AIRR-seq), as well as the extraction of TCR and BCR sequences from untargeted bulk and single-cell RNA-seq data. The pipeline enables an end-to-end analysis, departing from raw reads or assembled sequences, and performs sequence assembly, V(D)J assignment, novel allele identification, genotype inference, clonal inference, repertoire analysis, lineage reconstruction and BCR/TCR sequence embedding using the Immcantation framework, as well as other immune repertoire analysis tools.

## Run it
```bash
git submodule update --init pipelines/airrflow/upstream   # first time only
nfclaw run airrflow --input samplesheet.tsv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/airrflow/upstream -profile docker --input samplesheet.tsv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions airrflow` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show airrflow --pipeline-version X.Y.Z` prints that release's docs).

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

`--input` must match `^\S+\.tsv$`.

The samplesheet is a TSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```tsv
sample_id	subject_id	species	pcr_target_locus	tissue	sex	age	biomaterial_provider	single_cell
```

Any of the optional columns above may be appended to the header when your data needs them: `filename_R1`, `filename_R2`, `filename_I1`, `filename`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.tsv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Reference genome
No reference genome is set by default: supply your own (the `reference_genome_options` group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`). Passing `--genome <id>` instead resolves the references from AWS iGenomes at `s3://ngi-igenomes/igenomes/`, which needs access to that bucket and downloads them. Set `--igenomes-ignore true` to disable the lookup entirely.

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Adapter trimming** (`adapter_trimming`) — 8 parameters
- **Bulk filtering options** (`bulk_filtering_options`) — 3 parameters
- **Clonal analysis options** (`clonal_analysis_options`) — 10 parameters
- **Generic options** (`generic_options`) — 16 parameters
- **Genotyping and Novel Alleles options** (`genotyping_and_novel_alleles_options`) — 5 parameters
- **Input output options** (`input_output_options`) — 5 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Primer input and positions** (`primer_input_and_positions`) — 6 parameters
- **Protocol** (`protocol`) — 2 parameters
- **Reference genome options** (`reference_genome_options`) — 2 parameters
- **Report options** (`report_options`) — 6 parameters
- **Untargeted RNA-seq based analysis options** (`rnaseq_based_analysis_options`) — 4 parameters
- **Sequence Assembly options** (`sequence_assembly_options`) — 22 parameters
- **Single cell analysis options** (`single_cell_analysis_options`) — 1 parameter
- **Translation and embedding options** (`translation_and_embedding_options`) — 4 parameters
- **UMI barcode handling** (`umi_barcode_handling`) — 4 parameters
- **VDJ annotation options** (`vdj_annotation_options`) — 6 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run airrflow --input samplesheet.tsv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=26.04.1'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run airrflow ... --nxf-ver 26.04.1
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

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
