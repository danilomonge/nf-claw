---
name: nanoseq
pipeline: nf-core/nanoseq
version: 3.1.0
commit: 6e563e54362cddb8e48d15c156251708c22d0e8d
description: A pipeline to demultiplex, QC and map Nanopore data
summary: nfcore/nanoseq is a bioinformatics analysis pipeline for Nanopore DNA/RNA sequencing data that can be used to perform basecalling, demultiplexing, QC, alignment, and downstream analysis.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: bambu, BEDTools, cuteSV, DeepVariant, featureCounts, GraphMap, JAFFAL, m6anet, PEPPER-Margin-DeepVariant, Minimap2, Medaka, MultiQC, NanoLyse, NanoPlot, qcat, SAMtools, Sniffles, StringTie2, UCSC tools, xPore, R, BSgenome, DESeq2, DEXSeq, DRIMSeq, stageR
---
# nanoseq

nfcore/nanoseq is a bioinformatics analysis pipeline for Nanopore DNA/RNA sequencing data that can be used to perform basecalling, demultiplexing, QC, alignment, and downstream analysis.

## Run it
```bash
git submodule update --init pipelines/nanoseq/upstream   # first time only
nfclaw run nanoseq --input samplesheet.csv --outdir results --protocol <protocol> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/nanoseq/upstream -profile docker --input samplesheet.csv --outdir results --protocol <protocol>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions nanoseq` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show nanoseq --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string | no |  |  |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) | ./samplesheet.csv |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--protocol` | string |  |  |  | Input sample type. Valid options: 'DNA', 'cDNA', and 'directRNA'. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `alignment_options` (4 parameters)
- `demultiplexing_options` (11 parameters)
- `differential_analysis_options` (3 parameters)
- `generic_options` (11 parameters)
- `input_output_options` (5 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)
- `process_skipping_options` (6 parameters)
- `reference_genome_options` (2 parameters)
- `rna_fusion_analysis_options` (2 parameters)
- `rna_modification_analysis_options` (3 parameters)
- `variant_calling_options` (8 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/nanoseq/blob/3.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: bambu, BEDTools, cuteSV, DeepVariant, featureCounts, GraphMap, JAFFAL, m6anet, PEPPER-Margin-DeepVariant, Minimap2, Medaka, MultiQC, NanoLyse, NanoPlot, qcat, SAMtools, Sniffles, StringTie2, UCSC tools, xPore, R, BSgenome, DESeq2, DEXSeq, DRIMSeq, stageR.

Full list with references: https://github.com/nf-core/nanoseq/blob/3.1.0/CITATIONS.md

## Demo
```bash
nfclaw run nanoseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/nanoseq/blob/3.1.0/docs/usage.md

<!-- Generated from nf-core/nanoseq@6e563e54362cddb8e48d15c156251708c22d0e8d. Do not edit by hand. -->
