---
name: rnasplice
pipeline: nf-core/rnasplice
version: 1.0.4
commit: 1d0494ae3402d1a46e0adadad24f81a0ff855c77
description: Alternative splicing analysis using RNA-seq.
summary: nf-core/rnasplice is a bioinformatics pipeline for alternative splicing analysis of RNA sequencing data obtained from organisms with a reference genome and annotation.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2, strandedness, condition)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: BEDTools, FastQC, featureCounts, gffread, HTSeq, MISO, MultiQC, rMats, RSEM, Salmon, SAMtools, STAR, SUPPA2, Trim Galore!, UCSC tools, R, DEXSeq, DRIMSeq, edgeR, StageR, tximport
---
# rnasplice

nf-core/rnasplice is a bioinformatics pipeline for alternative splicing analysis of RNA sequencing data obtained from organisms with a reference genome and annotation.

## Run it
```bash
git submodule update --init pipelines/rnasplice/upstream   # first time only
nfclaw run rnasplice --input samplesheet.csv --outdir results --contrasts <contrasts> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/rnasplice/upstream -profile docker --input samplesheet.csv --outdir results --contrasts <contrasts>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions rnasplice` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show rnasplice --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string | no |  |  |
| `strandedness` | string | yes | forward, reverse, unstranded |  |
| `condition` | string | yes |  | matches ^\S+$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,strandedness,condition
```

Any of the optional columns above may be appended to the header when your data needs them: `fastq_2`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--contrasts` | string |  |  |  | Path to comma-separated file containing information about the contrasts in the experiment. |
| `--source` | string | fastq | fastq, genome_bam, transcriptome_bam, salmon_results |  | Source of input files. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Reference genome
No reference genome is set by default: supply your own (the `reference_genome_options` group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`). Passing `--genome <id>` instead resolves the references from AWS iGenomes at `s3://ngi-igenomes/igenomes`, which needs access to that bucket and downloads them. Set `--igenomes-ignore true` to disable the lookup entirely.

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Alignment options** (`alignment_options`) — 9 parameters
- **DEXSeq DEU options** (`dexseq_deu_options`) — 7 parameters
- **DEXSeq DTU options** (`dexseq_dtu_options`) — 8 parameters
- **edgeR DEU options** (`edger_deu_options`) — 3 parameters
- **Generic options** (`generic_options`) — 15 parameters
- **Input/output options** (`input_output_options`) — 7 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Max job request options** (`max_job_request_options`) — 3 parameters
- **Miso** (`miso`) — 6 parameters
- **QC options** (`qc_options`) — 2 parameters
- **Read trimming options** (`read_trimming_options`) — 9 parameters
- **Reference genome options** (`reference_genome_options`) — 13 parameters
- **rMATS options** (`rmats_options`) — 7 parameters
- **SUPPA options** (`suppa_options`) — 30 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run rnasplice --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=23.04.0'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run rnasplice ... --nxf-ver 23.04.0
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/rnasplice/blob/1.0.4/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: BEDTools, FastQC, featureCounts, gffread, HTSeq, MISO, MultiQC, rMats, RSEM, Salmon, SAMtools, STAR, SUPPA2, Trim Galore!, UCSC tools, R, DEXSeq, DRIMSeq, edgeR, StageR, tximport.

Full list with references: https://github.com/nf-core/rnasplice/blob/1.0.4/CITATIONS.md

## Demo
```bash
nfclaw run rnasplice --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/rnasplice/blob/1.0.4/docs/usage.md

<!-- Generated from nf-core/rnasplice@1d0494ae3402d1a46e0adadad24f81a0ff855c77. Do not edit by hand. -->
