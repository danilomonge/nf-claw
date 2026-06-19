---
name: demultiplex
version: 1.7.1
commit: fbec8e442f0599f8b74876e62263af05b9a41d33
---

# demultiplex — full parameter reference

nf-core/demultiplex pipeline parameters. Every parameter from the pinned `nextflow_schema.json`, validated by nf-schema at runtime. `hidden` marks nf-core's generic/boilerplate parameters; `constraints` lists each parameter's declared value bounds (pattern, min/max, length) — conditional or composed rules (e.g. anyOf/oneOf) are enforced by nf-schema at runtime.

## checkqc_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--checkqc-config` | string (file path) |  |  |  |  |  | Path to the checkqc config yml file. |

## demultiplex_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--demultiplexer` | string | yes |  | bases2fastq, bcl2fastq, bclconvert, fqtk, sgdemux, mkfastq, mgikit |  | bclconvert | Demultiplexer to use. |

## downstream_csv_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--strandedness` | string |  |  | unstranded, auto, reverse, forward |  | auto | Specifies the strandedness of RNA-Seq data for downstream sample sheet generation. This parameter does not affect the demultiplexing process but is used to generate the appropriate field in the nf-core/rnaseq samplesheet |

## generic_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--email-on-fail` | string |  | yes |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary, only when pipeline fails. |
| `--help` | boolean or string |  |  |  |  |  | Display the help message. |
| `--help-full` | boolean |  |  |  |  |  | Display the full detailed help message. |
| `--hook-url` | string |  | yes |  |  |  | Incoming hook URL for messaging service |
| `--max-multiqc-email-size` | string |  | yes |  | matches ^\d+(\.\d+)?\.?\s*(K\|M\|G\|T)?B$ | 25.MB | File size limit when attaching MultiQC reports to summary emails. |
| `--monochrome-logs` | boolean |  | yes |  |  |  | Do not use coloured log outputs. |
| `--multiqc-config` | string (file path) |  | yes |  |  |  | Custom config file to supply to MultiQC. |
| `--multiqc-logo` | string (file path) |  | yes |  |  |  | Custom logo file to supply to MultiQC. File name must also be set in the MultiQC config file |
| `--multiqc-methods-description` | string (file path) |  |  |  |  |  | Custom MultiQC yaml file containing HTML including a methods description. |
| `--pipelines-testdata-base-path` | string |  | yes |  |  | https://raw.githubusercontent.com/nf-core/test-datasets/ | Base URL or local path to location of pipeline test dataset files |
| `--plaintext-email` | boolean |  | yes |  |  |  | Send plain-text email instead of HTML. |
| `--publish-dir-mode` | string |  | yes | symlink, rellink, link, copy, copyNoFollow, move |  | copy | Method used to save pipeline results to output directory. |
| `--remove-samplesheet-adapter` | boolean |  |  |  |  | true | Boolean whether to remove adapter information from Illumina samplesheet. If adapter information is present, the various bcl conversion tools will perform adapter trimming already at the demultiplexing step. |
| `--show-hidden` | boolean |  |  |  |  |  | Display hidden parameters in the help message (only works when --help or --help_full are provided). |
| `--trace-report-suffix` | string |  | yes |  |  |  | Suffix to add to the trace report filename. Default is the date and time in the format yyyy-MM-dd_HH-mm-ss. |
| `--validate-params` | boolean |  | yes |  |  | true | Boolean whether to validate parameters against the schema at runtime |
| `--version` | boolean |  | yes |  |  |  | Display version and exit. |

## input_output_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--email` | string |  |  |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary. |
| `--flowcell-id` | string |  |  |  |  |  | Flowcell ID for single-flowcell runs. |
| `--flowcell-lane` | integer |  |  |  | ≥ 1; ≤ 8 |  | Lane number for single-flowcell runs. |
| `--flowcell-path` | string |  |  |  |  |  | Run directory (or tar.gz) for single-flowcell runs. |
| `--flowcell-per-flowcell-manifest` | string (file path) |  |  |  | matches ^\S+\.csv$ |  | Per-flowcell manifest file for fqtk single-flowcell runs. |
| `--flowcell-samplesheet` | string (file path) |  |  |  | matches ^\S+\.csv$ |  | Path to the flowcell SampleSheet.csv for single-flowcell runs. |
| `--input` | string (file path) |  |  |  | matches ^\S+\.csv$ |  | Path to comma-separated file containing information about the samples in the experiment. |
| `--multiqc-title` | string |  |  |  |  |  | MultiQC report title. Printed as page header, used for filename if not otherwise specified. |
| `--optional-outputs` | boolean |  |  |  |  |  | Whether to publish optional outputs such as undertermined files. |
| `--outdir` | string (directory path) | yes |  |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## institutional_config_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--config-profile-contact` | string |  | yes |  |  |  | Institutional config contact information. |
| `--config-profile-description` | string |  | yes |  |  |  | Institutional config description. |
| `--config-profile-name` | string |  | yes |  |  |  | Institutional config name. |
| `--config-profile-url` | string |  | yes |  |  |  | Institutional config URL link. |
| `--custom-config-base` | string (directory path) |  | yes |  |  | https://raw.githubusercontent.com/nf-core/configs/master | Base directory for Institutional configs. |
| `--custom-config-version` | string |  | yes |  |  | master | Git commit id for Institutional configs. |

## workflow_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--file-schema-validator` | string (file path) |  |  |  |  |  | Local JSON file to be passed to samshee module for samplesheet validation |
| `--json-schema-validator` | string |  |  |  |  |  | String in JSON format to be passed to samshee module for samplesheet validation |
| `--kraken-db` | string |  |  |  |  |  | Path to Kraken2 DB to use for screening |
| `--name-schema-validator` | string |  |  |  |  |  | Schema name to be passed to samshee module for samplesheet validation |
| `--sample-size` | integer |  |  |  |  | 100000 | Number of reads to subsample for contamination detection. |
| `--skip-tools` | string |  |  |  | matches ^((fastp\|fastqc\|kraken\|multiqc\|checkqc\|falco\|md5sum\|samshee)?,?)*(?<!,)$ |  | Comma-separated list of tools to skip (fastp,fastqc,kraken,multiqc,checkqc,falco,md5sum,samshee) |
| `--trim-fastq` | boolean |  |  |  |  | true | Whether or not to skip trimming |
| `--v1-schema` | boolean |  |  |  |  |  | Whether or not illumina samplesheet is v1 |

<!-- Generated from nf-core/demultiplex@fbec8e442f0599f8b74876e62263af05b9a41d33. Do not edit by hand. -->
