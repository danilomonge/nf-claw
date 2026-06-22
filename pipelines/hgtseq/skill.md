---
name: hgtseq
pipeline: nf-core/hgtseq
version: 1.1.0
commit: 683daaf41bb396839445e603152b45daa141ced4
description: A pipeline to investigate horizontal gene transfer from NGS data
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, MultiQC, Trim Galore, Qualimap, BAMTOOLS, BWA, BWAmem2, SAMtools, Kraken2, Krona, RMarkDown
---
# hgtseq

A pipeline to investigate horizontal gene transfer from NGS data

## Run it
```bash
git submodule update --init pipelines/hgtseq/upstream   # first time only
nfclaw run hgtseq --input samplesheet.csv --outdir results --taxonomy-id <taxonomy_id> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/hgtseq/upstream -profile docker --input samplesheet.csv --outdir results --taxonomy-id <taxonomy_id>
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string | no |  |  |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fastq_1,fastq_2
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--taxonomy-id` | number |  |  | TaxID of samples used as input |
| `--krakendb` | string |  |  | A local path to kraken database folder or compressed database file, or a URL to a compressed database file, in tar.gz format |
| `--kronadb` | string |  |  | A local path or a URL to a .tab krona taxonomy file; it can also receive a compressed .tab file in tar.gz format |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `generic_options` (14 parameters)
- `input_output_options` (7 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)
- `reference_genome_options` (9 parameters)
- `run_options` (2 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/hgtseq/blob/1.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, MultiQC, Trim Galore, Qualimap, BAMTOOLS, BWA, BWAmem2, SAMtools, Kraken2, Krona, RMarkDown.

Full list with references: https://github.com/nf-core/hgtseq/blob/1.1.0/CITATIONS.md

## Demo
```bash
nfclaw run hgtseq --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/hgtseq/blob/1.1.0/docs/usage.md

<!-- Generated from nf-core/hgtseq@683daaf41bb396839445e603152b45daa141ced4. Do not edit by hand. -->
