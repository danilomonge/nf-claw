---
name: ribomsqc
pipeline: nf-core/ribomsqc
version: 1.0.0
commit: 79916e8dea42d7d60b139607ca8eacfaf68e0e19
description: QC pipeline that monitors mass spectrometer performance in ribonucleoside analysis
summary: QC pipeline that monitors mass spectrometer performance in ribonucleoside analysis
has_samplesheet: true
input: samplesheet (id, raw_file)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: ThermoRawFileParser, MSnbase - Bioconductor package, MultiQC
---
# ribomsqc

QC pipeline that monitors mass spectrometer performance in ribonucleoside analysis

## Run it
```bash
git submodule update --init pipelines/ribomsqc/upstream   # first time only
nfclaw run ribomsqc --input samplesheet.csv --outdir results --analytes-tsv <analytes_tsv> --analyte <analyte> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/ribomsqc/upstream -profile docker --input samplesheet.csv --outdir results --analytes-tsv <analytes_tsv> --analyte <analyte>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions ribomsqc` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show ribomsqc --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `id` | string | yes |  | matches ^\S+$ |
| `raw_file` | string (file path) | yes |  | matches ^\S+\.raw$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
id,raw_file
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to a comma-separated file (CSV) listing samples to process. Must contain a header with two columns: 'id' (sample identifier) and 'raw_file' (full path to the corresponding RAW file). You may specify one or multiple samples for batch processing. |
| `--outdir` | string (directory path) |  |  |  | Directory where the pipeline will write its output. If a relative folder name is used (e.g., 'results'), it will be created in the current working directory. If an absolute path is given (e.g., '/path/to/output'), the folder will be created at that specific location. |
| `--analytes-tsv` | string (file path) |  |  | matches ^\S+\.tsv$ | Path to a tab-separated values (TSV) file describing the analytes for chromatographic peak extraction. Must include columns: `short_name`, `long_name`, `mz_M0` (required), and optionally `mz_M1`, `mz_M2`, `ms2_mz`, and `rt_teoretical` (required). Only `mz_M0` and `rt_teoretical` are mandatory. `mz_M1` and `mz_M2` are reserved for future support of isotopic envelope integration. |
| `--analyte` | string |  |  |  | Short name of the analyte to be extracted, as defined in the 'short_name' column of the TSV file. Use a specific value such as 'm3C' to process one analyte, or use 'all' to process all analytes defined in the TSV file. |
| `--rt-tolerance` | integer | 150 |  |  | Time window (in seconds) around the theoretical retention time in which peaks will be searched. The window is defined as RT ± tolerance. |
| `--mz-tolerance` | integer | 20 |  |  | Tolerance in parts-per-million (ppm) around the specified precursor m/z value (mz_M0) for XIC extraction. The window is defined as mz_M0 ± tolerance. |
| `--ms-level` | integer | 2 |  |  | MS level to extract chromatographic peaks from. Set to 1 for MS1 or 2 for MS2. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Generic options** (`generic_options`) — 12 parameters
- **Input/output options** (`input_output_options`) — 3 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **XIC extraction and plotting** (`xic_parameters`) — 10 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run ribomsqc --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.04.0'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run ribomsqc ... --nxf-ver 25.04.0
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/ribomsqc/blob/1.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: ThermoRawFileParser, MSnbase - Bioconductor package, MultiQC.

Full list with references: https://github.com/nf-core/ribomsqc/blob/1.0.0/CITATIONS.md

## Demo
```bash
nfclaw run ribomsqc --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/ribomsqc/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/ribomsqc@79916e8dea42d7d60b139607ca8eacfaf68e0e19. Do not edit by hand. -->
