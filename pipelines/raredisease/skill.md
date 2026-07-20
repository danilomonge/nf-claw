---
name: raredisease
pipeline: nf-core/raredisease
version: 3.1.2
commit: 83f2699d28bc957e1d3b875da3d96004a818c2c3
description: call and score variants from WGS/WES of rare disease patients
summary: nf-core/raredisease is a best-practice bioinformatic pipeline for calling and scoring variants from WGS/WES data from rare disease patients. This pipeline is heavily inspired by MIP.
has_samplesheet: true
input: samplesheet (sample, lane, fastq_1, fastq_2, spring_1, spring_2, bam, bai, sex, phenotype, paternal_id, maternal_id, case_id)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: nf-core, Nextflow, BCFtools, BEDTools, BWA-MEM, BWA-MEM2, BWA-MEME, CADD<sup>1</sup>, DeepVariant, Chromograph, Ensembl VEP, ExpansionHunter, FastQC, Fastp, GATK, Genmod, Gens, GLnexus, Manta, Mitosalt, Mosdepth, ngs-bits-samplegender, MultiQC, Peddy, Picard, RetroSeq, rhocall, RTG Tools (vcfeval), saltshaker, Sambamba, Sentieon DNAscope, Sentieon DNASeq, SMNCopyNumberCaller, Spring, stranger, svdb, Tabix, TIDDIT, UPD, UCSC Bigwig and Bigbed, vcf2cytosure, Vcfanno, VerifyBamID2
---
# raredisease

nf-core/raredisease is a best-practice bioinformatic pipeline for calling and scoring variants from WGS/WES data from rare disease patients. This pipeline is heavily inspired by MIP.

## Run it
```bash
git submodule update --init pipelines/raredisease/upstream   # first time only
nfclaw run raredisease --input samplesheet.csv --outdir results --fasta <fasta> --intervals-wgs <intervals_wgs> --intervals-y <intervals_y> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/raredisease/upstream -profile docker --input samplesheet.csv --outdir results --fasta <fasta> --intervals-wgs <intervals_wgs> --intervals-y <intervals_y>
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions raredisease` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show raredisease --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `lane` | integer or string | no |  |  |
| `fastq_1` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `fastq_2` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.f(ast)?q\.gz$ |
| `spring_1` | string (file path) | no |  | matches ^\S+.spring$ |
| `spring_2` | string (file path) | no |  | matches ^\S+.spring$ |
| `bam` | string (file path) | no |  | matches ^\S+\.bam$ |
| `bai` | string (file path) | no |  | matches ^\S+\.bai$ |
| `sex` | integer or string | yes |  |  |
| `phenotype` | integer | yes | 0, 1, 2 |  |
| `paternal_id` | string | no |  |  |
| `maternal_id` | string | no |  |  |
| `case_id` | string | yes |  | matches ^\S+$ |

`--input` must match `^\S+\.(csv|tsv|json|yaml|yml)$`.

Additional row validation rules from the schema:
- When `fastq_2` is set, also provide `fastq_1`.
- When `spring_2` is set, also provide `spring_1`.
- When `bam` is set, also provide `bai`.
- At least one of these conditional requirements must be satisfied: `fastq_1` when `lane` is set; `spring_1` when `lane` is set.

For tabular CSV/TSV input, use this header (the columns the schema requires); fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,sex,phenotype,case_id
```

Any of the optional columns above may be appended to the header when your data needs them: `lane`, `fastq_1`, `fastq_2`, `spring_1`, `spring_2`, `bam`, `bai`, `paternal_id`, `maternal_id`.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--fasta` | string (file path) |  |  | matches ^\S+\.fn?a(sta)?(\.gz)?$ | Path to FASTA genome file. |
| `--intervals-wgs` | string |  |  | matches ^\S+\.intervals?(_list)?$ | Path to the interval list of the genome (autosomes, sex chromosomes, and mitochondria). |
| `--intervals-y` | string |  |  | matches ^\S+\.intervals?(_list)?$ | Path to the interval list of the Y chromosome. |

## Reference genome
**This release resolves a reference genome remotely by default.** `--genome` defaults to `GRCh38`, which is looked up in AWS iGenomes at `s3://ngi-igenomes/igenomes/`. A run that passes no reference of its own therefore reads its references over S3 — that fails on a host without access to the bucket, and downloads tens of gigabytes on one that has it. For a self-contained run, pass your own reference instead (the `reference_genome_options` group in [reference.md](reference.md) lists every accepted file, e.g. `--fasta`). Set `--igenomes-ignore true` to disable the lookup entirely.

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Alignment options** (`alignment_options`) — 10 parameters
- **Analysis options** (`analysis_options`) — 17 parameters
- **Annotation options** (`annotation_options`) — 3 parameters
- **Generic options** (`generic_options`) — 17 parameters
- **Input/output options** (`input_output_options`) — 4 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Mitosalt and saltshaker options** (`mitosalt_options`) — 27 parameters
- **Reference file options** (`reference_file_options`) — 61 parameters
- **Variant calling options** (`variant_calling_options`) — 5 parameters

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run raredisease --input samplesheet.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Nextflow engine
This release declares `nextflowVersion = '!>=25.10.4'`.

To run the engine this release targets — worth doing if a newer Nextflow emits config-parser warnings the release never saw:
```bash
nfclaw run raredisease ... --nxf-ver 25.10.4
```
`--nxf-ver` is recorded in `<outdir>/provenance/`, so the replay uses the same engine. See [known-issues](../../docs/known-issues.md).

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/raredisease/blob/3.1.2/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: nf-core, Nextflow, BCFtools, BEDTools, BWA-MEM, BWA-MEM2, BWA-MEME, CADD<sup>1</sup>, DeepVariant, Chromograph, Ensembl VEP, ExpansionHunter, FastQC, Fastp, GATK, Genmod, Gens, GLnexus, Manta, Mitosalt, Mosdepth, ngs-bits-samplegender, MultiQC, Peddy, Picard, RetroSeq, rhocall, RTG Tools (vcfeval), saltshaker, Sambamba, Sentieon DNAscope, Sentieon DNASeq, SMNCopyNumberCaller, Spring, stranger, svdb, Tabix, TIDDIT, UPD, UCSC Bigwig and Bigbed, vcf2cytosure, Vcfanno, VerifyBamID2.

Full list with references: https://github.com/nf-core/raredisease/blob/3.1.2/CITATIONS.md

## Demo
```bash
nfclaw run raredisease --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/raredisease/blob/3.1.2/docs/usage.md

<!-- Generated from nf-core/raredisease@83f2699d28bc957e1d3b875da3d96004a818c2c3. Do not edit by hand. -->
