---
name: circdna
pipeline: nf-core/circdna
version: 1.1.0
commit: 8e0e14c84f90c94d975c2bac6bde8e5a1d5bc8ab
description: Pipeline for the identification of circular DNAs
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, MultiQC, Samtools, Trimgalore, BWA, Picard, Circle-Map, Unicycler, CNVKit, AmpliconSuite-Pipeline, AmpliconArchitect, AmpliconClassifier, Samblaster, Circle_finder, Circexplorer2
---
# circdna

Pipeline for the identification of circular DNAs

## Run it
```bash
git submodule update --init pipelines/circdna/upstream   # first time only
nfclaw run circdna --input samplesheet.csv --outdir results --input-format <input_format> --circle-identifier <circle_identifier> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/circdna/upstream -profile docker --input samplesheet.csv --outdir results --input-format <input_format> --circle-identifier <circle_identifier>
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
| `--input-format` | string |  |  | Specify input format. Default *FASTQ*. Options 'FASTQ' or 'BAM'. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--circle-identifier` | string |  |  | Specifies the circular DNA identification algorithm to use - available 'circle_map_realign', 'circle_map_repeats', 'circle_finder', 'circexplorer2', and 'ampliconarchitect'. Multiple circle_identifier's can be specified with a comma-separated string. E.g. `--circle_identifier 'circle_map_realign,unicycler'`. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `amplicon_architect_options` (5 parameters)
- `circdna_identifier_options` (1 parameter)
- `circle_finder_options` (1 parameter)
- `circle_map_options` (1 parameter)
- `generic_options` (15 parameters)
- `input_output_options` (7 parameters)
- `institutional_config_options` (6 parameters)
- `max_job_request_options` (3 parameters)
- `process_skipping_options` (5 parameters)
- `read_trimming_options` (8 parameters)
- `reference_genome_options` (5 parameters)
- `unicycler_options` (1 parameter)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/circdna/blob/1.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, MultiQC, Samtools, Trimgalore, BWA, Picard, Circle-Map, Unicycler, CNVKit, AmpliconSuite-Pipeline, AmpliconArchitect, AmpliconClassifier, Samblaster, Circle_finder, Circexplorer2.

Full list with references: https://github.com/nf-core/circdna/blob/1.1.0/CITATIONS.md

## Demo
```bash
nfclaw run circdna --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/circdna/blob/1.1.0/docs/usage.md

<!-- Generated from nf-core/circdna@8e0e14c84f90c94d975c2bac6bde8e5a1d5bc8ab. Do not edit by hand. -->
