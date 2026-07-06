---
name: nascent
pipeline: nf-core/nascent
version: 2.3.0
commit: 7d4fe61975015f652c271886e661764b05cfd3bf
description: Global Run-On sequencing analysis pipeline
summary: nf-core/nascent is a bioinformatics best-practice analysis pipeline for nascent transcript (NT) and Transcriptional Start Site (TSS) assays.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: BBMap, BEDTools, Bowtie 2, BWA-MEM, BWA-MEM2, deepTools, DragMap, FastP, FastQC, MultiQC, featureCounts, GffRead, HISAT2, HOMER, PINTS, preseq, RSeQC, SAMtools, STAR, UMI-tools, Pandas, R, argparse, GenomicAlignments, GenomicFeatures, groHMM
---
# nascent

nf-core/nascent is a bioinformatics best-practice analysis pipeline for nascent transcript (NT) and Transcriptional Start Site (TSS) assays.

## Run it
```bash
git submodule update --init pipelines/nascent/upstream   # first time only
nfclaw run nascent --input samplesheet.csv --outdir results --assay-type <assay_type> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/nascent/upstream -profile docker --input samplesheet.csv --outdir results --assay-type <assay_type>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions nascent` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show nascent --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--assay-type` | string |  | CoPRO, GROcap, PROcap, CAGE, NETCAGE, RAMPAGE, csRNAseq, STRIPEseq, PROseq, GROseq, R_5, R_3, R1_5, R1_3, R2_5, R2_3 |  | What type of nascent or TSS assay the sample is. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `alignment_options` (3 parameters)
- `generic_options` (13 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `reference_genome_options` (16 parameters)
- `transcript_identification_options` (9 parameters)
- `umi_options` (2 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/nascent/blob/2.3.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: BBMap, BEDTools, Bowtie 2, BWA-MEM, BWA-MEM2, deepTools, DragMap, FastP, FastQC, MultiQC, featureCounts, GffRead, HISAT2, HOMER, PINTS, preseq, RSeQC, SAMtools, STAR, UMI-tools, Pandas, R, argparse, GenomicAlignments, GenomicFeatures, groHMM.

Full list with references: https://github.com/nf-core/nascent/blob/2.3.0/CITATIONS.md

## Demo
```bash
nfclaw run nascent --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/nascent/blob/2.3.0/docs/usage.md

<!-- Generated from nf-core/nascent@7d4fe61975015f652c271886e661764b05cfd3bf. Do not edit by hand. -->
