---
name: phyloplace
version: 2.0.1
commit: 3e37f9d7aa8d9fcca04a4d9661b8cffdb25027fa
---

# phyloplace — full parameter reference

nf-core/phyloplace pipeline parameters. Every parameter from the pinned `nextflow_schema.json`, validated by nf-schema at runtime. `hidden` marks nf-core's generic/boilerplate parameters; `constraints` lists each parameter's declared value bounds (pattern, min/max, length) — conditional or composed rules (e.g. anyOf/oneOf) are enforced by nf-schema at runtime.

## generic_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--email-on-fail` | string |  | yes |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary, only when pipeline fails. |
| `--help` | boolean or string |  |  |  |  |  | Display the help message. |
| `--help-full` | boolean |  |  |  |  |  | Display the full detailed help message. |
| `--max-multiqc-email-size` | string |  | yes |  | matches ^\d+(\.\d+)?\.?\s*(K\|M\|G\|T)?B$ | 25.MB | File size limit when attaching MultiQC reports to summary emails. |
| `--monochrome-logs` | boolean |  | yes |  |  |  | Do not use coloured log outputs. |
| `--multiqc-config` | string (file path) |  | yes |  |  |  | Custom config file to supply to MultiQC. |
| `--multiqc-logo` | string |  | yes |  |  |  | Custom logo file to supply to MultiQC. File name must also be set in the MultiQC config file |
| `--multiqc-methods-description` | string |  |  |  |  |  | Custom MultiQC yaml file containing HTML including a methods description. |
| `--pipelines-testdata-base-path` | string |  | yes |  |  | https://raw.githubusercontent.com/nf-core/test-datasets/ | Base URL or local path to location of pipeline test dataset files |
| `--plaintext-email` | boolean |  | yes |  |  |  | Send plain-text email instead of HTML. |
| `--publish-dir-mode` | string |  | yes | symlink, rellink, link, copy, copyNoFollow, move |  | copy | Method used to save pipeline results to output directory. |
| `--show-hidden` | boolean |  |  |  |  |  | Display hidden parameters in the help message (only works when --help or --help_full are provided). |
| `--trace-report-suffix` | string |  | yes |  |  |  | Suffix to add to the trace report filename. Default is the date and time in the format yyyy-MM-dd_HH-mm-ss. |
| `--validate-params` | boolean |  | yes |  |  | true | Boolean whether to validate parameters against the schema at runtime |
| `--version` | boolean |  | yes |  |  |  | Display version and exit. |

## input_output_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--alignmethod` | string |  |  | hmmer, clustalo, mafft |  | hmmer | Method used to align query sequences with. |
| `--email` | string |  |  |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary. |
| `--hmmfile` | string (file path) |  |  |  |  |  | HMM file. If provided, will be used to align both the reference and query sequences. |
| `--id` | string |  |  |  |  | placement | Name of analysis |
| `--model` | string |  |  |  |  |  | Evolutionary model to use for placement, e.g. 'LG'. |
| `--multiqc-title` | string |  |  |  |  |  | MultiQC report title. Printed as page header, used for filename if not otherwise specified. |
| `--outdir` | string (directory path) | yes |  |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--phyloplace-input` | string (file path) |  |  |  | matches ^\S+\.csv$ |  | Path to comma-separated file containing information about phylogenetic placements to perform. |
| `--phylosearch-input` | string (file path) |  |  |  | matches ^\S+\.csv$ |  | Path to comma-separated file containing information about phylogenetic searches to perform. |
| `--queryseqfile` | string (file path) |  |  |  |  |  | Fasta file with query sequences |
| `--refphylogeny` | string (file path) |  |  |  |  |  | Newick file with aligned reference sequences. |
| `--refseqfile` | string (file path) |  |  |  |  |  | File with reference sequences. Any format supported by HMMER tools. |
| `--search-fasta` | string (file path) |  |  |  |  |  | Fasta file with sequences to be searched with HMM profiles. |
| `--taxonomy` | string (file path) |  |  |  | matches ^\S+\.tsv$ |  | Tab-separated file with taxonomy assignments of reference sequences. |

## institutional_config_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--config-profile-contact` | string |  | yes |  |  |  | Institutional config contact information. |
| `--config-profile-description` | string |  | yes |  |  |  | Institutional config description. |
| `--config-profile-name` | string |  | yes |  |  |  | Institutional config name. |
| `--config-profile-url` | string |  | yes |  |  |  | Institutional config URL link. |
| `--custom-config-base` | string |  | yes |  |  | https://raw.githubusercontent.com/nf-core/configs/master | Base directory for Institutional configs. |
| `--custom-config-version` | string |  | yes |  |  | master | Git commit id for Institutional configs. |

<!-- Generated from nf-core/phyloplace@3e37f9d7aa8d9fcca04a4d9661b8cffdb25027fa. Do not edit by hand. -->
