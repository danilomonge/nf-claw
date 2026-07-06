---
name: isoseq
pipeline: nf-core/isoseq
version: 2.0.0
commit: c7536ab0e18a27460476d4e8557845950292f070
description: Genes and transcripts annotation with Isoseq using uLTRA and TAMA
summary: nf-core/isoseq is a bioinformatics best-practice analysis pipeline for Isoseq gene annotation with uLTRA and TAMA. Starting from raw isoseq subreads, the pipeline:
has_samplesheet: true
input: samplesheet (sample, bam, pbi, reads)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: CCS, LIMA, ISOSEQ3 REFINE, SAMTOOLS, ULTRA, MINIMAP2, BAMTOOLS, TAMA, MultiQC
---
# isoseq

nf-core/isoseq is a bioinformatics best-practice analysis pipeline for Isoseq gene annotation with uLTRA and TAMA. Starting from raw isoseq subreads, the pipeline:

## Run it
```bash
git submodule update --init pipelines/isoseq/upstream   # first time only
nfclaw run isoseq --input samplesheet.csv --outdir results --primers <primers> --aligner <aligner> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/isoseq/upstream -profile docker --input samplesheet.csv --outdir results --primers <primers> --aligner <aligner>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions isoseq` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show isoseq --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `bam` | string (file path) | no |  | matches (^\S+\.bam$\|^None$) |
| `pbi` | string (file path) | no |  | matches (^\S+\.bam\.pbi$\|^None$) |
| `reads` | string (file path) | no |  | matches (^\S+\.fa\.gz$\|^None$) |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,bam,pbi,reads
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--primers` | string |  |  |  | Fasta file of primers sequences |
| `--aligner` | string |  | minimap2, ultra |  | Aligner to use for mapping: minimap2 or ultra |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `aligner_option` (1 parameter)
- `ccs_options` (6 parameters)
- `generic_options` (16 parameters)
- `input_output_options` (8 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)
- `reference_genome_options` (3 parameters)
- `tama_options` (4 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/isoseq/blob/2.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: CCS, LIMA, ISOSEQ3 REFINE, SAMTOOLS, ULTRA, MINIMAP2, BAMTOOLS, TAMA, MultiQC.

Full list with references: https://github.com/nf-core/isoseq/blob/2.0.0/CITATIONS.md

## Demo
```bash
nfclaw run isoseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/isoseq/blob/2.0.0/docs/usage.md

<!-- Generated from nf-core/isoseq@c7536ab0e18a27460476d4e8557845950292f070. Do not edit by hand. -->
