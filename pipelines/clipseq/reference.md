---
name: clipseq
version: 1.0.0
commit: 45ae3c0b9b16206b687f4a645e1643c85b3f1ab4
---

# clipseq — full parameter reference

nf-core/clipseq pipeline parameters. Every parameter from the pinned `nextflow_schema.json`, validated by nf-schema at runtime. `hidden` marks nf-core's generic/boilerplate parameters; `constraints` lists each parameter's declared value bounds (pattern, min/max, length) — conditional or composed rules (e.g. anyOf/oneOf) are enforced by nf-schema at runtime.

## adapter_and_umi_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--adapter` | string |  |  |  |  | AGATCGGAAGAGC | Sequencing adapter for trimming |
| `--deduplicate` | boolean |  |  |  |  | true | Deduplicate using UMIs |
| `--move-umi` | string |  |  |  |  | False | UMI format to move to FastQ header (optional) |
| `--umi-separator` | string |  |  |  |  | : | UMI separator in the FastQ read name |

## generic_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--email-on-fail` | string |  | yes |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary, only when pipeline fails. |
| `--help` | boolean |  | yes |  |  |  | Display help text. |
| `--max-multiqc-email-size` | string |  | yes |  |  | 25.MB | File size limit when attaching MultiQC reports to summary emails. |
| `--monochrome-logs` | boolean |  | yes |  |  |  | Do not use coloured log outputs. |
| `--multiqc-config` | string |  | yes |  |  |  | Custom config file to supply to MultiQC. |
| `--plaintext-email` | boolean |  | yes |  |  |  | Send plain-text email instead of HTML. |
| `--publish-dir-mode` | string |  | yes | symlink, rellink, link, copy, copyNoFollow, move |  | copy | Method used to save pipeline results to output directory. |
| `--show-hidden-params` | boolean |  | yes |  |  |  | Show all params when using `--help` |
| `--tracedir` | string |  | yes |  |  | ${params.outdir}/pipeline_info | Directory to keep pipeline Nextflow logs and reports. |
| `--validate-params` | boolean |  | yes |  |  | true | Boolean whether to validate parameters against the schema at runtime |

## input_output_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--email` | string |  |  |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary. |
| `--input` | string | yes |  |  |  |  | Input FastQ files. |
| `--outdir` | string |  |  |  |  | ./results | The output directory where the results will be saved. |

## institutional_config_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--config-profile-contact` | string |  | yes |  |  |  | Institutional config contact information. |
| `--config-profile-description` | string |  | yes |  |  |  | Institutional config description. |
| `--config-profile-name` | string |  | yes |  |  |  | Institutional config name. |
| `--config-profile-url` | string |  | yes |  |  |  | Institutional config URL link. |
| `--custom-config-base` | string |  | yes |  |  | https://raw.githubusercontent.com/nf-core/configs/master | Base directory for Institutional configs. |
| `--custom-config-version` | string |  | yes |  |  | master | Git commit id for Institutional configs. |
| `--hostnames` | string |  | yes |  |  |  | Institutional configs hostname. |

## max_job_request_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--max-cpus` | integer |  | yes |  |  | 16 | Maximum number of CPUs that can be requested for any single job. |
| `--max-memory` | string |  | yes |  | matches ^[\d\.]+\s*.(K\|M\|G\|T)?B$ | 128.GB | Maximum amount of memory that can be requested for any single job. |
| `--max-time` | string |  | yes |  | matches ^[\d\.]+\.*(s\|m\|h\|d)$ | 240.h | Maximum amount of time that can be requested for any single job. |

## motif_finding

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--motif` | boolean |  |  |  |  |  | Perform motif finding |
| `--motif-sample` | integer |  |  |  |  | 1000 | Sample n peaks for motif finding |

## peak_calling_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--bin-size-both` | integer |  |  |  |  | 3 | Piranha bin size |
| `--cluster-dist` | integer |  |  |  |  | 3 | Piranha clustering distance |
| `--half-window` | integer |  |  |  |  | 3 | iCount half-window setting |
| `--max-cluster-length` | integer |  |  |  |  | 200 | Paraclu maximum cluster length |
| `--merge-window` | integer |  |  |  |  | 3 | iCount merge-window setting |
| `--min-density-increase` | integer |  |  |  |  | 2 | Paraclu minimum density increase |
| `--min-value` | integer |  |  |  |  | 10 | Paraclu minimum cluster count |
| `--peakcaller` | string |  |  |  |  |  | Which peakcaller(s) to use |
| `--pureclip-bc` | integer |  |  |  |  | 0 | PureCLIP binding characteristics of protein |
| `--pureclip-dm` | integer |  |  |  |  | 8 | PureCLIP merge distance |
| `--pureclip-iv` | string |  |  |  |  | all | PureCLIP chromosomes for HMM training |
| `--segment` | string |  |  |  |  |  | Path to iCount segment file |

## reference_genome_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--fai` | string |  |  |  |  |  | Path to genome FASTA index file |
| `--fasta` | string |  |  |  |  |  | Path to genome FASTA file. |
| `--genome` | string |  |  |  |  |  | Name of iGenomes reference. |
| `--gtf` | string |  |  |  |  |  | Path to GTF annotation file |
| `--igenomes-base` | string |  | yes |  |  | s3://ngi-igenomes/igenomes/ | Directory / URL base for iGenomes references. |
| `--igenomes-ignore` | boolean |  | yes |  |  |  | Do not load the iGenomes reference config. |
| `--save-index` | boolean |  |  |  |  |  | Save STAR index if generated within pipeline. |
| `--smrna-fasta` | string |  |  |  |  |  | Path to small RNA FASTA file |
| `--smrna-org` | string |  |  |  |  |  | Organism for small RNA reference. |
| `--star-index` | string |  |  |  |  |  | Path to genome STAR index |

<!-- Generated from nf-core/clipseq@45ae3c0b9b16206b687f4a645e1643c85b3f1ab4. Do not edit by hand. -->
