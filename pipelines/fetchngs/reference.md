---
name: fetchngs
version: 1.12.0
commit: 8ec2d934f9301c818d961b1e4fdf7fc79610bdc5
---

# fetchngs — full parameter reference

nf-core/fetchngs pipeline parameters. Every parameter from the pinned `nextflow_schema.json`, validated by nf-schema at runtime. `hidden` marks nf-core's generic/boilerplate parameters; `constraints` lists the value bounds the schema enforces (pattern, min/max, length).

## deprecated_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--force-sratools-download` | boolean |  | yes | False |  |  | This parameter has been deprecated. Please use '--download_method sratools' instead. |

## generic_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--email-on-fail` | string |  | yes |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary, only when pipeline fails. |
| `--help` | boolean |  | yes |  |  |  | Display help text. |
| `--hook-url` | string |  | yes |  |  |  | Incoming hook URL for messaging service |
| `--monochrome-logs` | boolean |  | yes |  |  |  | Do not use coloured log outputs. |
| `--plaintext-email` | boolean |  | yes |  |  |  | Send plain-text email instead of HTML. |
| `--publish-dir-mode` | string |  | yes | symlink, rellink, link, copy, copyNoFollow, move |  | copy | Method used to save pipeline results to output directory. |
| `--validate-params` | boolean |  | yes |  |  | True | Boolean whether to validate parameters against the schema at runtime |
| `--validationFailUnrecognisedParams` | boolean |  | yes |  |  |  | Validation of parameters fails when an unrecognised parameter is found. |
| `--validationLenientMode` | boolean |  | yes |  |  |  | Validation of parameters in lenient more. |
| `--validationShowHiddenParams` | boolean |  | yes |  |  |  | Show all params when using `--help` |
| `--version` | boolean |  | yes |  |  |  | Display version and exit. |

## input_output_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--dbgap-key` | string (file path) |  |  |  |  |  | dbGaP repository key. |
| `--download-method` | string |  |  | aspera, ftp, sratools |  | ftp | Method to download FastQ files. Available options are 'aspera', 'ftp' or 'sratools'. Default is 'ftp'. |
| `--email` | string |  |  |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary. |
| `--ena-metadata-fields` | string |  |  |  |  |  | Comma-separated list of ENA metadata fields to fetch before downloading data. |
| `--input` | string (file path) | yes |  |  | matches ^\S+\.(csv\|tsv\|txt)$ |  | File containing SRA/ENA/GEO/DDBJ identifiers one per line to download their associated metadata and FastQ files. |
| `--nf-core-pipeline` | string |  |  | rnaseq, atacseq, viralrecon, taxprofiler |  |  | Name of supported nf-core pipeline e.g. 'rnaseq'. A samplesheet for direct use with the pipeline will be created with the appropriate columns. |
| `--nf-core-rnaseq-strandedness` | string |  |  |  |  | auto | Value for 'strandedness' entry added to samplesheet created when using '--nf_core_pipeline rnaseq'. |
| `--outdir` | string (directory path) | yes |  |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--sample-mapping-fields` | string |  |  |  |  | experiment_accession,run_accession,sample_accession,experiment_alias,run_alias,sample_alias,experiment_title,sample_title,sample_description | Comma-separated list of ENA metadata fields used to create a separate 'id_mappings.csv' and 'multiqc_config.yml' with selected fields that can be used to rename samples in general and in MultiQC. |
| `--skip-fastq-download` | boolean |  |  |  |  |  | Only download metadata for public data database ids and don't download the FastQ files. |

## institutional_config_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--config-profile-contact` | string |  | yes |  |  |  | Institutional config contact information. |
| `--config-profile-description` | string |  | yes |  |  |  | Institutional config description. |
| `--config-profile-name` | string |  | yes |  |  |  | Institutional config name. |
| `--config-profile-url` | string |  | yes |  |  |  | Institutional config URL link. |
| `--custom-config-base` | string |  | yes |  |  | https://raw.githubusercontent.com/nf-core/configs/master | Base directory for Institutional configs. |
| `--custom-config-version` | string |  | yes |  |  | master | Git commit id for Institutional configs. |

## max_job_request_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--max-cpus` | integer |  | yes |  |  | 16 | Maximum number of CPUs that can be requested for any single job. |
| `--max-memory` | string |  | yes |  | matches ^\d+(\.\d+)?\.?\s*(K\|M\|G\|T)?B$ | 128.GB | Maximum amount of memory that can be requested for any single job. |
| `--max-time` | string |  | yes |  | matches ^(\d+\.?\s*(s\|m\|h\|d\|day)\s*)+$ | 240.h | Maximum amount of time that can be requested for any single job. |

<!-- Generated from nf-core/fetchngs@8ec2d934f9301c818d961b1e4fdf7fc79610bdc5. Do not edit by hand. -->
