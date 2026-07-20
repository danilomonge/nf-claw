---
name: riboseq
pipeline: nf-core/riboseq
version: 1.2.0
commit: 74ab1ea2668ee9a221a5c96c86b2a6ee1b2d2f2f
description: Analysis of ribosome profiling, or Ribo-seq (also named ribosome footprinting)
summary: nf-core/riboseq is a bioinformatics pipeline for analysis of Ribo-seq data. It borrows heavily from nf-core/rnaseq in the preprocessing stages:
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2, strandedness, type)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: anota2seq, BBMap, BEDTools, fastp, FastQC, MultiQC, Ribo-TISH, Ribotricer, riboWaltz, SortMeRNA, STAR, Trim Galore!, UMI-tools
---
# riboseq

nf-core/riboseq is a bioinformatics pipeline for analysis of Ribo-seq data. It borrows heavily from nf-core/rnaseq in the preprocessing stages:

## Run it
```bash
git submodule update --init pipelines/riboseq/upstream   # first time only
nfclaw run riboseq --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/riboseq/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions riboseq` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show riboseq --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `strandedness` | string | yes | forward, reverse, unstranded, auto |  |
| `type` | string | yes | riboseq, rnaseq, tiseq |  |

`--input` must match `^\S+\.(csv|tsv|json|yaml|yml)$`.

For tabular CSV/TSV input, use this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,strandedness,type
```

Any of the optional columns above may be appended to the header when your data needs them: `fastq_2`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.(csv\|tsv\|json\|yaml\|yml)$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Reference genome
No reference genome is set by default: supply your own (the `reference_genome_options` group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`). Passing `--genome <id>` instead resolves the references from AWS iGenomes at `s3://ngi-igenomes/igenomes/`, which needs access to that bucket and downloads them. Set `--igenomes-ignore true` to disable the lookup entirely.

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- `general` — 1 parameter
- **Alignment options** (`alignment_options`) — 11 parameters
- **Generic options** (`generic_options`) — 16 parameters
- **Input/output options** (`input_output_options`) — 5 parameters
- **Institutional config options** (`institutional_config_options`) — 7 parameters
- **Optional outputs** (`optional_outputs`) — 8 parameters
- **Process skipping options** (`process_skipping_options`) — 14 parameters
- **Read filtering options** (`read_filtering_options`) — 6 parameters
- **Read trimming options** (`read_trimming_options`) — 4 parameters
- **Reference genome options** (`reference_genome_options`) — 13 parameters
- **Riboseq-specific options** (`riboseq_specific_options`) — 6 parameters
- **UMI options** (`umi_options`) — 9 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run riboseq --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.04.8'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run riboseq ... --nxf-ver 25.04.8
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/riboseq/blob/1.2.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: anota2seq, BBMap, BEDTools, fastp, FastQC, MultiQC, Ribo-TISH, Ribotricer, riboWaltz, SortMeRNA, STAR, Trim Galore!, UMI-tools.

Full list with references: https://github.com/nf-core/riboseq/blob/1.2.0/CITATIONS.md

## Demo
```bash
nfclaw run riboseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/riboseq/blob/1.2.0/docs/usage.md

<!-- Generated from nf-core/riboseq@74ab1ea2668ee9a221a5c96c86b2a6ee1b2d2f2f. Do not edit by hand. -->
