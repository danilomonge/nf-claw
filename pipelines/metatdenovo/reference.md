---
name: metatdenovo
version: 1.4.0
commit: 4d0307aa7d34575aa7891a7b4996ffe19e774cd9
---

# metatdenovo — full parameter reference

nf-core/metatdenovo pipeline parameters. Every parameter from the pinned `nextflow_schema.json`, validated by nf-schema at runtime. `hidden` marks nf-core's generic/boilerplate parameters; `constraints` lists each parameter's declared value bounds (pattern, min/max, length) — conditional or composed rules (e.g. anyOf/oneOf) are enforced by nf-schema at runtime.

## assembler_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--assembler` | string |  |  | megahit, spades |  |  | Specify the assembler to run. Possible alternatives: megahit, spades. |
| `--min-contig-length` | integer |  |  |  |  | 0 | Filter out contigs shorter than this. |
| `--save-formatspades` | boolean |  |  |  |  |  | Save the formatted spades fasta file |
| `--spades-flavor` | string |  |  | rna, isolate, sc, meta, plasmid, metaplasmid, metaviral, rnaviral |  | rna | Select which type of assembly you want to make. Default: rna |
| `--user-assembly` | string (file path) |  |  |  |  |  | Path to a fasta file with a finished assembly. Assembly will be skipped by the pipeline. |
| `--user-assembly-name` | string |  |  |  |  | user_assembly | Name to give to the user-provided assembly. |

## bbduk_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--save-bbduk-fastq` | boolean |  |  |  |  |  | Save the resulting fastq files from filtering |
| `--sequence-filter` | string |  |  |  |  |  | Fasta file with sequences to filter away before running assembly etc.. |

## digital_normalization_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--bbnorm` | boolean |  |  |  |  |  | Perform normalization to reduce sequencing depth. |
| `--bbnorm-min` | integer |  |  |  |  | 5 | Reads with an apparent depth of under nx will be presumed to be errors and discarded |
| `--bbnorm-target` | integer |  |  |  |  | 100 | Reduce the number of reads for assembly average coverage of this number. |
| `--save-bbnorm-fastq` | boolean |  |  |  |  |  | Save the resulting fastq files from normalization |

## functional_annotation_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--eggnog-dbpath` | string |  |  |  |  | eggnog | Specify EGGNOG database path |
| `--hmmdir` | string (directory path) |  |  |  | matches ^\S+ |  | Directory with hmm files which will be searched for among ORFs |
| `--hmmfiles` | string (file path) |  |  |  | matches \S+hmm(\.gz)? |  | Comma-separated list of hmm files which will be searched for among ORFs |
| `--hmmpattern` | string |  |  |  |  | *.hmm | Specify which pattern hmm files end with |
| `--kofam-dir` | string |  |  |  |  | ./kofam/ | Path to a directory with KOfam files. Will be created if it doesn't exist. |
| `--skip-eggnog` | boolean |  |  |  |  |  | Skip EGGNOG functional annotation |
| `--skip-kofamscan` | boolean |  |  |  |  |  | If enabled, skips the run of KofamScan. |

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
| `--email` | string |  |  |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary. |
| `--input` | string (file path) | yes |  |  | matches ^\S+\.csv$ |  | Path to comma-separated file containing information about the samples in the experiment. |
| `--multiqc-title` | string |  |  |  |  |  | MultiQC report title. Printed as page header, used for filename if not otherwise specified. |
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

## mapping_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--bbmap-minid` | number |  |  |  |  | 0.9 | Minimum identity needed to assign read to a contig |
| `--save-bam` | boolean |  |  |  |  |  | Save the bam files from mapping |
| `--save-samtools` | boolean |  |  |  |  | true | Save the output from samtools |

## orf_caller_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--orf-caller` | string |  |  | prodigal, prokka, transdecoder |  |  | Specify which ORF caller to run. Possible alternatives: prodigal, prokka, transdecoder. This needs to be set unless the `--user_orfs_*` params are set. |
| `--prodigal-trainingfile` | string |  |  |  |  |  | Specify a training file for prodigal. By default prodigal will learn from the input sequences |
| `--prokka-batchsize` | integer |  | yes |  | matches ^\d+(\.\d+)?\.?\s*(K\|M\|G\|T)?B$ | 10485760 | Size of individual files annotated by Prokka in one batch. |
| `--user-orfs-faa` | string (file path) |  |  |  |  |  | Path to a protein fasta file for user-provided ORFs. |
| `--user-orfs-gff` | string (file path) |  |  |  |  |  | Path to a gff file for user-provided ORFs. |
| `--user-orfs-name` | string |  |  |  |  | user_orfs | Name to give to user-provided ORFs. |

## quality_control_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--skip-fastqc` | boolean |  |  |  |  |  | Skip FastQC. |
| `--skip-qc` | boolean |  |  |  |  |  | Skip all QC steps except for MultiQC. |

## taxonomy_annotation_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--diamond-dbs` | string (file path) |  |  |  | matches ^\S+\.(csv\|tsv\|json\|yaml\|yml)$ |  | Path to comma-separated file containing information about Diamond database files you want to use for taxonomy assignment. |
| `--diamond-top` | integer |  |  |  |  | 10 | Argument to Diamond's `--top` that controls the percentage of hits to include in the LCA. |
| `--eukulele-db` | string |  |  | gtdb, phylodb, marmmetsp, mmetsp, eukprot |  |  | EUKulele database. |
| `--eukulele-dbpath` | string |  |  |  |  | ./eukulele/ | EUKulele database folder. |
| `--eukulele-method` | string |  |  | mets, mags |  | mets | Specify which method to use for EUKulele. the alternatives are: mets (metatranscriptomics) or mags (Metagenome Assembled Genomes). default: mets |
| `--skip-eukulele` | boolean |  |  |  |  |  | If enabled, skips the run of EUKulele |

## trimming_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--clip-r1` | string |  |  |  |  |  | Instructs Trim Galore to remove bp from the 5' end of read 1 (or single-end reads). |
| `--clip-r2` | string |  |  |  |  |  | Instructs Trim Galore to remove bp from the 5' end of read 2 (paired-end reads only). |
| `--save-trimmed` | boolean |  |  |  |  |  | Save the trimmed FastQ files in the results directory. |
| `--skip-trimming` | boolean |  |  |  |  |  | Skip the adapter trimming step. |
| `--three-prime-clip-r1` | string |  |  |  |  |  | Instructs Trim Galore to remove bp from the 3' end of read 1 AFTER adapter/quality trimming has been performed. |
| `--three-prime-clip-r2` | string |  |  |  |  |  | Instructs Trim Galore to remove bp from the 3' end of read 2 AFTER adapter/quality trimming has been performed. |
| `--trim-nextseq` | string |  |  |  |  |  | Instructs Trim Galore to apply the --nextseq=X option, to trim based on quality after removing poly-G tails. |

<!-- Generated from nf-core/metatdenovo@4d0307aa7d34575aa7891a7b4996ffe19e774cd9. Do not edit by hand. -->
