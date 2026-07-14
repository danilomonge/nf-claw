---
name: mag
pipeline: nf-core/mag
version: 5.4.2
commit: 5dabb0159ac0104885e09f301db22126e8fcb394
description: Assembly, binning and annotation of metagenomes
summary: nf-core/mag is a bioinformatics best-practice analysis pipeline for assembly, binning and annotation of metagenomes.
has_samplesheet: true
input: samplesheet (sample, run, group, short_reads_1, short_reads_2, short_reads_platform, long_reads, long_reads_platform)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: AdapterRemoval2, ALE, BBnorm/BBTools, BCFtools, Bowtie2, BUSCO, CAT, CheckM, CheckM2, Chopper, COMEBin, CONCOCT, MetaBinner, SemiBin2, DAS Tool, FastP, FastQC, Filtlong, Flye, Freebayes, geNomad, GTDB-Tk, GUNC, BIgMAG, MaxBin2, MEGAHIT, MetaBAT2, MetaEuk, metaMDBG, minimap2, MMseqs2, MultiQC, NanoLyse, NanoPlot, Nanoq, Porechop, Porechop-abi, Prodigal, Prokka, PyDamage, SAMtools, Seqtk, SPAdes, Tiara, Trimmomatic
---
# mag

nf-core/mag is a bioinformatics best-practice analysis pipeline for assembly, binning and annotation of metagenomes.

## Run it
```bash
git submodule update --init pipelines/mag/upstream   # first time only
nfclaw run mag --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/mag/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions mag` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show mag --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `run` | string or integer | no |  | matches ^\S+$ |
| `group` | string or integer | yes |  | matches ^\S+$ |
| `short_reads_1` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `short_reads_2` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `short_reads_platform` | string | no | ILLUMINA, BGISEQ, LS454, ION_TORRENT, DNBSEQ, ELEMENT, ULTIMA, VELA_DIAGNOSTICS, GENAPSYS, GENEMIND, TAPESTRI |  |
| `long_reads` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `long_reads_platform` | string | no | OXFORD_NANOPORE, OXFORD_NANOPORE_HQ, PACBIO_CLR, PACBIO_HIFI |  |

`--input` must match `^\S+\.csv$`.

Additional row validation rules from the schema:
- When `short_reads_2` is set, also provide `short_reads_1`.
- When `short_reads_1` is set, also provide `short_reads_platform`.
- When `long_reads` is set, also provide `long_reads_platform`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,group
```

Any of the optional columns above may be appended to the header when your data needs them: `run`, `short_reads_1`, `short_reads_2`, `short_reads_platform`, `long_reads`, `long_reads_platform`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | CSV samplesheet file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Reference genome
No reference genome is set by default: supply your own (the `reference_genome_options` group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`). Passing `--genome <id>` instead resolves the references from AWS iGenomes at `s3://ngi-igenomes/igenomes/`, which needs access to that bucket and downloads them. Set `--igenomes-ignore true` to disable the lookup entirely.

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Ancient DNA assembly** (`ancient_dna_assembly`) — 9 parameters
- **Assembly options** (`assembly_options`) — 11 parameters
- **Bin quality check options** (`bin_quality_check_options`) — 23 parameters
- **Binning options** (`binning_options`) — 27 parameters
- **Gene prediction and annotation options** (`gene_prediction_and_annotation_options`) — 9 parameters
- **Generic options** (`generic_options`) — 16 parameters
- **Input/output options** (`input_output_options`) — 6 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Quality control for long reads options** (`quality_control_for_long_reads_options`) — 14 parameters
- **Quality control for short reads options** (`quality_control_for_short_reads_options`) — 26 parameters
- **Reference genome options** (`reference_genome_options`) — 2 parameters
- **Reproducibility options** (`reproducibility_options`) — 4 parameters
- **Taxonomic profiling options** (`taxonomic_profiling_options`) — 16 parameters
- **Virus identification options** (`virus_identification_options`) — 4 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run mag --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.04.2'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run mag ... --nxf-ver 25.04.2
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/mag/blob/5.4.2/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: AdapterRemoval2, ALE, BBnorm/BBTools, BCFtools, Bowtie2, BUSCO, CAT, CheckM, CheckM2, Chopper, COMEBin, CONCOCT, MetaBinner, SemiBin2, DAS Tool, FastP, FastQC, Filtlong, Flye, Freebayes, geNomad, GTDB-Tk, GUNC, BIgMAG, MaxBin2, MEGAHIT, MetaBAT2, MetaEuk, metaMDBG, minimap2, MMseqs2, MultiQC, NanoLyse, NanoPlot, Nanoq, Porechop, Porechop-abi, Prodigal, Prokka, PyDamage, SAMtools, Seqtk, SPAdes, Tiara, Trimmomatic.

Full list with references: https://github.com/nf-core/mag/blob/5.4.2/CITATIONS.md

## Demo
```bash
nfclaw run mag --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/mag/blob/5.4.2/docs/usage.md

<!-- Generated from nf-core/mag@5dabb0159ac0104885e09f301db22126e8fcb394. Do not edit by hand. -->
