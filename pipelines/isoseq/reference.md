---
name: isoseq
version: 2.0.0
commit: c7536ab0e18a27460476d4e8557845950292f070
---

# isoseq — full parameter reference

nf-core/isoseq pipeline parameters. Every parameter from the pinned `nextflow_schema.json`, validated by nf-schema at runtime. `hidden` marks nf-core's generic/boilerplate parameters; `constraints` lists each parameter's declared value bounds (pattern, min/max, length) — conditional or composed rules (e.g. anyOf/oneOf) are enforced by nf-schema at runtime.

## aligner_option

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--aligner` | string | yes |  | minimap2, ultra |  |  | Aligner to use for mapping: minimap2 or ultra |

## ccs_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--max-length` | integer |  |  |  |  | 50000 | ccs --max-length option, maximum CCS length for CCS selection |
| `--min-length` | integer |  |  |  |  | 10 | ccs --min-length option, minimum CCS length for CCS selection |
| `--min-passes` | integer |  |  |  |  | 3 | ccs --min-passes option, define the minimum number of passes to select a CCS |
| `--min-snr` | number |  |  |  |  | 2.5 | ccs --min-snr option, minimum SNR of subreads to use for generating CCS |
| `--rq` | number |  |  |  |  | 0.9 | ccs --rq option, define the minimum read quality for CCS selection |
| `--top-passes` | integer |  |  |  |  | 60 | ccs --top-passes option, maximum number of passes to use for CCS generation |

## generic_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--email-on-fail` | string |  | yes |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary, only when pipeline fails. |
| `--help` | boolean |  | yes |  |  |  | Display help text. |
| `--hook-url` | string |  | yes |  |  |  | Incoming hook URL for messaging service |
| `--max-multiqc-email-size` | string |  | yes |  | matches ^\d+(\.\d+)?\.?\s*(K\|M\|G\|T)?B$ | 25.MB | File size limit when attaching MultiQC reports to summary emails. |
| `--monochrome-logs` | boolean |  | yes |  |  |  | Do not use coloured log outputs. |
| `--multiqc-config` | string (file path) |  | yes |  |  |  | Custom config file to supply to MultiQC. |
| `--multiqc-logo` | string |  | yes |  |  |  | Custom logo file to supply to MultiQC. File name must also be set in the MultiQC config file |
| `--multiqc-methods-description` | string |  |  |  |  |  | Custom MultiQC yaml file containing HTML including a methods description. |
| `--pipelines-testdata-base-path` | string |  | yes |  |  | https://raw.githubusercontent.com/nf-core/test-datasets/ | Base URL or local path to location of pipeline test dataset files |
| `--plaintext-email` | boolean |  | yes |  |  |  | Send plain-text email instead of HTML. |
| `--publish-dir-mode` | string |  | yes | symlink, rellink, link, copy, copyNoFollow, move |  | copy | Method used to save pipeline results to output directory. |
| `--validate-params` | boolean |  | yes |  |  | true | Boolean whether to validate parameters against the schema at runtime |
| `--validationFailUnrecognisedParams` | boolean |  | yes |  |  |  | Validation of parameters fails when an unrecognised parameter is found. |
| `--validationLenientMode` | boolean |  | yes |  |  |  | Validation of parameters in lenient more. |
| `--validationShowHiddenParams` | boolean |  | yes |  |  |  | Show all params when using `--help` |
| `--version` | boolean |  | yes |  |  |  | Display version and exit. |

## input_output_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--chunk` | integer |  |  |  |  | 40 | If entrypoint 'isoseq', ccs --chunk option, define the number of batches to run in parallel. If entrypoint 'map', split fasta in files of 'chunk' sequences. |
| `--email` | string |  |  |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary. |
| `--entrypoint` | string |  |  | isoseq, map |  | isoseq | Run complete pipeline or TAMA only? |
| `--gtf` | string |  |  |  |  |  | Genome annotation file |
| `--input` | string (file path) | yes |  |  | matches ^\S+\.csv$ |  | Path to comma-separated file containing information about the samples in the experiment. |
| `--multiqc-title` | string |  |  |  |  |  | MultiQC report title. Printed as page header, used for filename if not otherwise specified. |
| `--outdir` | string (directory path) | yes |  |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--primers` | string | yes |  |  |  |  | Fasta file of primers sequences |

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

## reference_genome_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--fasta` | string (file path) |  |  |  | matches ^\S+\.fn?a(sta)?(\.gz)?$ |  | Path to FASTA genome file. |
| `--genome` | string |  |  |  |  |  | Name of iGenomes reference. |
| `--igenomes-ignore` | boolean |  | yes |  |  |  | Do not load the iGenomes reference config. |

## tama_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--capped` | boolean |  |  |  |  |  | TAMA collapse: Capped RNA? |
| `--five-prime` | integer |  |  |  |  | 100 | TAMA collapse: 5 prime wobble threshold |
| `--splice-junction` | integer |  |  |  |  | 10 | TAMA collapse: Splice junction / exon wobble threshold |
| `--three-prime` | integer |  |  |  |  | 100 | TAMA collapse: 3 prime wobble threshold |

<!-- Generated from nf-core/isoseq@c7536ab0e18a27460476d4e8557845950292f070. Do not edit by hand. -->
