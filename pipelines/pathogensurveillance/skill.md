---
name: pathogensurveillance
pipeline: nf-core/pathogensurveillance
version: 1.1.0
commit: 13547eaa7345dab4ac97db49775ae8284af4113d
description: Surveillance of pathogens using high-throughput sequencing
summary: nf-core/pathogensurveillance is a population genomics pipeline for pathogen identification, variant detection, and biosurveillance. The pipeline accepts paths to raw reads for one or more organisms and creates reports in the form of an interactive HTML document. Significant features include the ability to analyze unidentified eukaryotic and prokaryotic samples, creation of reports for multiple user-defined groupings of samples, automated discovery and downloading of reference assemblies from NCBI RefSeq, and rapid initial identification based on k-mer sketches followed by a more robust multi gene phylogeny and SNP-based phylogeny.
has_samplesheet: true
input: samplesheet (sample_id, name, description, path, path_2, ncbi_accession, ncbi_query, ncbi_query_max, sequence_type, report_group_ids, color_by, ploidy, enabled, ref_group_ids)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, MultiQC
---
# pathogensurveillance

nf-core/pathogensurveillance is a population genomics pipeline for pathogen identification, variant detection, and biosurveillance. The pipeline accepts paths to raw reads for one or more organisms and creates reports in the form of an interactive HTML document. Significant features include the ability to analyze unidentified eukaryotic and prokaryotic samples, creation of reports for multiple user-defined groupings of samples, automated discovery and downloading of reference assemblies from NCBI RefSeq, and rapid initial identification based on k-mer sketches followed by a more robust multi gene phylogeny and SNP-based phylogeny.

## Run it
```bash
git submodule update --init pipelines/pathogensurveillance/upstream   # first time only
nfclaw run pathogensurveillance --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/pathogensurveillance/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions pathogensurveillance` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show pathogensurveillance --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample_id` | string | no |  |  |
| `name` | string | no |  |  |
| `description` | string | no |  |  |
| `path` | string | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `path_2` | string | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `ncbi_accession` | string | no |  | matches ^[A-Z]{3,6}[0-9]+$ |
| `ncbi_query` | string | no |  |  |
| `ncbi_query_max` | integer | no |  | ≥ 1 |
| `sequence_type` | string | no |  | matches (?i)illumina\|nanopore\|pacbio\|bgiseq |
| `report_group_ids` | string | no |  | matches ^[a-zA-Z0-9_ -]+(?:;[a-zA-Z0-9_ -]+)*$ |
| `color_by` | string | no |  |  |
| `ploidy` | integer | no |  | ≥ 1 |
| `enabled` | boolean | no |  |  |
| `ref_group_ids` | string | no |  |  |

`--input` must match `^\S+\.[ct]sv$`.

The samplesheet is a CSV with this header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample_id,name,description,path,path_2,ncbi_accession,ncbi_query,ncbi_query_max,sequence_type,report_group_ids,color_by,ploidy,enabled,ref_group_ids
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.[ct]sv$ | Path to comma/tab-separated file containing information about samples. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage if running on Cloud infrastructure. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Analysis parameters** (`analysis_parameters`) — 19 parameters
- **Generic options** (`generic_options`) — 17 parameters
- **Input/output options** (`input_output_options`) — 11 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run pathogensurveillance --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/pathogensurveillance/blob/1.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, MultiQC.

Full list with references: https://github.com/nf-core/pathogensurveillance/blob/1.1.0/CITATIONS.md

## Demo
```bash
nfclaw run pathogensurveillance --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/pathogensurveillance/blob/1.1.0/docs/usage.md

<!-- Generated from nf-core/pathogensurveillance@13547eaa7345dab4ac97db49775ae8284af4113d. Do not edit by hand. -->
