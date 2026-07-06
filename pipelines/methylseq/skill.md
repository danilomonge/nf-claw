---
name: methylseq
pipeline: nf-core/methylseq
version: 4.2.0
commit: 5aa56467a85a5e2d6795ea72dfa5a5f0c9babc23
description: Methylation (Bisulfite-Sequencing) Best Practice analysis pipeline, part of the nf-core community.
summary: nf-core/methylseq is a bioinformatics analysis pipeline used for Methylation (Bisulfite) sequencing data. It pre-processes raw data from FastQ inputs, aligns the reads and performs extensive quality-control on the results.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2, genome)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, MultiQC, Trim Galore!, Bismark, BWA-MEM, bwa-meth, Picard, Qualimap, Preseq, rastair, Samtools, Bedtools
---
# methylseq

nf-core/methylseq is a bioinformatics analysis pipeline used for Methylation (Bisulfite) sequencing data. It pre-processes raw data from FastQ inputs, aligns the reads and performs extensive quality-control on the results.

## Run it
```bash
git submodule update --init pipelines/methylseq/upstream   # first time only
nfclaw run methylseq --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/methylseq/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions methylseq` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show methylseq --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `genome` | string (file path) | no |  | matches ^[a-zA-Z0-9._-]+$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2,genome
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--aligner` | string | bismark | bismark, bismark_hisat, bwameth, bwamem |  | Alignment tool to use. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `adapter_trimming` (7 parameters)
- `alignment_options` (2 parameters)
- `bismark_options` (16 parameters)
- `generic_options` (16 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `methyldackel_options` (5 parameters)
- `qualimap_options` (1 parameter)
- `rastair_options` (2 parameters)
- `reference_genome_options` (8 parameters)
- `run_pipeline_steps` (3 parameters)
- `save_intermediate_files` (4 parameters)
- `skip_pipeline_steps` (4 parameters)
- `special_library_types` (8 parameters)
- `targeted_sequencing_analysis_options` (2 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/methylseq/blob/4.2.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, MultiQC, Trim Galore!, Bismark, BWA-MEM, bwa-meth, Picard, Qualimap, Preseq, rastair, Samtools, Bedtools.

Full list with references: https://github.com/nf-core/methylseq/blob/4.2.0/CITATIONS.md

## Demo
```bash
nfclaw run methylseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/methylseq/blob/4.2.0/docs/usage.md

<!-- Generated from nf-core/methylseq@5aa56467a85a5e2d6795ea72dfa5a5f0c9babc23. Do not edit by hand. -->
