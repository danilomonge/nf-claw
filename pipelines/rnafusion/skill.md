---
name: rnafusion
pipeline: nf-core/rnafusion
version: 4.1.3
commit: 76ad76e7c39b2ba9edc35aa3602e3dc454d842ec
description: Nextflow rnafusion analysis pipeline, part of the nf-core community.
summary: nf-core/rnafusion is a bioinformatics best-practice analysis pipeline for RNA sequencing consisting of several tools designed for detecting and visualizing fusion genes. Results from fusion callers tools (STAR-Fusion, arriba and FusionCatcher) are created, and are also aggregated, most notably in a pdf visualisation document, a vcf data collection file, and html and tsv reports. In parallel StringTie and CTAT-Splicing collect additional information on splicing events.
has_samplesheet: true
input: samplesheet (sample, fastq_1, fastq_2, bam, bai, cram, crai, junctions, splice_junctions, strandedness, seq_platform, seq_center)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: Arriba, BEDOPS, FastP, FastQC, FusionCatcher, FusionInspector, Fusion-report, GATK4, MegaFusion, MultiQC, picard-tools, SAMtools, STAR, STAR-Fusion, StringTie
---
# rnafusion

nf-core/rnafusion is a bioinformatics best-practice analysis pipeline for RNA sequencing consisting of several tools designed for detecting and visualizing fusion genes. Results from fusion callers tools (STAR-Fusion, arriba and FusionCatcher) are created, and are also aggregated, most notably in a pdf visualisation document, a vcf data collection file, and html and tsv reports. In parallel StringTie and CTAT-Splicing collect additional information on splicing events.

## Run it
```bash
git submodule update --init pipelines/rnafusion/upstream   # first time only
nfclaw run rnafusion --input samplesheet.csv --outdir results --genomes-base <genomes_base> --tools <tools> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/rnafusion/upstream -profile docker --input samplesheet.csv --outdir results --genomes-base <genomes_base> --tools <tools>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions rnafusion` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show rnafusion --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fastq_1` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `bam` | string (file path) | no |  | matches ^\S+\.bam$ |
| `bai` | string (file path) | no |  | matches ^\S+\.bam\.bai$ |
| `cram` | string (file path) | no |  | matches ^\S+\.cram$ |
| `crai` | string (file path) | no |  | matches ^\S+\.cram\.crai$ |
| `junctions` | string (file path) | no |  | matches ^\S+\.junction$ |
| `splice_junctions` | string (file path) | no |  | matches ^\S+\.SJ.out.tab$ |
| `strandedness` | string | yes | forward, reverse, unstranded, unknown |  |
| `seq_platform` | string | no |  | matches ^\S+$ |
| `seq_center` | string | no |  | matches ^\S+$ |

`--input` must match `^\S+\.(csv|yaml|yml|json)$`.

Additional row validation rules from the schema:
- When `bai` is set, also provide `bam`.
- When `crai` is set, also provide `cram`.

The samplesheet is a CSV with this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,strandedness
```

Any of the optional columns above may be appended to the header when your data needs them: `fastq_1`, `fastq_2`, `bam`, `bai`, `cram`, `crai`, `junctions`, `splice_junctions`, `seq_platform`, `seq_center`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--genomes-base` | string |  |  |  | Path to reference folder |
| `--tools` | string |  |  | matches ^((arriba\|ctatsplicing\|fusioncatcher\|starfusion\|stringtie\|fusionreport\|fastp\|salmon\|fusioninspector\|all)?,?)*(?<!,)$ | Comma-delimited list of tools to run |

## Reference genome
No reference genome is set by default: supply your own (the `reference_genome_options` group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`). Passing `--genome <id>` instead resolves the references from AWS iGenomes, which needs access to that bucket and downloads them.

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Alignment compression options** (`compression_options`) — 1 parameter
- **Generic options** (`generic_options`) — 18 parameters
- **Input/output options** (`input_output_options`) — 39 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Read trimming options** (`read_trimming_options`) — 6 parameters
- **Reference genome options** (`reference_genome_options`) — 12 parameters
- **Skip steps** (`skip_steps`) — 3 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run rnafusion --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.10.4'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run rnafusion ... --nxf-ver 25.10.4
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/rnafusion/blob/4.1.3/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: Arriba, BEDOPS, FastP, FastQC, FusionCatcher, FusionInspector, Fusion-report, GATK4, MegaFusion, MultiQC, picard-tools, SAMtools, STAR, STAR-Fusion, StringTie.

Full list with references: https://github.com/nf-core/rnafusion/blob/4.1.3/CITATIONS.md

## Demo
```bash
nfclaw run rnafusion --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/rnafusion/blob/4.1.3/docs/usage.md

<!-- Generated from nf-core/rnafusion@76ad76e7c39b2ba9edc35aa3602e3dc454d842ec. Do not edit by hand. -->
