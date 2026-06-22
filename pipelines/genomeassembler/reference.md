---
name: genomeassembler
version: 1.1.0
commit: ccf1b89898cb720f46a966029c3a60dbcc25b012
---

# genomeassembler — full parameter reference

nf-core/genomeassembler pipeline parameters. Every parameter from the pinned `nextflow_schema.json`, validated by nf-schema at runtime. `hidden` marks nf-core's generic/boilerplate parameters; `constraints` lists each parameter's declared value bounds (pattern, min/max, length) — conditional or composed rules (e.g. anyOf/oneOf) are enforced by nf-schema at runtime.

## annotations_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--lift-annotations` | boolean |  |  |  |  | true | Lift-over annotations (requires reference)? |

## assembly_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--assembler` | string |  |  | flye, hifiasm, flye_on_hifiasm, hifiasm_on_hifiasm |  | flye | Assembler to use. Valid choices are: `'hifiasm'`, `'flye'`, `'flye_on_hifiasm'` or `hifiasm_on_hifiasm`. `flye_on_hifiasm` will scaffold flye assembly (ont) on hifiasm (hifi) assembly using ragtag. `hifiasm_on_hifiasm` will scaffold hifiasm (ont) onto hifiasm (HiFi) using ragtag |
| `--flye-args` | string |  |  |  |  |  | additional args for flye |
| `--flye-mode` | string |  |  | --pacbio-raw, --pacbio-corr, --pacbio-hifi, --nano-raw, --nano-corr, --nano-hq |  | --nano-hq | flye mode |
| `--genome-size` | integer |  |  |  | ≥ 1 |  | expected genome size, optional |
| `--hifiasm-args` | string |  |  |  |  |  | Extra arguments passed to `hifiasm` |
| `--hifiasm-ont` | boolean |  |  |  |  |  | Use hifi and ONT reads with `hifiasm --ul` |

## general_parameters

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--skip-alignments` | boolean |  |  |  |  |  | skip alignments during qc |
| `--skip-assembly` | boolean |  |  |  |  |  | skip assembly steps |
| `--use-ref` | boolean |  |  |  |  | true | use reference genome |

## generic_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--email-on-fail` | string |  | yes |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary, only when pipeline fails. |
| `--hook-url` | string |  | yes |  |  |  | Incoming hook URL for messaging service |
| `--monochrome-logs` | boolean |  | yes |  |  |  | Do not use coloured log outputs. |
| `--pipelines-testdata-base-path` | string |  | yes |  |  | https://raw.githubusercontent.com/nf-core/test-datasets/ | Base URL or local path to location of pipeline test dataset files |
| `--plaintext-email` | boolean |  | yes |  |  |  | Send plain-text email instead of HTML. |
| `--publish-dir-mode` | string |  | yes | symlink, rellink, link, copy, copyNoFollow, move |  | copy | Method used to save pipeline results to output directory. |
| `--validate-params` | boolean |  | yes |  |  | true | Boolean whether to validate parameters against the schema at runtime |
| `--version` | boolean |  | yes |  |  |  | Display version and exit. |

## hifi_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--hifi` | boolean |  |  |  |  |  | HiFi reads available? |
| `--lima` | boolean |  |  |  |  |  | run lima on HiFi reads? |
| `--pacbio-primers` | string (file path) |  |  |  | matches ^\S+\.fn?a(sta)?$ |  | file containing pacbio primers for trimming with lima |

## input_output_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--email` | string |  |  |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary. |
| `--input` | string (file path) | yes |  |  | matches ^\S+\.csv$ |  | Path to comma-separated file containing information about the samples in the experiment. |
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

## ont_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--collect` | boolean |  |  |  |  |  | collect ONT reads into a single file |
| `--dump` | boolean |  |  |  |  |  | dump jellyfish output |
| `--jellyfish` | boolean |  |  |  |  | true | run jellyfish on ONT reads to compute k-mer distribution and estimate genome size |
| `--kmer-length` | integer |  |  |  | ≥ 1 | 21 | kmer length to be used for jellyfish |
| `--ont` | boolean |  |  |  |  |  | ONT reads available? |
| `--porechop` | boolean |  |  |  |  |  | run porechop on ONT reads |
| `--read-length` | integer |  |  |  | ≥ 1 |  | read length for genomescope (ONT only) |

## polishing_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--medaka-model` | string |  |  |  |  |  | model to use with medaka |
| `--polish-medaka` | boolean |  |  |  |  |  | Polish assembly with medaka (ONT only) |
| `--polish-pilon` | boolean |  |  |  |  |  | Polish assembly with pilon? Requires short reads |

## qc_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--busco` | boolean |  |  |  |  | true | Run BUSCO? |
| `--busco-db` | string (directory path) |  |  |  |  |  | Path to busco db (optional) |
| `--busco-lineage` | string |  |  |  |  | brassicales_odb10 | Busco lineage to use |
| `--merqury` | boolean |  |  |  |  | true | Run merqury |
| `--qc-reads` | string |  |  | ONT, HIFI |  | ONT | Long reads that should be used for QC when both ONT and HiFi reads are provided. Options are `'ONT'` or `'HIFI'` |
| `--quast` | boolean |  |  |  |  | true | Run quast |

## scaffolding_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--scaffold-links` | boolean |  |  |  |  |  | Scaffolding with links? |
| `--scaffold-longstitch` | boolean |  |  |  |  |  | Scaffold with longstitch? |
| `--scaffold-ragtag` | boolean |  |  |  |  |  | Scaffold with ragtag (requires reference)? |

## short_read_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--meryl-k` | integer |  |  |  | ≥ 1 | 21 | kmer length for meryl / merqury |
| `--short-reads` | boolean |  |  |  |  |  | Short reads available? |
| `--trim-short-reads` | boolean |  |  |  |  | true | trim short reads with trimgalore |

<!-- Generated from nf-core/genomeassembler@ccf1b89898cb720f46a966029c3a60dbcc25b012. Do not edit by hand. -->
