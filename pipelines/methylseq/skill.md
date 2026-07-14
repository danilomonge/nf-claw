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

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1
```

Any of the optional columns above may be appended to the header when your data needs them: `fastq_2`, `genome`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--aligner` | string | bismark | bismark, bismark_hisat, bwameth, bwamem |  | Alignment tool to use. |

## Reference genome
No reference genome is set by default: supply your own (the `reference_genome_options` group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`). Passing `--genome <id>` instead resolves the references from AWS iGenomes at `s3://ngi-igenomes/igenomes/`, which needs access to that bucket and downloads them. Set `--igenomes-ignore true` to disable the lookup entirely.

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Adapter Trimming** (`adapter_trimming`) — 7 parameters
- **Alignment options** (`alignment_options`) — 2 parameters
- **Bismark options** (`bismark_options`) — 16 parameters
- **Generic options** (`generic_options`) — 16 parameters
- **Input/output options** (`input_output_options`) — 4 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **MethylDackel options** (`methyldackel_options`) — 5 parameters
- **Qualimap Options** (`qualimap_options`) — 1 parameter
- **rastair options** (`rastair_options`) — 2 parameters
- **Reference genome options** (`reference_genome_options`) — 8 parameters
- **Run pipeline steps** (`run_pipeline_steps`) — 3 parameters
- **Save intermediate files** (`save_intermediate_files`) — 4 parameters
- **Skip pipeline steps** (`skip_pipeline_steps`) — 4 parameters
- **Special library types** (`special_library_types`) — 8 parameters
- **Targeted Sequencing Analysis Options** (`targeted_sequencing_analysis_options`) — 2 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run methylseq --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.04.0'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run methylseq ... --nxf-ver 25.04.0
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

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
