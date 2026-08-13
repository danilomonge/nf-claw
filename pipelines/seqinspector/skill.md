---
name: seqinspector
pipeline: nf-core/seqinspector
version: 1.1.1
commit: 2b2c69f37f46dc3d1c3ef211aeb14da13295a913
description: Pipeline to QC your sequences
summary: nf-core/seqinspector is a bioinformatics pipeline that processes raw sequence data (FASTQ) to provide comprehensive quality control. It can perform subsampling, quality assessment, duplication level analysis, and complexity evaluation on a per-sample basis, while also detecting adapter content, technical artifacts, and common biological contaminants. The pipeline generates detailed MultiQC reports with flexible output options, ranging from individual sample reports to project-wide summaries, making it particularly useful for sequencing core facilities and research groups with access to sequencing instruments. If provided, nf-core/seqinspector can also parse statistics from an Illumina run folder directory into the final MultiQC reports.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2, rundir, tags)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: BBMap, BWAMEM2, checkQC, Chelae, FastQC, Kraken2, Krona, Fastp, FastQ Screen, FASTQE, FQ, MultiQC, MultiQC SAV, Riker, Picard Tools, Rundirparser, SAMTOOLS, SeqFu, Seqkit, Seqtk, Sequali, ToulligQC, pigz, Python, PyYAML, GNU tar
---
# seqinspector

nf-core/seqinspector is a bioinformatics pipeline that processes raw sequence data (FASTQ) to provide comprehensive quality control. It can perform subsampling, quality assessment, duplication level analysis, and complexity evaluation on a per-sample basis, while also detecting adapter content, technical artifacts, and common biological contaminants. The pipeline generates detailed MultiQC reports with flexible output options, ranging from individual sample reports to project-wide summaries, making it particularly useful for sequencing core facilities and research groups with access to sequencing instruments. If provided, nf-core/seqinspector can also parse statistics from an Illumina run folder directory into the final MultiQC reports.

## Run it
```bash
git submodule update --init pipelines/seqinspector/upstream   # first time only
nfclaw run seqinspector --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/seqinspector/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions seqinspector` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show seqinspector --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | yes |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `rundir` | string | no |  |  |
| `tags` | string | no |  | matches ^([A-Za-z0-9_-]+:)*([A-Za-z0-9_-]+)$ |

`--input` must match `^\S+\.csv$`.

Additional row validation rules from the schema:
- When `fastq_2` is set, also provide `fastq_1`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1
```

Any of the optional columns above may be appended to the header when your data needs them: `fastq_2`, `rundir`, `tags`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Reference genome
No reference genome is set by default: supply your own (the `reference_genome_options` group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`). Passing `--genome <id>` instead resolves the references from AWS iGenomes at `s3://ngi-igenomes/igenomes/`, which needs access to that bucket and downloads them. Set `--igenomes-ignore true` to disable the lookup entirely.

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **BBMap options** (`bbmap_options`) — 2 parameters
- **Generic options** (`generic_options`) — 16 parameters
- **Input/output options** (`input_output_options`) — 9 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Kraken2 options** (`kraken2_options`) — 4 parameters
- **Reference genome options** (`reference_genome_options`) — 10 parameters
- **Riker options** (`riker_options`) — 1 parameter
- **Validation options** (`validation_options`) — 3 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run seqinspector --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.10.4'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run seqinspector ... --nxf-ver 25.10.4
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/seqinspector/blob/1.1.1/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: BBMap, BWAMEM2, checkQC, Chelae, FastQC, Kraken2, Krona, Fastp, FastQ Screen, FASTQE, FQ, MultiQC, MultiQC SAV, Riker, Picard Tools, Rundirparser, SAMTOOLS, SeqFu, Seqkit, Seqtk, Sequali, ToulligQC, pigz, Python, PyYAML, GNU tar.

Full list with references: https://github.com/nf-core/seqinspector/blob/1.1.1/CITATIONS.md

## Demo
```bash
nfclaw run seqinspector --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/seqinspector/blob/1.1.1/docs/usage.md

<!-- Generated from nf-core/seqinspector@2b2c69f37f46dc3d1c3ef211aeb14da13295a913. Do not edit by hand. -->
