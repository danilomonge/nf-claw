---
name: genomeassembler
pipeline: nf-core/genomeassembler
version: 1.1.0
commit: ccf1b89898cb720f46a966029c3a60dbcc25b012
description: Assemble genomes from long ONT or pacbio HiFi reads
summary: nf-core/genomeassembler is a bioinformatics pipeline that carries out genome assembly, polishing and scaffolding from long reads (ONT or pacbio). Assembly can be done via flye or hifiasm, polishing can be carried out with medaka (ONT), or pilon (requires short-reads), and scaffolding can be done using LINKS, Longstitch, or RagTag (if a reference is available). Quality control includes BUSCO, QUAST and merqury (requires short-reads). Currently, this pipeline does not implement phasing of polyploid genomes or HiC scaffolding.
has_samplesheet: true
input: samplesheet (sample, ontreads, hifireads, ref_fasta, ref_gff, shortread_F, shortread_R, paired)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions)
tools: lima, nanoq, porechop, TrimGalore, hifiasm, flye, pilon, medaka, LINKS, longstitch, RagTag, liftoff, BUSCO, genomescope2, jellyfish, meryl, QUAST, minimap2, samtools
---
# genomeassembler

nf-core/genomeassembler is a bioinformatics pipeline that carries out genome assembly, polishing and scaffolding from long reads (ONT or pacbio). Assembly can be done via flye or hifiasm, polishing can be carried out with medaka (ONT), or pilon (requires short-reads), and scaffolding can be done using LINKS, Longstitch, or RagTag (if a reference is available). Quality control includes BUSCO, QUAST and merqury (requires short-reads). Currently, this pipeline does not implement phasing of polyploid genomes or HiC scaffolding.

## Run it
```bash
git submodule update --init pipelines/genomeassembler/upstream   # first time only
nfclaw run genomeassembler --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/genomeassembler/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions genomeassembler` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show genomeassembler --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `ontreads` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `hifireads` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `ref_fasta` | string (file path) | no |  | matches ^\S+\.f(n\|ast)?a |
| `ref_gff` | string (file path) | no |  | matches ^\S+\.gff(3)? |
| `shortread_F` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `shortread_R` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `paired` | boolean | no |  |  |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample
```

Any of the optional columns above may be appended to the header when your data needs them: `ontreads`, `hifireads`, `ref_fasta`, `ref_gff`, `shortread_F`, `shortread_R`, `paired`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Annotations options** (`annotations_options`) — 1 parameter
- **Assembly options** (`assembly_options`) — 6 parameters
- **General parameters** (`general_parameters`) — 3 parameters
- **Generic options** (`generic_options`) — 8 parameters
- **HiFi options** (`hifi_options`) — 3 parameters
- **Input/output options** (`input_output_options`) — 3 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **ONT options** (`ont_options`) — 7 parameters
- **Polishing options** (`polishing_options`) — 3 parameters
- **QC options** (`qc_options`) — 6 parameters
- **Scaffolding options** (`scaffolding_options`) — 3 parameters
- **Short read options** (`short_read_options`) — 3 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run genomeassembler --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/genomeassembler/blob/1.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: lima, nanoq, porechop, TrimGalore, hifiasm, flye, pilon, medaka, LINKS, longstitch, RagTag, liftoff, BUSCO, genomescope2, jellyfish, meryl, QUAST, minimap2, samtools.

Full list with references: https://github.com/nf-core/genomeassembler/blob/1.1.0/CITATIONS.md

## Demo
```bash
nfclaw run genomeassembler --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/genomeassembler/blob/1.1.0/docs/usage.md

<!-- Generated from nf-core/genomeassembler@ccf1b89898cb720f46a966029c3a60dbcc25b012. Do not edit by hand. -->
