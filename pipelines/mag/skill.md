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

Additional row validation rules from the schema:
- When `short_reads_2` is set, also provide `short_reads_1`.
- When `short_reads_1` is set, also provide `short_reads_platform`.
- When `long_reads` is set, also provide `long_reads_platform`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,run,group,short_reads_1,short_reads_2,short_reads_platform,long_reads,long_reads_platform
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | CSV samplesheet file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `ancient_dna_assembly` (9 parameters)
- `assembly_options` (11 parameters)
- `bin_quality_check_options` (23 parameters)
- `binning_options` (27 parameters)
- `gene_prediction_and_annotation_options` (9 parameters)
- `generic_options` (16 parameters)
- `input_output_options` (6 parameters)
- `institutional_config_options` (6 parameters)
- `quality_control_for_long_reads_options` (14 parameters)
- `quality_control_for_short_reads_options` (26 parameters)
- `reference_genome_options` (2 parameters)
- `reproducibility_options` (4 parameters)
- `taxonomic_profiling_options` (16 parameters)
- `virus_identification_options` (4 parameters)

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
