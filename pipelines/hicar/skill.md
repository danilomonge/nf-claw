---
name: hicar
pipeline: nf-core/hicar
version: 1.0.0
commit: 429087d2b13e59c3edd2e71b8005c1adc5bbb7bb
description: This pipeline analyses data for HiCAR data, a robust and sensitive multi-omic co-assay for simultaneous measurement of transcriptome, chromatin accessibility and cis-regulatory chromatin contacts.
summary: nf-core/hicar is a bioinformatics best-practice analysis pipeline for HiC on Accessible Regulatory DNA (HiCAR) data, a robust and sensitive assay for simultaneous measurement of chromatin accessibility and cis-regulatory chromatin contacts. Unlike the immunoprecipitation-based methods such as HiChIP, PlAC-seq and ChIA-PET, HiCAR does not require antibodies. HiCAR utilizes a Transposase-Accessible Chromatin assay to anchor the chromatin interactions. HiCAR is a tool to study chromatin interactions for low input samples and samples with no available antibodies.
has_samplesheet: true
input: samplesheet (group, replicate, fastq_1, fastq_2, md5_1, md5_2)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, MultiQC, BWA, BEDTools, SAMtools, UCSC tools, cooler, MACS2, MAPS, GenMap, edgeR, ChIPpeakAnno, clusterProfiler, trackViewer, circos, Juicer_tools, igv.js, pairsqc, pairtools
---
# hicar

nf-core/hicar is a bioinformatics best-practice analysis pipeline for HiC on Accessible Regulatory DNA (HiCAR) data, a robust and sensitive assay for simultaneous measurement of chromatin accessibility and cis-regulatory chromatin contacts. Unlike the immunoprecipitation-based methods such as HiChIP, PlAC-seq and ChIA-PET, HiCAR does not require antibodies. HiCAR utilizes a Transposase-Accessible Chromatin assay to anchor the chromatin interactions. HiCAR is a tool to study chromatin interactions for low input samples and samples with no available antibodies.

## Run it
```bash
git submodule update --init pipelines/hicar/upstream   # first time only
nfclaw run hicar --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/hicar/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions hicar` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show hicar --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `group` | string | yes |  | matches ^\S+$ |
| `replicate` | integer | yes |  |  |
| `fastq_1` | string | yes |  | matches ^\S+\.f(ast)?q\.gz$ |
| `fastq_2` | string | yes |  |  |
| `md5_1` | string | no |  |  |
| `md5_2` | string | no |  |  |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
group,replicate,fastq_1,fastq_2
```

Any of the optional columns above may be appended to the header when your data needs them: `md5_1`, `md5_2`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **MACS2 peak calling options** (`MACS2_peak_calling_options`) — 5 parameters
- **MAPS peak calling options** (`MAPS_peak_calling_options`) — 13 parameters
- **Other options not expose** (`Other_options_not_expose_yet`) — 5 parameters
- **Options related to tracks, juicer_tools, and circos** (`Visualization_options`) — 4 parameters
- **Experiment design options** (`experiment_config_options`) — 3 parameters
- **Generic options** (`generic_options`) — 11 parameters
- **Input/output options** (`input_output_options`) — 6 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Max job request options** (`max_job_request_options`) — 3 parameters
- **Pipeline controler** (`pipeline_controls`) — 6 parameters
- **Reference genome options** (`reference_genome_options`) — 12 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run hicar --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/hicar/blob/1.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, MultiQC, BWA, BEDTools, SAMtools, UCSC tools, cooler, MACS2, MAPS, GenMap, edgeR, ChIPpeakAnno, clusterProfiler, trackViewer, circos, Juicer_tools, igv.js, pairsqc, pairtools.

Full list with references: https://github.com/nf-core/hicar/blob/1.0.0/CITATIONS.md

## Demo
```bash
nfclaw run hicar --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/hicar/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/hicar@429087d2b13e59c3edd2e71b8005c1adc5bbb7bb. Do not edit by hand. -->
