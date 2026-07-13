---
name: hlatyping
pipeline: nf-core/hlatyping
version: 2.2.0
commit: 3237d20e7e611d8bbf8c37e637202dfe8a23e996
description: Precision HLA typing from next-generation sequencing data.
summary: nf-core/hlatyping is a bioinformatics pipeline that can be used to perform HLA typing from next-generation sequencing data. The pipeline does next-generation sequencing-based Human Leukocyte Antigen (HLA) typing using OptiType. OptiType is a HLA genotyping algorithm based on integer linear programming. Reads of whole exome/genome/transcriptome sequencing data are mapped against a reference of known MHC class I alleles. To produce accurate 4-digit HLA genotyping predictions, all major and minor HLA-I loci are considered simultaneously to find an allele combination that maximizes the number of explained reads.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2, bam, seq_type)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, SAMtools, Yara, OptiType, HLA-HD, MultiQC
---
# hlatyping

nf-core/hlatyping is a bioinformatics pipeline that can be used to perform HLA typing from next-generation sequencing data. The pipeline does next-generation sequencing-based Human Leukocyte Antigen (HLA) typing using OptiType. OptiType is a HLA genotyping algorithm based on integer linear programming. Reads of whole exome/genome/transcriptome sequencing data are mapped against a reference of known MHC class I alleles. To produce accurate 4-digit HLA genotyping predictions, all major and minor HLA-I loci are considered simultaneously to find an allele combination that maximizes the number of explained reads.

## Run it
```bash
git submodule update --init pipelines/hlatyping/upstream   # first time only
nfclaw run hlatyping --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/hlatyping/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions hlatyping` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show hlatyping --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `bam` | string (file path) | no |  | matches ^\S+\.bam$ |
| `seq_type` | string | yes | dna, rna |  |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,seq_type
```

Any of the optional columns above may be appended to the header when your data needs them: `fastq_1`, `fastq_2`, `bam`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Generic options** (`generic_options`) — 16 parameters
- **HLA-HD options** (`hlahd_options`) — 2 parameters
- **HLA typing options** (`hlatyping_options`) — 1 parameter
- **Input/output options** (`input_output_options`) — 3 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Optional outputs** (`optional_outputs`) — 1 parameter
- **OptiType Optimisation steps** (`optitype_optimisation_steps`) — 4 parameters
- **Reference genome options** (`reference_genome_options`) — 3 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run hlatyping --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/hlatyping/blob/2.2.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, SAMtools, Yara, OptiType, HLA-HD, MultiQC.

Full list with references: https://github.com/nf-core/hlatyping/blob/2.2.0/CITATIONS.md

## Demo
```bash
nfclaw run hlatyping --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/hlatyping/blob/2.2.0/docs/usage.md

<!-- Generated from nf-core/hlatyping@3237d20e7e611d8bbf8c37e637202dfe8a23e996. Do not edit by hand. -->
