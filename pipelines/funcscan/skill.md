---
name: funcscan
pipeline: nf-core/funcscan
version: 3.0.0
commit: fa9db018e528ffb5149cdde928e2fa24e7c546fe
description: Pipeline for screening for functional components of assembled contigs
summary: nf-core/funcscan is a bioinformatics best-practice analysis pipeline for the screening of nucleotide sequences such as assembled contigs for functional genes. It currently features mining for antimicrobial peptides, antibiotic resistance genes and biosynthetic gene clusters.
has_samplesheet: true
input: samplesheet (sample, fasta, protein, gbk)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: ABRicate, AMPir, AMPlify, AMRFinderPlus, AntiSMASH, argNorm, Bakta, comBGC, DeepARG, DeepBGC, fARGene, GECCO, AMPcombi, hAMRonization, HMMER, InterPro, InterProScan, Macrel, MMseqs2, Prodigal, PROKKA, Pyrodigal, RGI, SeqKit
---
# funcscan

nf-core/funcscan is a bioinformatics best-practice analysis pipeline for the screening of nucleotide sequences such as assembled contigs for functional genes. It currently features mining for antimicrobial peptides, antibiotic resistance genes and biosynthetic gene clusters.

## Run it
```bash
git submodule update --init pipelines/funcscan/upstream   # first time only
nfclaw run funcscan --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/funcscan/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions funcscan` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show funcscan --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fasta` | string (file path) | yes |  | matches ^\S+\.(fasta\|fas\|fna\|fa)(\.gz)?$ |
| `protein` | string (file path) | no |  | matches ^\S+\.(faa\|fasta)(\.gz)?$ |
| `gbk` | string (file path) | no |  | matches ^\S+\.(gbk\|gbff)(\.gz)?$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fasta,protein,gbk
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing sample names and paths to corresponding FASTA files, and optional annotation files. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `amp_ampcombi2_cluster` (7 parameters)
- `amp_ampcombi2_parsetables` (13 parameters)
- `amp_ampir` (3 parameters)
- `amp_amplify` (1 parameter)
- `amp_hmmsearch` (5 parameters)
- `amp_macrel` (1 parameter)
- `annotation_bakta` (22 parameters)
- `annotation_general_options` (2 parameters)
- `annotation_prodigal` (4 parameters)
- `annotation_prokka` (12 parameters)
- `annotation_pyrodigal` (5 parameters)
- `arg_abricate` (5 parameters)
- `arg_amrfinderplus` (7 parameters)
- `arg_argnorm` (1 parameter)
- `arg_deeparg` (9 parameters)
- `arg_fargene` (7 parameters)
- `arg_hamronization` (1 parameter)
- `arg_rgi` (10 parameters)
- `bgc_antismash` (13 parameters)
- `bgc_deepbgc` (11 parameters)
- `bgc_gecco` (6 parameters)
- `bgc_general_options` (2 parameters)
- `bgc_hmmsearch` (5 parameters)
- `database_downloading_options` (1 parameter)
- `generic_options` (13 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `protein_annotation` (6 parameters)
- `screening_type_activation` (3 parameters)
- `taxonomic_classification_general_options` (3 parameters)
- `taxonomic_classification_mmseqs2_databases` (3 parameters)
- `taxonomic_classification_mmseqs2_taxonomy` (8 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/funcscan/blob/3.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: ABRicate, AMPir, AMPlify, AMRFinderPlus, AntiSMASH, argNorm, Bakta, comBGC, DeepARG, DeepBGC, fARGene, GECCO, AMPcombi, hAMRonization, HMMER, InterPro, InterProScan, Macrel, MMseqs2, Prodigal, PROKKA, Pyrodigal, RGI, SeqKit.

Full list with references: https://github.com/nf-core/funcscan/blob/3.0.0/CITATIONS.md

## Demo
```bash
nfclaw run funcscan --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/funcscan/blob/3.0.0/docs/usage.md

<!-- Generated from nf-core/funcscan@fa9db018e528ffb5149cdde928e2fa24e7c546fe. Do not edit by hand. -->
