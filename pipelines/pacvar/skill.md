---
name: pacvar
pipeline: nf-core/pacvar
version: 1.1.0
commit: 20364830237171928c79e59651142460379d1459
description: A variant caller for PacBio long read sequencing - also can be used for PureTarget panel analysis, and quantification of repeat expansions
summary: nf-core/pacvar is a bioinformatics pipeline that processes long-read PacBio data. Specifically, the pipeline provides two workflows: one for processing whole-genome sequencing data, and another for processing reads from the PureTarget expansion panel offered by PacBio. This second workflow characterizes tandem repeats. Because the pipeline is designed for PacBio reads, it uses PacBio’s officially released tools.
has_samplesheet: true
input: samplesheet (sample, bam, pbi, fail, repeat_id, karyotype)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, MultiQC, lima, pbmm2, SAMtools, deepvariant, HaplotypeCaller, bcftools, HiPhase, pbsv, HiFiCNV, TRGT, pb-CpG-tools / alignedbamtocpgscores, Sawfish, pbbam / pbmerge, Ensembl VEP
---
# pacvar

nf-core/pacvar is a bioinformatics pipeline that processes long-read PacBio data. Specifically, the pipeline provides two workflows: one for processing whole-genome sequencing data, and another for processing reads from the PureTarget expansion panel offered by PacBio. This second workflow characterizes tandem repeats. Because the pipeline is designed for PacBio reads, it uses PacBio’s officially released tools.

## Run it
```bash
git submodule update --init pipelines/pacvar/upstream   # first time only
nfclaw run pacvar --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/pacvar/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions pacvar` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show pacvar --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string or integer | yes |  | matches ^\S+$ |
| `bam` | string (file path) | yes |  | matches ^\S+\.(bam\|cram)$ |
| `pbi` | string (file path) | no |  | matches ^\S+\.(bai\|crai\|pbi)$ |
| `fail` | string (file path) | no |  | matches ^\S+\.(bam\|cram)$ |
| `repeat_id` | string | no |  |  |
| `karyotype` | string | no | XX, XY |  |

`--input` must match `^\S+\.(csv|tsv|json|yaml|yml)$`.

For tabular CSV/TSV input, use this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,bam,pbi,fail,repeat_id,karyotype
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.(csv\|tsv\|json\|yaml\|yml)$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `annotation` (6 parameters)
- `general_workflow_options` (1 parameter)
- `generic_options` (15 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `methylation_profiling` (3 parameters)
- `pre_processing` (3 parameters)
- `reference_genome_options` (13 parameters)
- `repeat` (1 parameter)
- `variant` (8 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/pacvar/blob/1.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, MultiQC, lima, pbmm2, SAMtools, deepvariant, HaplotypeCaller, bcftools, HiPhase, pbsv, HiFiCNV, TRGT, pb-CpG-tools / alignedbamtocpgscores, Sawfish, pbbam / pbmerge, Ensembl VEP.

Full list with references: https://github.com/nf-core/pacvar/blob/1.1.0/CITATIONS.md

## Demo
```bash
nfclaw run pacvar --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/pacvar/blob/1.1.0/docs/usage.md

<!-- Generated from nf-core/pacvar@20364830237171928c79e59651142460379d1459. Do not edit by hand. -->
