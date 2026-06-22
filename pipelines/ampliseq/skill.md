---
name: ampliseq
pipeline: nf-core/ampliseq
version: 2.18.0
commit: 2723d4c298d48321594920d0324697e14d73ee94
description: Amplicon sequencing analysis workflow using DADA2 and QIIME2
has_samplesheet: true
input: samplesheet (sampleID, forwardReads, reverseReads, sample, fastq_1, fastq_2, run, control, quant_reading)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, Cutadapt, Barrnap, DADA2, Greengenes2, PR2 - Protist Reference Ribosomal Database, GTDB - Genome Taxonomy Database, SBDI-GTDB, RDP - Ribosomal Database Project, UNITE - eukaryotic nuclear ribosomal ITS region, MIDORI2 - a collection of reference databases, COIDB - CO1 Taxonomy Database, PhytoRef plastid 16S rRNA database for photosynthetic eukaryotes, Zehr lab nifH database, BOLD Plantae, nf-core/phyloplace, HMMER, MAFFT, EPA-NG, Gappa, q2-sidle, SMURF, RESCRIPt, SEPP, QIIME2, ANCOM, ANCOM-BC, ANCOM-BC2, Adonis, Phyloseq, TreeSummarizedExperiment, ITSx, ITSxRust, PICRUSt2, VSEARCH, decontam, Kraken2, MultiQC
---
# ampliseq

Amplicon sequencing analysis workflow using DADA2 and QIIME2

## Run it
```bash
git submodule update --init pipelines/ampliseq/upstream   # first time only
nfclaw run ampliseq --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/ampliseq/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sampleID` | string | no |  | matches ^[a-zA-Z][a-zA-Z0-9_]+$ |
| `forwardReads` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `reverseReads` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `sample` | string | no |  | matches ^[a-zA-Z][a-zA-Z0-9_]+$ |
| `fastq_1` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `run` | string or integer | no |  | matches ^\S+$ |
| `control` | string | no | control, sample |  |
| `quant_reading` | number | no |  |  |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sampleID,forwardReads,reverseReads,sample,fastq_1,fastq_2,run,control,quant_reading
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `amplicon_sequence_variants_asv_calculation` (8 parameters)
- `asv_filtering` (3 parameters)
- `asv_post_processing` (14 parameters)
- `differential_abundance_analysis` (10 parameters)
- `downstream_analysis` (8 parameters)
- `generic_options` (16 parameters)
- `input_output_options` (11 parameters)
- `institutional_config_options` (7 parameters)
- `multiregion_taxonomic_database` (7 parameters)
- `pipeline_report` (5 parameters)
- `primer_removal` (5 parameters)
- `read_trimming_and_quality_filtering` (9 parameters)
- `running_specific_steps` (1 parameter)
- `sequencing_input` (11 parameters)
- `skipping_specific_steps` (17 parameters)
- `taxonomic_assignment` (38 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/ampliseq/blob/2.18.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, Cutadapt, Barrnap, DADA2, Greengenes2, PR2 - Protist Reference Ribosomal Database, GTDB - Genome Taxonomy Database, SBDI-GTDB, RDP - Ribosomal Database Project, UNITE - eukaryotic nuclear ribosomal ITS region, MIDORI2 - a collection of reference databases, COIDB - CO1 Taxonomy Database, PhytoRef plastid 16S rRNA database for photosynthetic eukaryotes, Zehr lab nifH database, BOLD Plantae, nf-core/phyloplace, HMMER, MAFFT, EPA-NG, Gappa, q2-sidle, SMURF, RESCRIPt, SEPP, QIIME2, ANCOM, ANCOM-BC, ANCOM-BC2, Adonis, Phyloseq, TreeSummarizedExperiment, ITSx, ITSxRust, PICRUSt2, VSEARCH, decontam, Kraken2, MultiQC.

Full list with references: https://github.com/nf-core/ampliseq/blob/2.18.0/CITATIONS.md

## Demo
```bash
nfclaw run ampliseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/ampliseq/blob/2.18.0/docs/usage.md

<!-- Generated from nf-core/ampliseq@2723d4c298d48321594920d0324697e14d73ee94. Do not edit by hand. -->
