---
name: cageseq
version: 1.0.2
commit: 838d2a5165edb86439d7ff0400bd385d6bcf6927
---

# cageseq — full parameter reference

nf-core/cageseq pipeline parameters. Every parameter from the pinned `nextflow_schema.json`, validated by nf-schema at runtime. `hidden` marks nf-core's generic/boilerplate parameters; `constraints` lists each parameter's declared value bounds (pattern, min/max, length) — conditional or composed rules (e.g. anyOf/oneOf) are enforced by nf-schema at runtime.

## alignment_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--aligner` | string |  |  | star, bowtie1 |  | star | Alignment tool to be used |
| `--min-aln-length` | integer |  |  |  |  | 15 | Minimum number of aligned basepairs of a read to be kept |

## cage_tag_clustering_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--min-cluster` | integer |  |  |  |  | 30 | Minimum cluster size |
| `--tpm-cluster-threshold` | number |  |  |  |  | 0.2 | Minimum tags per million a cluster has to have |

## generic_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--clusterOptions` | string |  | yes |  |  | false | Arguments passed to Nextflow clusterOptions. |
| `--email-on-fail` | string |  | yes |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary, only when pipeline fails. |
| `--help` | boolean |  | yes |  |  |  | Display help text. |
| `--max-multiqc-email-size` | string |  | yes |  |  | 25.MB | File size limit when attaching MultiQC reports to summary emails. |
| `--monochrome-logs` | boolean |  | yes |  |  |  | Do not use coloured log outputs. |
| `--multiqc-config` | string |  | yes |  |  |  | Custom config file to supply to MultiQC. |
| `--name` | string |  | yes |  |  |  | Workflow name. |
| `--plaintext-email` | boolean |  | yes |  |  |  | Send plain-text email instead of HTML. |
| `--publish-dir-mode` | string |  | yes | symlink, rellink, link, copy, copyNoFollow, move |  | copy | Method used to save pipeline results to output directory. |
| `--tracedir` | string |  | yes |  |  | ${params.outdir}/pipeline_info | Directory to keep pipeline Nextflow logs and reports. |

## input_output_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--bigwig` | boolean |  |  |  |  |  | Specifies if TSS-bigwigs should be generated, additionally to the TSS-bed files |
| `--email` | string |  |  |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary. |
| `--input` | string | yes |  |  |  | data/*R1.fastq.gz | Input FastQ files. |
| `--outdir` | string |  |  |  |  | ./results | The output directory where the results will be saved. |

## institutional_config_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--config-profile-contact` | string |  | yes |  |  |  | Institutional config contact information. |
| `--config-profile-description` | string |  | yes |  |  |  | Institutional config description. |
| `--config-profile-url` | string |  | yes |  |  |  | Institutional config URL link. |
| `--custom-config-base` | string |  | yes |  |  | https://raw.githubusercontent.com/nf-core/configs/master | Base directory for Institutional configs. |
| `--custom-config-version` | string |  | yes |  |  | master | Git commit id for Institutional configs. |
| `--hostnames` | string |  | yes |  |  |  | Institutional configs hostname. |

## max_job_request_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--max-cpus` | integer |  | yes |  |  | 16 | Maximum number of CPUs that can be requested for any single job. |
| `--max-memory` | string |  | yes |  |  | 128.GB | Maximum amount of memory that can be requested for any single job. |
| `--max-time` | string |  | yes |  |  | 240.h | Maximum amount of time that can be requested for any single job. |

## process_skipping_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--skip-alignment` | boolean |  |  |  |  |  | Skip alignment step. |
| `--skip-ctss-generation` | boolean |  |  |  |  |  | Skip steps generating CTSS files including clustering, bed/bigwig and count table output generation. |
| `--skip-ctss-qc` | boolean |  |  |  |  |  | Skip running RSeQC's read distribution QC step on the clustered CTSS. |
| `--skip-initial-fastqc` | boolean |  |  |  |  |  | Skip FastQC run on input reads. |
| `--skip-samtools-stats` | boolean |  |  |  |  |  | Skip samtools stats QC step of aligned reads |
| `--skip-trimming` | boolean |  |  |  |  |  | Skip all trimming steps. |
| `--skip-trimming-fastqc` | boolean |  |  |  |  |  | Skip FastQC run on trimmed reads. |

## reference_genome_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--bowtie-index` | string |  |  |  |  |  | Path to bowtie index directory. |
| `--fasta` | string |  |  |  |  |  | Path to FASTA genome file. |
| `--genome` | string |  |  |  |  |  | Name of iGenomes reference. |
| `--gtf` | string |  |  |  |  |  | Path to gtf file. |
| `--igenomes-base` | string |  | yes |  |  | s3://ngi-igenomes/igenomes/ | Directory / URL base for iGenomes references. |
| `--igenomes-ignore` | boolean |  | yes |  |  |  | Do not load the iGenomes reference config. |
| `--save-reference` | boolean |  |  |  |  |  | All generated reference files will be saved to the results folder if this flag is set. |
| `--star-index` | string |  |  |  |  |  | Path to star index directory. |

## ribosomal_rna_removal_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--remove-ribo-rna` | boolean |  |  |  |  |  | Select to remove ribosoamal reads with SortMeRNA |
| `--ribo-database-manifest` | string |  |  |  |  | $projectDir/assets/rrna-db-defaults.txt | Path to SortMeRNA database file |
| `--save-non-ribo-reads` | boolean |  |  |  |  |  | Select to save the ribosomal-free reads |

## trimming_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--artifacts-3end` | string |  |  |  |  | $projectDir/assets/artifacts_3end.fasta | Path to 3' end artifacts |
| `--artifacts-5end` | string |  |  |  |  | $projectDir/assets/artifacts_5end.fasta | Path to 5' end artifacts |
| `--eco-site` | string |  |  |  |  | CAGCAG | Sequence of the ecoP15 site at the 5' end |
| `--linker-seq` | string |  |  |  |  | TCGTATGCCGTCTTC | Sequence of the linker at the 3' end |
| `--save-trimmed` | boolean |  |  |  |  |  |  |
| `--trim-5g` | boolean |  |  |  |  |  | Trim the first `G` at the 5' end, if available |
| `--trim-artifacts` | boolean |  |  |  |  |  | Artifacts, generated in the sequencing process, are cut if this flag is not set to false. |
| `--trim-ecop` | boolean |  |  |  |  |  | Set to cut the enzyme binding site at the 5' end |
| `--trim-linker` | boolean |  |  |  |  |  | Select to cut the linker at the 3' end |

<!-- Generated from nf-core/cageseq@838d2a5165edb86439d7ff0400bd385d6bcf6927. Do not edit by hand. -->
