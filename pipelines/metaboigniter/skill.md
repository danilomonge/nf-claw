---
name: metaboigniter
pipeline: nf-core/metaboigniter
version: 2.0.1
commit: 55d82547604fcae3b6557fe7a3c442b623184f34
description: Pre-processing of mass spectrometry-based metabolomics data
summary: nf-core/metaboigniter is a bioinformatics pipeline that ingests raw mass spectrometry data in mzML format, typically in the form of peak lists and MS2 spectral data, for comprehensive metabolomics analysis. The key stages involve centroiding, feature detection, adduct detection, alignment, and linking, which progressively refine and align the data. The pipeline can also perform requantification to compensate for missing values and leverages MS2Query for compound identification based on MS2 data, outputting a comprehensive list of detected and potentially identified metabolites.
has_samplesheet: true
input: samplesheet (sample, type, level, msfile)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: OpenMS, SIRIUS, MS2Query
---
# metaboigniter

nf-core/metaboigniter is a bioinformatics pipeline that ingests raw mass spectrometry data in mzML format, typically in the form of peak lists and MS2 spectral data, for comprehensive metabolomics analysis. The key stages involve centroiding, feature detection, adduct detection, alignment, and linking, which progressively refine and align the data. The pipeline can also perform requantification to compensate for missing values and leverages MS2Query for compound identification based on MS2 data, outputting a comprehensive list of detected and potentially identified metabolites.

## Run it
```bash
git submodule update --init pipelines/metaboigniter/upstream   # first time only
nfclaw run metaboigniter --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/metaboigniter/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions metaboigniter` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show metaboigniter --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `type` | string | yes |  | matches ^\S+$ |
| `level` | string | yes | MS1, MS2, MS12 |  |
| `msfile` | string (file path) | yes |  | matches ^\S+\.mzML |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,type,level,msfile
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `alignment_and_linking` (70 parameters)
- `annotation` (16 parameters)
- `generic_controls` (8 parameters)
- `generic_options` (15 parameters)
- `input_output_options` (5 parameters)
- `institutional_config_options` (6 parameters)
- `mapping_and_identification` (45 parameters)
- `max_job_request_options` (3 parameters)
- `quantification` (43 parameters)
- `re_quantification` (18 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/metaboigniter/blob/2.0.1/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: OpenMS, SIRIUS, MS2Query.

Full list with references: https://github.com/nf-core/metaboigniter/blob/2.0.1/CITATIONS.md

## Demo
```bash
nfclaw run metaboigniter --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/metaboigniter/blob/2.0.1/docs/usage.md

<!-- Generated from nf-core/metaboigniter@55d82547604fcae3b6557fe7a3c442b623184f34. Do not edit by hand. -->
