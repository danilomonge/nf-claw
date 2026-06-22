---
name: crisprseq
pipeline: nf-core/crisprseq
version: 2.3.0
commit: 0e9f915c4a3c89d02a66ec58e2decbc832323c8b
description: Pipeline for the analysis of CRISPR data
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2, condition, reference, protospacer, template)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, MultiQC, Pear, Seqtk, Bowtie2, BWA, Minimap2, Cutadapt, Samtools, MAGeCKFlute
---
# crisprseq

Pipeline for the analysis of CRISPR data

## Run it
```bash
git submodule update --init pipelines/crisprseq/upstream   # first time only
nfclaw run crisprseq --input samplesheet.csv --outdir results --analysis <analysis> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/crisprseq/upstream -profile docker --input samplesheet.csv --outdir results --analysis <analysis>
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `condition` | string | no |  | matches ^\S+$ |
| `reference` | string | no |  | matches ^[ACTGNactgn]+$ |
| `protospacer` | string | no |  | matches ^[ACTGNactgn]+$ |
| `template` | string | no |  | matches ^[ACTGNactgn]+$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2,condition,reference,protospacer,template
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--analysis` | string | screening, targeted |  | Type of analysis to perform. Targeted for targeted CRISPR experiments and screening for CRISPR screening experiments. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `generic_options` (12 parameters)
- `input_output_options` (5 parameters)
- `institutional_config_options` (6 parameters)
- `reference_genome_options` (4 parameters)
- `screening_parameters` (21 parameters)
- `targeted_parameters` (2 parameters)
- `targeted_pipeline_steps` (3 parameters)
- `umi_parameters` (2 parameters)
- `vsearch_parameters` (3 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/crisprseq/blob/2.3.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, MultiQC, Pear, Seqtk, Bowtie2, BWA, Minimap2, Cutadapt, Samtools, MAGeCKFlute.

Full list with references: https://github.com/nf-core/crisprseq/blob/2.3.0/CITATIONS.md

## Demo
```bash
nfclaw run crisprseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/crisprseq/blob/2.3.0/docs/usage.md

<!-- Generated from nf-core/crisprseq@0e9f915c4a3c89d02a66ec58e2decbc832323c8b. Do not edit by hand. -->
