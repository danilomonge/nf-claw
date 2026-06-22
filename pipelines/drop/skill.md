---
name: drop
pipeline: nf-core/drop
version: 1.0.0
commit: 20388350d242746f8e799b28c3ae80421627b077
description: The detection of RNA Outliers Pipeline (DROP) is an integrative workflow to detect aberrant expression, aberrant splicing, and mono-allelic expression from raw sequencing files.
has_samplesheet: true
input: samplesheet (RNA_ID, RNA_BAM_FILE, RNA_BAI_FILE, DNA_ID, DNA_VCF_FILE, DNA_TBI_FILE, DROP_GROUP, PAIRED_END, COUNT_MODE, COUNT_OVERLAPS, STRAND, HPO_TERMS, GENE_COUNTS_FILE, GENE_ANNOTATION, GENOME, SPLICE_COUNTS_DIR, SEX, TISSUE, DISEASE)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
---
# drop

The detection of RNA Outliers Pipeline (DROP) is an integrative workflow to detect aberrant expression, aberrant splicing, and mono-allelic expression from raw sequencing files.

## Run it
```bash
git submodule update --init pipelines/drop/upstream   # first time only
nfclaw run drop --input samplesheet.csv --outdir results --genome <genome> -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/drop/upstream -profile docker --input samplesheet.csv --outdir results --genome <genome>
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `RNA_ID` | string or integer | yes |  | matches ^\S+$ |
| `RNA_BAM_FILE` | string (file path) | no |  | matches ^\S+\.(bam\|cram)$ |
| `RNA_BAI_FILE` | string (file path) | no |  | matches ^\S+\.(bam\|cram)\.(bai\|crai)$ |
| `DNA_ID` | string or integer | no |  | matches ^\S+$ |
| `DNA_VCF_FILE` | string (file path) | no |  | matches ^\S+\.vcf.gz$ |
| `DNA_TBI_FILE` | string (file path) | no |  | matches ^\S+\.vcf.gz.tbi$ |
| `DROP_GROUP` | string | yes |  | matches ^\S+$ |
| `PAIRED_END` | boolean | no |  |  |
| `COUNT_MODE` | string | no | union, IntersectionStrict, IntersectionNotEmpty |  |
| `COUNT_OVERLAPS` | boolean | no |  |  |
| `STRAND` | string | yes | yes, no, reverse |  |
| `HPO_TERMS` | string | no |  |  |
| `GENE_COUNTS_FILE` | string (file path) | no |  | matches ^\S+\.tsv(\.gz)?$ |
| `GENE_ANNOTATION` | string | no |  |  |
| `GENOME` | string | no | ncbi, ucsc |  |
| `SPLICE_COUNTS_DIR` | string | no |  | matches ^\S+$ |
| `SEX` | string | no |  |  |
| `TISSUE` | string | no |  |  |
| `DISEASE` | string | no |  |  |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
RNA_ID,RNA_BAM_FILE,RNA_BAI_FILE,DNA_ID,DNA_VCF_FILE,DNA_TBI_FILE,DROP_GROUP,PAIRED_END,COUNT_MODE,COUNT_OVERLAPS,STRAND,HPO_TERMS,GENE_COUNTS_FILE,GENE_ANNOTATION,GENOME,SPLICE_COUNTS_DIR,SEX,TISSUE,DISEASE
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.tsv$ | Path to the samplesheet file used by the pipeline. The file should be a TSV file. Equivalent to the `sampleAnnotation` parameter in the snakemake pipeline. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. Equivalent to the `root` parameter in the snakemake pipeline. |
| `--genome` | string | hg19, hs37d5 , hg38, GRCh38 |  | Equivalent to the `genomeAssembly` parameter in the snakemake pipeline. Either hg19/hs37d5 or hg38/GRCh38, depending on the genome assembly used for mapping |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `aberrant_expression` (11 parameters)
- `aberrant_splicing` (18 parameters)
- `export_counts` (2 parameters)
- `generic_options` (18 parameters)
- `input_output_options` (8 parameters)
- `institutional_config_options` (6 parameters)
- `mono_allelic_expression` (18 parameters)
- `reference_genome_options` (2 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/drop/blob/1.0.0/docs/output.md

## Demo
```bash
nfclaw run drop --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/drop/blob/1.0.0/docs/usage.md

<!-- Generated from nf-core/drop@20388350d242746f8e799b28c3ae80421627b077. Do not edit by hand. -->
