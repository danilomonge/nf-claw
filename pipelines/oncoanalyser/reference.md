---
name: oncoanalyser
version: 2.3.0
commit: 234fd82acc16a3beb01bf301900d83346b6ec812
---

# oncoanalyser — full parameter reference

nf-core/oncoanalyser pipeline parameters. Every parameter from the pinned `nextflow_schema.json`, validated by nf-schema at runtime. `hidden` marks nf-core's generic/boilerplate parameters; `constraints` lists each parameter's declared value bounds (pattern, min/max, length) — conditional or composed rules (e.g. anyOf/oneOf) are enforced by nf-schema at runtime.

## generic_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--email-on-fail` | string |  | yes |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary, only when pipeline fails. |
| `--help` | boolean or string |  |  |  |  |  | Display the help message. |
| `--help-full` | boolean |  |  |  |  |  | Display the full detailed help message. |
| `--hook-url` | string |  | yes |  |  |  | Incoming hook URL for messaging service |
| `--monochrome-logs` | boolean |  | yes |  |  |  | Do not use coloured log outputs. |
| `--pipelines-testdata-base-path` | string |  | yes |  |  | https://raw.githubusercontent.com/nf-core/test-datasets/oncoanalyser | Base URL or local path to location of pipeline test dataset files |
| `--plaintext-email` | boolean |  | yes |  |  |  | Send plain-text email instead of HTML. |
| `--publish-dir-mode` | string |  | yes | symlink, rellink, link, copy, copyNoFollow, move |  | copy | Method used to save pipeline results to output directory. |
| `--show-hidden` | boolean |  |  |  |  |  | Display hidden parameters in the help message (only works when --help or --help_full are provided). |
| `--trace-report-suffix` | string |  | yes |  |  |  | Suffix to add to the trace report filename. Default is the date and time in the format yyyy-MM-dd_HH-mm-ss. |
| `--validate-params` | boolean |  | yes |  |  | true | Boolean whether to validate parameters against the schema at runtime |
| `--version` | boolean |  | yes |  |  |  | Display version and exit. |

## input_output_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--input` | string (file path) |  |  |  | matches ^\S+\.csv$ |  | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) | yes |  |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## institutional_config_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--config-profile-contact` | string |  | yes |  |  |  | Institutional config contact information. |
| `--config-profile-description` | string |  | yes |  |  |  | Institutional config description. |
| `--config-profile-name` | string |  | yes |  |  |  | Institutional config name. |
| `--config-profile-url` | string |  | yes |  |  |  | Institutional config URL link. |
| `--custom-config-base` | string |  | yes |  |  | https://raw.githubusercontent.com/nf-core/configs/master | Base directory for Institutional configs. |
| `--custom-config-version` | string |  | yes |  |  | master | Git commit id for Institutional configs. |

## other_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--create-stub-placeholders` | boolean |  |  |  |  | false | Create placeholders for reference data during stub run. |
| `--driver-gene-panel` | string |  |  |  |  |  | User defined driver gene panel used in panel resource creation, or for overriding the default file located in ref_data_hmf_data_path |
| `--email` | string |  |  |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary. |
| `--fastp-umi-enabled` | boolean |  |  |  |  | false | Enable fastp UMI processing. |
| `--fastp-umi-length` | integer |  |  |  |  | 0 | fastp UMI length parameter (--umi_len) |
| `--fastp-umi-location` | string |  |  |  |  |  | fastp UMI location parameter (--umi_loc). |
| `--fastp-umi-skip` | integer |  |  |  |  | -1 | fastp UMI skip parameter (--umi_skip) |
| `--force-genome` | boolean |  |  |  |  | false | Skip check for restricted genome. |
| `--force-panel` | boolean |  |  |  |  | false | Skip check for known panels. |
| `--gridss-config` | string |  |  |  |  |  | Path to GRIDSS configuration file. |
| `--hmftools-log-level` | string |  |  | ALL, TRACE, DEBUG, INFO, WARN, ERROR, FATAL |  | DEBUG | Log level filter for WiGiTS modules |
| `--isofox-counts` | string |  |  |  |  |  | User defined Isofox expected counts files (read length dependent). |
| `--isofox-functions` | string |  |  |  |  | TRANSCRIPT_COUNTS;ALT_SPLICE_JUNCTIONS;FUSIONS;RETAINED_INTRONS | Semicolon-separated list of Isofox functions to run |
| `--isofox-gc-ratios` | string |  |  |  |  |  | User defined Isofox expected GC ratios file. |
| `--isofox-gene-ids` | string |  |  |  |  |  | User defined Isofox gene list file for panel data. |
| `--isofox-read-length` | integer |  |  |  |  |  | User defined RNA read length used for Isofox. |
| `--isofox-tpm-norm` | string |  |  |  |  |  | User defined Isofox TPM normalisation file for panel data. |
| `--max-fastq-records` | integer |  |  |  |  | 10000000 | When positive, will use fastp to split fastq files so that each resultant fastq file has no more than max_fastq_records records. When nonpositive, fastp is not used and the provided fastq files are passed as-is to the aligner. |
| `--mode` | string |  |  |  | matches ^(wgts\|targeted\|purity_estimate\|panel_resource_creation\|prepare_reference) |  | Workflow run mode. |
| `--panel` | string |  |  |  |  |  | Name of panel to use. |
| `--processes-exclude` | string |  |  |  |  |  | Exclude processes provided as a comma separated list. |
| `--processes-include` | string |  |  |  |  |  | Include processes that are excluded by default, provided as a comma separated list. |
| `--processes-manual` | string |  |  |  |  |  | Manually run processes provided as a comma separated list. |
| `--purity-estimate-mode` | string |  |  |  | matches ^(wgts\|targeted) |  | Purity estimate workflow run mode. |
| `--redux-umi-duplex-delim` | string |  |  |  |  |  | UMI duplex delimiter as used by REDUX. |
| `--redux-umi-enabled` | boolean |  |  |  |  | false | Enable REDUX UMI processing. |
| `--ref-data-types` | string |  |  |  |  |  | Which reference data types to download and extract. |
| `--target-regions-bed` | string |  |  |  |  |  | User defined target regions BED used in panel resource creation. |

## reference_data_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--genome` | string |  |  |  |  |  | Name of genome reference. |
| `--genome-type` | string |  | yes | alt, no_alt |  |  | Type of reference genome. |
| `--genome-version` | string |  | yes | 37, 38, 37, 38 |  |  | Version of reference genome. |
| `--hmf-genomes-base` | string (directory path) |  | yes |  |  | https://pub-cf6ba01919994c3cbd354659947f74d8.r2.dev/genomes | The base path to the HMF genome reference files |
| `--igenomes-base` | string (directory path) |  | yes |  |  | s3://ngi-igenomes/igenomes/ | The base path to the igenomes reference files |
| `--igenomes-ignore` | boolean |  | yes |  |  | true | Do not load the iGenomes reference config. |
| `--prepare-reference-only` | boolean |  | yes |  |  | false |  |
| `--ref-data-genome-bwamem2-index` | string |  |  |  |  |  | Path to reference genome bwa-mem2 index. |
| `--ref-data-genome-dict` | string |  |  |  |  |  | Path to reference genome dict. |
| `--ref-data-genome-fai` | string |  |  |  |  |  | Path to reference genome FAI. |
| `--ref-data-genome-fasta` | string |  |  |  |  |  | Path to reference genome FASTA. |
| `--ref-data-genome-gridss-index` | string |  |  |  |  |  | Path to reference genome GRIDSS index. |
| `--ref-data-genome-gtf` | string |  |  |  |  |  | Path to reference genome GTF. |
| `--ref-data-genome-img` | string |  |  |  |  |  | Path to reference genome img. |
| `--ref-data-genome-star-index` | string |  |  |  |  |  | Path to reference genome STAR index. |
| `--ref-data-hmf-data-path` | string |  |  |  |  |  | Path to HMF data. |
| `--ref-data-panel-data-path` | string |  |  |  |  |  | Path to panel data. |

<!-- Generated from nf-core/oncoanalyser@234fd82acc16a3beb01bf301900d83346b6ec812. Do not edit by hand. -->
