---
name: taxprofiler
pipeline: nf-core/taxprofiler
version: 2.0.1
commit: 70ecc15e49b4f1fcf79d876643b5d14b65c66178
description: Taxonomic classification and profiling of shotgun short- and long-read metagenomic data
summary: nf-core/taxprofiler is a bioinformatics best-practice analysis pipeline for taxonomic classification and profiling of shotgun short- and long-read metagenomic data. It allows for in-parallel taxonomic identification of reads or taxonomic abundance estimation with multiple classification and profiling tools against multiple databases, and produces standardised output tables for facilitating results comparison between different tools and databases.
has_samplesheet: true
input: samplesheet (sample, run_accession, instrument_platform, fastq_1, fastq_2, fasta)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, MultiQC, falco, fastp, AdapterRemoval2, Nonpareil, Porechop, Porechop_ABI, Filtlong, nanoq, BBTools, PRINSEQ++, Bowtie2, minimap2, SAMTools, Bracken, Kraken2, KrakenUniq, MetaPhlAn, MALT, MEGAN, DIAMOND, Centrifuge, Kaiju, mOTUs, KMCP, ganon, melon, Krona, TAXPASTA, sylph, MetaCache
---
# taxprofiler

nf-core/taxprofiler is a bioinformatics best-practice analysis pipeline for taxonomic classification and profiling of shotgun short- and long-read metagenomic data. It allows for in-parallel taxonomic identification of reads or taxonomic abundance estimation with multiple classification and profiling tools against multiple databases, and produces standardised output tables for facilitating results comparison between different tools and databases.

## Run it
```bash
git submodule update --init pipelines/taxprofiler/upstream   # first time only
nfclaw run taxprofiler --input samplesheet.csv --outdir results --databases <databases> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/taxprofiler/upstream -profile docker --input samplesheet.csv --outdir results --databases <databases>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions taxprofiler` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show taxprofiler --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string or integer | yes |  | matches ^[^\s]+$ |
| `run_accession` | string or integer | yes |  | matches ^[^\s]+$ |
| `instrument_platform` | string | yes | ABI_SOLID, BGISEQ, CAPILLARY, COMPLETE_GENOMICS, DNBSEQ, HELICOS, ILLUMINA, ION_TORRENT, LS454, OXFORD_NANOPORE, PACBIO_SMRT |  |
| `fastq_1` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fasta` | string (file path) | no |  | matches ^\S+\.(fasta\|fas\|fna\|fa)\.gz?$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,run_accession,instrument_platform
```

Any of the optional columns above may be appended to the header when your data needs them: `fastq_1`, `fastq_2`, `fasta`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples and libraries/runs. |
| `--databases` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about databases and profiling parameters for each taxonomic profiler |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Generic options** (`generic_options`) — 15 parameters
- **Input/output options** (`input_output_options`) — 6 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Postprocessing and visualisation options** (`postprocessing_and_visualisation_options`) — 12 parameters
- **Preprocessing general QC options** (`preprocessing_general_qc_options`) — 4 parameters
- **Preprocessing host removal options** (`preprocessing_host_removal_options`) — 8 parameters
- **Preprocessing long-read QC options** (`preprocessing_long_read_qc_options`) — 11 parameters
- **Preprocessing run merging options** (`preprocessing_run_merging_options`) — 2 parameters
- **Preprocessing short-read QC options** (`preprocessing_short_read_qc_options`) — 19 parameters
- **Profiling options** (`profiling_options`) — 48 parameters
- **Redundancy Estimation** (`redundancy_estimation`) — 2 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run taxprofiler --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.10.4'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run taxprofiler ... --nxf-ver 25.10.4
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/taxprofiler/blob/2.0.1/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, MultiQC, falco, fastp, AdapterRemoval2, Nonpareil, Porechop, Porechop_ABI, Filtlong, nanoq, BBTools, PRINSEQ++, Bowtie2, minimap2, SAMTools, Bracken, Kraken2, KrakenUniq, MetaPhlAn, MALT, MEGAN, DIAMOND, Centrifuge, Kaiju, mOTUs, KMCP, ganon, melon, Krona, TAXPASTA, sylph, MetaCache.

Full list with references: https://github.com/nf-core/taxprofiler/blob/2.0.1/CITATIONS.md

## Demo
```bash
nfclaw run taxprofiler --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/taxprofiler/blob/2.0.1/docs/usage.md

<!-- Generated from nf-core/taxprofiler@70ecc15e49b4f1fcf79d876643b5d14b65c66178. Do not edit by hand. -->
