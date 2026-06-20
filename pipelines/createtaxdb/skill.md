---
name: createtaxdb
pipeline: nf-core/createtaxdb
version: 3.0.0
commit: e561e64257492bb337a4ade1555ecb772156a0c2
description: Parallelised and automated creation of metagenomic classifier databases of different tools
has_samplesheet: true
input: samplesheet (id, taxid, fasta_dna, fasta_aa)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
---
# createtaxdb

Parallelised and automated creation of metagenomic classifier databases of different tools

## Run it
```bash
git submodule update --init pipelines/createtaxdb/upstream   # first time only
nfclaw run createtaxdb --input samplesheet.csv --outdir results --dbname <dbname> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/createtaxdb/upstream -profile docker --input samplesheet.csv --outdir results --dbname <dbname>
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `id` | string | yes |  | matches ^\S+$ |
| `taxid` | integer | yes |  |  |
| `fasta_dna` | string (file path) | no |  | matches ^\S+\.(fasta\|fas\|fa\|fna)(\.gz)?$ |
| `fasta_aa` | string (file path) | no |  | matches ^\S+\.(fasta\|fas\|fa\|faa)(\.gz)?$ |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
id,taxid,fasta_dna,fasta_aa
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--dbname` | string |  |  | Specify name that resulting databases will be prefixed with. |
| `--unzip-batch-size` | integer |  |  | How many files to unzip in parallel in a single job. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `database_building_options` (31 parameters)
- `generate_samplesheet_options` (2 parameters)
- `generic_options` (16 parameters)
- `input_file_preprocessing` (3 parameters)
- `input_output_options` (13 parameters)
- `institutional_config_options` (6 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/createtaxdb/blob/3.0.0/docs/output.md

## Demo
```bash
nfclaw run createtaxdb --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/createtaxdb/blob/3.0.0/docs/usage.md

<!-- Generated from nf-core/createtaxdb@e561e64257492bb337a4ade1555ecb772156a0c2. Do not edit by hand. -->
