---
name: createtaxdb
pipeline: nf-core/createtaxdb
version: 3.1.0
commit: b01a0f8ed96a5990d15470828dfa92a22cf08bba
description: Parallelised and automated creation of metagenomic classifier databases of different tools
summary: nf-core/createtaxdb is a bioinformatics pipeline that constructs custom metagenomic classifier databases for multiple classifiers and profilers from the same input reference genome set in a highly automated and parallelised manner. It supports both nucleotide and protein based classifiers and profilers. The pipeline is designed to be a companion pipeline to nf-core/taxprofiler for taxonomic profiling of metagenomic data, but can be used for any context.
has_samplesheet: true
input: samplesheet (id, taxid, fasta_dna, fasta_aa)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: Bracken, Centrifuge, Centrifuger, DIAMOND, ganon, Kaiju, KMCP, Kraken2, KrakenUniq, MALT, MetaCache, MultiQC, SeqKit2, sourmash, sylph
---
# createtaxdb

nf-core/createtaxdb is a bioinformatics pipeline that constructs custom metagenomic classifier databases for multiple classifiers and profilers from the same input reference genome set in a highly automated and parallelised manner. It supports both nucleotide and protein based classifiers and profilers. The pipeline is designed to be a companion pipeline to nf-core/taxprofiler for taxonomic profiling of metagenomic data, but can be used for any context.

## Run it
```bash
git submodule update --init pipelines/createtaxdb/upstream   # first time only
nfclaw run createtaxdb --input samplesheet.csv --outdir results --dbname <dbname> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/createtaxdb/upstream -profile docker --input samplesheet.csv --outdir results --dbname <dbname>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions createtaxdb` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show createtaxdb --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `id` | string | yes |  | matches ^\S+$ |
| `taxid` | integer | yes |  |  |
| `fasta_dna` | string (file path) | no |  | matches ^\S+\.(fasta\|fas\|fa\|fna)(\.gz)?$ |
| `fasta_aa` | string (file path) | no |  | matches ^\S+\.(fasta\|fas\|fa\|faa)(\.gz)?$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
id,taxid
```

Any of the optional columns above may be appended to the header when your data needs them: `fasta_dna`, `fasta_aa`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--dbname` | string |  |  |  | Specify name that resulting databases will be prefixed with. |
| `--unzip-batch-size` | integer | 10000 |  |  | How many files to unzip in parallel in a single job. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Database Building Options** (`database_building_options`) — 33 parameters
- **Downstream pipeline samplesheet generation options** (`generate_samplesheet_options`) — 2 parameters
- **Generic options** (`generic_options`) — 16 parameters
- **Input file preprocessing** (`input_file_preprocessing`) — 3 parameters
- **Input/output options** (`input_output_options`) — 13 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run createtaxdb --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.10.4'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run createtaxdb ... --nxf-ver 25.10.4
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/createtaxdb/blob/3.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: Bracken, Centrifuge, Centrifuger, DIAMOND, ganon, Kaiju, KMCP, Kraken2, KrakenUniq, MALT, MetaCache, MultiQC, SeqKit2, sourmash, sylph.

Full list with references: https://github.com/nf-core/createtaxdb/blob/3.1.0/CITATIONS.md

## Demo
```bash
nfclaw run createtaxdb --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/createtaxdb/blob/3.1.0/docs/usage.md

<!-- Generated from nf-core/createtaxdb@b01a0f8ed96a5990d15470828dfa92a22cf08bba. Do not edit by hand. -->
