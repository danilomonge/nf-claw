---
name: scrnaseq
pipeline: nf-core/scrnaseq
version: 4.1.0
commit: f7bf36d7c7e4bddc5302c3facd8d19ca83e22226
description: Pipeline for processing 10x Genomics single cell rnaseq data
keywords: [scrnaseq, nf-core, nextflow]
has_samplesheet: true
---
# scrnaseq

Pipeline for processing 10x Genomics single cell rnaseq data

## Run it
```bash
git submodule update --init pipelines/scrnaseq/upstream   # first time only
nfclaw run scrnaseq --input samplesheet.csv --outdir results -profile docker
# raw equivalent:
nextflow run pipelines/scrnaseq/upstream -r 4.1.0 -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required |
|---|---|---|
| `sample` | string | yes |
| `fastq_1` | string | yes |
| `fastq_2` | string | yes |
| `fastq_barcode` | string | no |
| `expected_cells` | integer | no |
| `seq_center` | string | no |
| `sample_type` | string | no |
| `feature_type` | string | no |

Example `samplesheet.csv`:
```csv
sample,fastq_1,fastq_2,fastq_barcode,expected_cells,seq_center,sample_type,feature_type
sample1,data/sample1_fastq_1.gz,data/sample1_fastq_2.gz,value,value,value,value,value
```

## Key parameters
| parameter | type | description |
|---|---|---|
| `--input` | string | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--barcode-whitelist` | string | If not using the 10X Genomics platform, a custom barcode whitelist can be used with `--barcode_whitelist`. |
| `--cellranger-index` | string | Specify a pre-calculated cellranger index. Readily prepared indexes can be obtained from the 10x Genomics website. Provide the base directory of the index (e.g., '/PATH/TO/10X_REF/refdata-gex-GRCh38-2024-A/') |
| `--cellranger-multi-barcodes` | string | Additional samplesheet to provide information about multiplexed samples. See the 'Usage' section for more details. |
| `--cellranger-vdj-index` | string | Specify a pre-built Cell Ranger index for VDJ analysis. |
| `--cellrangerarc-config` | string | Specify a config file to create the cellranger-arc index. |
| `--cellrangerarc-reference` | string | Specify the genome reference name used in the config file to create a cellranger-arc index. |
| `--config-profile-contact` | string | Institutional config contact information. |
| `--config-profile-description` | string | Institutional config description. |
| `--config-profile-name` | string | Institutional config name. |
| `--config-profile-url` | string | Institutional config URL link. |
| `--email` | string | Email address for completion summary. |
| `--email-on-fail` | string | Email address for completion summary, only when pipeline fails. |
| `--fasta` | string | Path to FASTA genome file. |
| `--fb-reference` | string | Provide a reference file for feature barcoding (e.g. antibody measurements). Please refer to the [Cell Ranger Feature Reference documentation](https://www.10xgenomics.com/support/software/cell-ranger/latest/analysis/inputs/cr-feature-ref-csv) for more details. |
| `--genome` | string | Name of iGenomes reference. |
| `--gex-barcode-sample-assignment` | string | This is only necessary to override Cell Ranger's default cell calling and tag calling steps. In most cases, you need to only use the `cellranger_multi_barcodes` parameter. Please refer to the [10x documentation](https://www.10xgenomics.com/support/software/cell-ranger/latest/analysis/running-pipelines/cr-3p-multi#barcode-asst) for more information about this file. |
| `--gex-cmo-set` | string | Provide a Cell Multiplexing Oligo (CMO) description file when working with multiplexed samples. This is only necessary if you with to override Cell Ranger's default CMO-set. Please refer to the [10x documentation](https://www.10xgenomics.com/support/software/cell-ranger/latest/analysis/running-pipelines/cr-3p-multi#cmo-ref) about CMO references for more details. |
| `--gex-frna-probe-set` | string | Provide a probe set for fixed RNA-seq profiling (used with FFPE samples). Please refer to the [10x documentation about probesets](https://www.10xgenomics.com/support/single-cell-gene-expression-flex/documentation/steps/probe-sets/chromium-frp-probe-set-files) for more details. |

## Outputs
Results land in `--outdir`; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions).

## Demo
```bash
nfclaw run scrnaseq --demo --outdir results   # uses upstream -profile test
```

## Full reference
Every parameter: [reference.md](reference.md) · upstream usage: https://github.com/nf-core/scrnaseq/blob/4.1.0/docs/usage.md

<!-- Generated from nf-core/scrnaseq@f7bf36d7c7e4bddc5302c3facd8d19ca83e22226. Do not edit by hand. -->
