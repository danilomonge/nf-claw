---
name: readsimulator
pipeline: nf-core/readsimulator
version: 1.0.1
commit: 0e8805ddbcd0e0fdcdc62105d59c3f29dd985a64
description: A workflow to simulate reads
summary: nf-core/readsimulator is a pipeline to simulate sequencing reads. The pipeline currently supports simulating amplicon, target capture, metagenome, and wholegenome data. It takes a samplesheet with sample names and seeds for random generation to produce simulated FASTQ files and a samplesheet that contains the paths to the FASTQ files.
has_samplesheet: true
input: samplesheet (sample, seed)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: ART, bedtools, Bowtie2, CapSim, CRABS, FastQC, InSilicoSeq, MultiQC, ncbi-genome-download, Samtools, Wgsim, Tetrapods; 2,560 baits for 2,386 UCEs; version 1, Tetrapods; 5,472 baits for 5,060 UCEs; version 1, Actinopterygians; 2,001 baits for 500 UCEs; version 1, Acanthomorphs; 2,628 baits for 1,314 UCEs; version 1, Arachnida; 14,799 baits for 1,120 UCEs; version 1, Coleoptera; 13,674 baits for 1,172 UCEs; version 1, Diptera; 31,328 baits for 2,711 UCEs; version 1, Hemiptera; 40,207 baits for 2,731 UCEs; version 1, Hymenoptera; 2,749 baits for 1,510 UCEs; version 1, Hymenoptera; 31,829 baits for 2,590 UCEs; version 2, Anthozoa; 16,306 baits for 720 UCEs and 1,071 exons; version 1
---
# readsimulator

nf-core/readsimulator is a pipeline to simulate sequencing reads. The pipeline currently supports simulating amplicon, target capture, metagenome, and wholegenome data. It takes a samplesheet with sample names and seeds for random generation to produce simulated FASTQ files and a samplesheet that contains the paths to the FASTQ files.

## Run it
```bash
git submodule update --init pipelines/readsimulator/upstream   # first time only
nfclaw run readsimulator --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/readsimulator/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions readsimulator` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show readsimulator --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `seed` | integer | yes |  |  |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,seed
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Reference genome
No reference genome is set by default: supply your own (the `reference_genome_options` group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`). Passing `--genome <id>` instead resolves the references from AWS iGenomes, which needs access to that bucket and downloads them. Set `--igenomes-ignore true` to disable the lookup entirely.

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Amplicon options** (`amplicon_options`) — 6 parameters
- **Generic options** (`generic_options`) — 15 parameters
- **Input/output options** (`input_output_options`) — 4 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Max job request options** (`max_job_request_options`) — 3 parameters
- **Metagenome options** (`metagenome_options`) — 9 parameters
- **Reference genome options** (`reference_genome_options`) — 7 parameters
- **Simulation options** (`simulation_options`) — 4 parameters
- **Target capture options** (`target_capture_options`) — 13 parameters
- **Wholegenome options** (`wholegenome_options`) — 9 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run readsimulator --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=23.04.0'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run readsimulator ... --nxf-ver 23.04.0
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/readsimulator/blob/1.0.1/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: ART, bedtools, Bowtie2, CapSim, CRABS, FastQC, InSilicoSeq, MultiQC, ncbi-genome-download, Samtools, Wgsim, Tetrapods; 2,560 baits for 2,386 UCEs; version 1, Tetrapods; 5,472 baits for 5,060 UCEs; version 1, Actinopterygians; 2,001 baits for 500 UCEs; version 1, Acanthomorphs; 2,628 baits for 1,314 UCEs; version 1, Arachnida; 14,799 baits for 1,120 UCEs; version 1, Coleoptera; 13,674 baits for 1,172 UCEs; version 1, Diptera; 31,328 baits for 2,711 UCEs; version 1, Hemiptera; 40,207 baits for 2,731 UCEs; version 1, Hymenoptera; 2,749 baits for 1,510 UCEs; version 1, Hymenoptera; 31,829 baits for 2,590 UCEs; version 2, Anthozoa; 16,306 baits for 720 UCEs and 1,071 exons; version 1.

Full list with references: https://github.com/nf-core/readsimulator/blob/1.0.1/CITATIONS.md

## Demo
```bash
nfclaw run readsimulator --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/readsimulator/blob/1.0.1/docs/usage.md

<!-- Generated from nf-core/readsimulator@0e8805ddbcd0e0fdcdc62105d59c3f29dd985a64. Do not edit by hand. -->
