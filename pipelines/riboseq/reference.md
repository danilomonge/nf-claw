---
name: riboseq
version: 1.2.0
commit: 74ab1ea2668ee9a221a5c96c86b2a6ee1b2d2f2f
---

# riboseq — full parameter reference

nf-core/riboseq pipeline parameters. Every parameter from the pinned `nextflow_schema.json`, validated by nf-schema at runtime. `hidden` marks nf-core's generic/boilerplate parameters; `constraints` lists each parameter's declared value bounds (pattern, min/max, length) — conditional or composed rules (e.g. anyOf/oneOf) are enforced by nf-schema at runtime.

## general

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--fastp-merge` | boolean |  |  |  |  |  |  |

## alignment_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--aligner` | string |  |  | star |  | star | Specifies the alignment algorithm to use - available options are currently 'star'. |
| `--bam-csi-index` | boolean |  |  |  |  |  | Create a CSI index for BAM files instead of the traditional BAI index. This will be required for genomes with larger chromosome sizes. |
| `--extra-salmon-quant-args` | string |  |  |  |  |  | Extra arguments to pass to Salmon quant command in addition to defaults defined by the pipeline. |
| `--extra-star-align-args` | string |  |  |  |  |  | Extra arguments to pass to STAR alignment command in addition to defaults defined by the pipeline. Only available for the STAR-Salmon route. |
| `--min-mapped-reads` | number |  |  |  |  | 5.0 | Minimum percentage of uniquely mapped reads below which samples are removed from further processing. |
| `--pseudo-aligner-kmer-size` | integer |  |  |  |  | 31 | Kmer length passed to indexing step of pseudoaligners |
| `--salmon-quant-libtype` | string |  |  | A, IS, ISF, ISR, IU, MS, MSF, MSR, MU, OS, OSF, OSR, OU, SF, SR, U |  |  | Override Salmon library type inferred based on strandedness defined in meta object. |
| `--seq-center` | string |  |  |  |  |  | Sequencing center information to be added to read group of BAM files. |
| `--star-ignore-sjdbgtf` | boolean |  |  |  |  |  | When using pre-built STAR indices do not re-extract and use splice junctions from the GTF file. |
| `--stranded-threshold` | number |  |  |  | ≥ 0.5; ≤ 1 | 0.8 | The fraction of stranded reads that must be assigned to a strandedness for confident assignment. Must be at least 0.5. |
| `--unstranded-threshold` | number |  |  |  | ≥ 0; ≤ 1 | 0.1 | The difference in fraction of stranded reads assigned to 'forward' and 'reverse' below which a sample is classified as 'unstranded'. By default the forward and reverse fractions must differ by less than 0.1 for the sample to be called as unstranded. |

## generic_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--email-on-fail` | string |  | yes |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary, only when pipeline fails. |
| `--help` | boolean or string |  |  |  |  |  | Display the help message. |
| `--help-full` | boolean |  |  |  |  |  | Display the full detailed help message. |
| `--hook-url` | string |  | yes |  |  |  | Incoming hook URL for messaging service |
| `--max-multiqc-email-size` | string |  | yes |  |  | 25.MB | File size limit when attaching MultiQC reports to summary emails. |
| `--monochrome-logs` | boolean |  | yes |  |  |  | Do not use coloured log outputs. |
| `--multiqc-config` | string (file path) |  | yes |  |  |  | Custom config file to supply to MultiQC. |
| `--multiqc-logo` | string (file path) |  | yes |  |  |  | Custom logo file to supply to MultiQC. File name must also be set in the MultiQC config file |
| `--multiqc-methods-description` | string (file path) |  |  |  |  |  | Custom MultiQC yaml file containing HTML including a methods description. |
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
| `--contrasts` | string (file path) |  |  |  | matches ^\S+\.(csv\|tsv\|txt)$ |  | A CSV file describing sample contrasts |
| `--email` | string |  |  |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary. |
| `--input` | string (file path) | yes |  |  | matches ^\S+\.(csv\|tsv\|json\|yaml\|yml)$ |  | Path to comma-separated file containing information about the samples in the experiment. |
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
| `--test-data-base` | string |  | yes |  |  | https://raw.githubusercontent.com/nf-core/test-datasets/riboseq/testdata/ | Base path / URL for data used in the test profiles |

## optional_outputs

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--save-align-intermeds` | boolean |  |  |  |  | true | Save the intermediate BAM files from the alignment step. |
| `--save-bbsplit-reads` | boolean |  |  |  |  |  | If this option is specified, FastQ files split by reference will be saved in the results directory. |
| `--save-merged-fastq` | boolean |  |  |  |  |  | Save FastQ files after merging re-sequenced libraries in the results directory. |
| `--save-non-ribo-reads` | boolean |  |  |  |  |  | If this option is specified, intermediate FastQ files containing non-rRNA reads will be saved in the results directory. |
| `--save-reference` | boolean |  |  |  |  |  | If generated by the pipeline save the STAR index in the results directory. |
| `--save-trimmed` | boolean |  |  |  |  |  | Save the trimmed FastQ files in the results directory. |
| `--save-umi-intermeds` | boolean |  |  |  |  |  | If this option is specified, intermediate FastQ and BAM files produced by UMI-tools are also saved in the results directory. |
| `--save-unaligned` | boolean |  |  |  |  |  | Where possible, save unaligned reads from either STAR, HISAT2 or Salmon to the results directory. |

## process_skipping_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--skip-alignment` | boolean |  |  |  |  |  | Skip all of the alignment-based processes within the pipeline. |
| `--skip-bbsplit` | boolean |  |  |  |  | true | Skip BBSplit for removal of non-reference genome reads. |
| `--skip-fastqc` | boolean |  |  |  |  |  | Skip FastQC. |
| `--skip-gtf-filter` | boolean |  |  |  |  |  | Skip filtering of GTF for valid scaffolds and/ or transcript IDs. |
| `--skip-gtf-transcript-filter` | boolean |  |  |  |  |  | Skip the 'transcript_id' checking component of the GTF filtering script used in the pipeline. |
| `--skip-linting` | boolean |  |  |  |  |  | Skip linting checks during FASTQ preprocessing and filtering. |
| `--skip-markduplicates` | boolean |  |  |  |  |  | Skip picard MarkDuplicates step. |
| `--skip-multiqc` | boolean |  |  |  |  |  | Skip MultiQC. |
| `--skip-qc` | boolean |  |  |  |  |  | Skip all QC steps except for MultiQC. |
| `--skip-ribotish` | boolean |  |  |  |  |  | Skip Ribo-TISH. |
| `--skip-ribotricer` | boolean |  |  |  |  |  | Skip Riboricer. |
| `--skip-ribowaltz` | boolean |  |  |  |  |  | Skip riboWaltz. |
| `--skip-trimming` | boolean |  |  |  |  |  | Skip the adapter trimming step. |
| `--skip-umi-extract` | boolean |  |  |  |  |  | Skip the UMI extraction from the read in case the UMIs have been moved to the headers in advance of the pipeline run. |

## read_filtering_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--bbsplit-fasta-list` | string (file path) |  |  |  |  |  | Path to comma-separated file containing a list of reference genomes to filter reads against with BBSplit. You have to also explicitly set `--skip_bbsplit false` if you want to use BBSplit. |
| `--bbsplit-index` | string |  |  |  |  |  | Path to directory or tar.gz archive for pre-built BBSplit index. |
| `--extra-fqlint-args` | string |  |  |  |  | --disable-validator P001 | Extra arguments to pass to the fq lint command. |
| `--remove-ribo-rna` | boolean |  |  |  |  | true | Enable the removal of reads derived from ribosomal RNA using SortMeRNA. |
| `--ribo-database-manifest` | string (file path) |  |  |  |  | ${projectDir}/assets/rrna-db-defaults.txt | Text file containing paths to fasta files (one per line) that will be used to create the database for SortMeRNA. |
| `--sortmerna-index` | string |  |  |  |  |  | Path to directory or tar.gz archive for pre-built sortmerna index. |

## read_trimming_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--extra-fastp-args` | string |  |  |  |  |  | Extra arguments to pass to fastp command in addition to defaults defined by the pipeline. |
| `--extra-trimgalore-args` | string |  |  |  |  |  | Extra arguments to pass to Trim Galore! command in addition to defaults defined by the pipeline. |
| `--min-trimmed-reads` | integer |  |  |  |  | 10000 | Minimum number of trimmed reads below which samples are removed from further processing. Some downstream steps in the pipeline will fail if this threshold is too low. |
| `--trimmer` | string |  |  | trimgalore, fastp |  | trimgalore | Specifies the trimming tool to use - available options are 'trimgalore' and 'fastp'. |

## reference_genome_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--additional-fasta` | string (file path) |  |  |  | matches ^\S+\.fn?a(sta)?(\.gz)?$ |  | FASTA file to concatenate to genome FASTA file e.g. containing spike-in sequences. |
| `--fasta` | string (file path) |  |  |  | matches ^\S+\.fn?a(sta)?(\.gz)?$ |  | Path to FASTA genome file. |
| `--gencode` | boolean |  |  |  |  |  | Specify if your GTF annotation is in GENCODE format. |
| `--genome` | string |  |  |  |  |  | Name of iGenomes reference. |
| `--gff` | string (file path) |  |  |  | matches ^\S+\.gff(\.gz)?$ |  | Path to GFF3 annotation file. |
| `--gtf` | string (file path) |  |  |  | matches ^\S+\.gtf(\.gz)?$ |  | Path to GTF annotation file. |
| `--gtf-extra-attributes` | string |  |  |  |  | gene_name | By default, the pipeline uses the `gene_name` field to obtain additional gene identifiers from the input GTF file when running Salmon. |
| `--gtf-group-features` | string |  |  |  |  | gene_id | Define the attribute type used to group features in the GTF file when running Salmon. |
| `--igenomes-base` | string (directory path) |  | yes |  |  | s3://ngi-igenomes/igenomes/ | The base path to the igenomes reference files |
| `--igenomes-ignore` | boolean |  | yes |  |  |  | Do not load the iGenomes reference config. |
| `--salmon-index` | string |  |  |  |  |  | Path to directory or tar.gz archive for pre-built Salmon index. |
| `--star-index` | string |  |  |  |  |  | Path to directory or tar.gz archive for pre-built STAR index. |
| `--transcript-fasta` | string (file path) |  |  |  | matches ^\S+\.fn?a(sta)?(\.gz)?$ |  | Path to FASTA transcriptome file. |

## riboseq_specific_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--extra-anota2seq-run-args` | string |  |  |  |  |  | Extra arguments to pass to anota2seq in addition to defaults defined by the pipeline. |
| `--extra-ribotish-predict-args` | string |  |  |  |  |  | Extra arguments to pass to the ribotish predict command in addition to defaults defined by the pipeline. |
| `--extra-ribotish-quality-args` | string |  |  |  |  |  | Extra arguments to pass to the ribotish quality command in addition to defaults defined by the pipeline. |
| `--extra-ribotricer-detectorfs-args` | string |  |  |  |  |  | Extra arguments to pass to the ribotricer detect-orfs command in addition to defaults defined by the pipeline. |
| `--extra-ribotricer-prepareorfs-args` | string |  |  |  |  |  | Extra arguments to pass to the ribotricer prepare-orfs command in addition to defaults defined by the pipeline. |
| `--extra-ribowaltz-args` | string |  |  |  |  |  | Extra arguments to pass to the riboWaltz command in addition to defaults defined by the pipeline. |

## umi_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--umi-dedup-tool` | string |  |  | umitools, umicollapse |  | umitools | Specifies the tool to use for UMI deduplication - available options are 'umitools' and 'umicollapse'. |
| `--umi-discard-read` | integer |  |  |  |  |  | After UMI barcode extraction discard either R1 or R2 by setting this parameter to 1 or 2, respectively. |
| `--umitools-bc-pattern` | string |  |  |  |  |  | The UMI barcode pattern to use e.g. 'NNNNNN' indicates that the first 6 nucleotides of the read are from the UMI. |
| `--umitools-bc-pattern2` | string |  |  |  |  |  | The UMI barcode pattern to use if the UMI is located in read 2. |
| `--umitools-dedup-stats` | boolean |  |  |  |  |  | Generate output stats when running "umi_tools dedup". |
| `--umitools-extract-method` | string |  |  |  |  | string | UMI pattern to use. Can be either 'string' (default) or 'regex'. |
| `--umitools-grouping-method` | string |  |  | unique, percentile, cluster, adjacency, directional |  | directional | Method to use to determine read groups by subsuming those with similar UMIs. All methods start by identifying the reads with the same mapping position, but treat similar yet nonidentical UMIs differently. |
| `--umitools-umi-separator` | string |  |  |  |  |  | The character that separates the UMI in the read name. Most likely a colon if you skipped the extraction with UMI-tools and used other software. |
| `--with-umi` | boolean |  |  |  |  |  | Enable UMI-based read deduplication. |

<!-- Generated from nf-core/riboseq@74ab1ea2668ee9a221a5c96c86b2a6ee1b2d2f2f. Do not edit by hand. -->
