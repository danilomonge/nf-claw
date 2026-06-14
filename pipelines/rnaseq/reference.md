---
name: rnaseq
version: 3.26.0
commit: e7ca46272c8f9d5ceee3f71759f4ba551d3217a4
---

# rnaseq — full parameter reference

## alignment_options

| parameter | type | default | description |
|---|---|---|---|
| `--aligner` | string | star_salmon | Specifies the alignment algorithm to use - available options are 'star_salmon', 'star_rsem', 'hisat2', and 'bowtie2_salmon'. (one of: star_salmon, star_rsem, hisat2, bowtie2_salmon) |
| `--bam-csi-index` | boolean |  | Create a CSI index for BAM files instead of the traditional BAI index. This will be required for genomes with larger chromosome sizes. |
| `--extra-bowtie2-align-args` | string |  | Extra arguments to pass to Bowtie2 alignment command in addition to defaults defined by the pipeline. Only available when using --aligner bowtie2_salmon. |
| `--extra-kallisto-quant-args` | string |  | Extra arguments to pass to Kallisto quant command in addition to defaults defined by the pipeline. |
| `--extra-salmon-quant-args` | string |  | Extra arguments to pass to Salmon quant command in addition to defaults defined by the pipeline. |
| `--extra-star-align-args` | string |  | Extra arguments to pass to STAR alignment command in addition to defaults defined by the pipeline. Only available for the STAR-Salmon route. |
| `--gpu-container-options` | string |  | Override container GPU flags for GPU tasks. Auto-detects if not set (--gpus all for Docker, --nv for Singularity/Apptainer). |
| `--kallisto-quant-fraglen` | integer | 200 | In single-end mode Kallisto requires an estimated fragment length. Specify a default value for that here. TODO: use existing RSeQC results to do this dynamically. |
| `--kallisto-quant-fraglen-sd` | integer | 200 | In single-end mode, Kallisto requires an estimated standard error for fragment length. Specify a default value for that here. TODO: use existing RSeQC results to do this dynamically. |
| `--min-mapped-reads` | number | 5 | Minimum percentage of uniquely mapped reads below which samples are removed from further processing. |
| `--pseudo-aligner` | string |  | Specifies the pseudo aligner to use - available options are 'salmon'. Runs in addition to '--aligner'. (one of: salmon, kallisto) |
| `--pseudo-aligner-kmer-size` | integer | 31 | Kmer length passed to indexing step of pseudoaligners |
| `--salmon-quant-libtype` | string |  |  Override Salmon library type inferred based on strandedness defined in meta object. (one of: A, IS, ISF, ISR, IU, MS, MSF, MSR, MU, OS, OSF, OSR, OU, SF, SR, U) |
| `--seq-center` | string |  | Sequencing center information to be added to read group of BAM files. |
| `--seq-platform` | string |  | Sequencing platform information to be added to read group of BAM files. |
| `--star-ignore-sjdbgtf` | boolean |  | When using pre-built STAR indices do not re-extract and use splice junctions from the GTF file. |
| `--stranded-threshold` | number | 0.8 | The fraction of stranded reads that must be assigned to a strandedness for confident assignment. Must be at least 0.5. |
| `--stringtie-ignore-gtf` | boolean |  | Perform reference-guided de novo assembly of transcripts using StringTie i.e. dont restrict to those in GTF file. |
| `--unstranded-threshold` | number | 0.1 | The difference in fraction of stranded reads assigned to 'forward' and 'reverse' below which a sample is classified as 'unstranded'. By default the forward and reverse fractions must differ by less than 0.1 for the sample to be called as unstranded. |
| `--use-parabricks-star` | boolean |  | Optionally accelerate STAR and MarkDuplicates with Parabricks |
| `--use-sentieon-star` | boolean |  | Optionally accelerate STAR with Sentieon |

## generic_options

| parameter | type | default | description |
|---|---|---|---|
| `--email-on-fail` | string |  | Email address for completion summary, only when pipeline fails. |
| `--help` | ['boolean', 'string'] |  | Display the help message. |
| `--help-full` | boolean |  | Display the full detailed help message. |
| `--max-multiqc-email-size` | string | 25.MB | File size limit when attaching MultiQC reports to summary emails. |
| `--monochrome-logs` | boolean |  | Do not use coloured log outputs. |
| `--multiqc-config` | string |  | Custom config file to supply to MultiQC. |
| `--multiqc-logo` | string |  | Custom logo file to supply to MultiQC. File name must also be set in the MultiQC config file |
| `--multiqc-methods-description` | string |  | Custom MultiQC yaml file containing HTML including a methods description. |
| `--pipelines-testdata-base-path` | string | https://raw.githubusercontent.com/nf-core/test-datasets/7f1614baeb0ddf66e60be78c3d9fa55440465ac8/ | Base URL or local path to location of pipeline test dataset files |
| `--plaintext-email` | boolean |  | Send plain-text email instead of HTML. |
| `--publish-dir-mode` | string | copy | Method used to save pipeline results to output directory. (one of: symlink, rellink, link, copy, copyNoFollow, move) |
| `--show-hidden` | boolean |  | Display hidden parameters in the help message (only works when --help or --help_full are provided). |
| `--trace-report-suffix` | string |  | Suffix to add to the trace report filename. |
| `--validate-params` | boolean | True | Boolean whether to validate parameters against the schema at runtime |
| `--version` | boolean |  | Display version and exit. |

## input_output_options

| parameter | type | default | description |
|---|---|---|---|
| `--email` | string |  | Email address for completion summary. |
| `--input` | string |  | Path to the sample sheet (CSV) containing metadata about the experimental samples. |
| `--multiqc-title` | string |  | MultiQC report title. Printed as page header, used for filename if not otherwise specified. |
| `--outdir` | string |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## institutional_config_options

| parameter | type | default | description |
|---|---|---|---|
| `--config-profile-contact` | string |  | Institutional config contact information. |
| `--config-profile-description` | string |  | Institutional config description. |
| `--config-profile-name` | string |  | Institutional config name. |
| `--config-profile-url` | string |  | Institutional config URL link. |
| `--custom-config-base` | string | https://raw.githubusercontent.com/nf-core/configs/master | Base directory for Institutional configs. |
| `--custom-config-version` | string | master | Git commit id for Institutional configs. |

## optional_outputs

| parameter | type | default | description |
|---|---|---|---|
| `--save-align-intermeds` | boolean |  | Save the intermediate BAM files from the alignment step. |
| `--save-bbsplit-reads` | boolean |  | If this option is specified, FastQ files split by reference will be saved in the results directory. |
| `--save-kraken-assignments` | boolean |  | Save read-by-read assignments from Kraken2. |
| `--save-kraken-unassigned` | boolean |  | Save reads that were not given assignment from Kraken2. |
| `--save-merged-fastq` | boolean |  | Save FastQ files after merging re-sequenced libraries in the results directory. |
| `--save-non-ribo-reads` | boolean |  | If this option is specified, intermediate FastQ files containing non-rRNA reads will be saved in the results directory. |
| `--save-reference` | boolean |  | If generated by the pipeline save the STAR index in the results directory. |
| `--save-trimmed` | boolean |  | Save the trimmed FastQ files in the results directory. |
| `--save-umi-intermeds` | boolean |  | If this option is specified, intermediate FastQ and BAM files produced by UMI-tools are also saved in the results directory. |
| `--save-unaligned` | boolean |  | Where possible, save unaligned reads from either STAR, HISAT2 or Salmon to the results directory. |

## process_skipping_options

| parameter | type | default | description |
|---|---|---|---|
| `--skip-alignment` | boolean |  | Skip all of the alignment-based processes within the pipeline. |
| `--skip-bbsplit` | boolean | True | Skip BBSplit for removal of non-reference genome reads. |
| `--skip-bigwig` | boolean |  | Skip bigWig file creation. |
| `--skip-biotype-qc` | boolean |  | Skip additional featureCounts process for biotype QC. |
| `--skip-deseq2-qc` | boolean |  | Skip DESeq2 PCA and heatmap plotting. |
| `--skip-dupradar` | boolean |  | Skip dupRadar. |
| `--skip-fastqc` | boolean |  | Skip FastQC. |
| `--skip-gtf-filter` | boolean |  | Skip filtering of GTF for valid scaffolds and/ or transcript IDs. |
| `--skip-gtf-transcript-filter` | boolean |  | Skip the 'transcript_id' checking component of the GTF filtering script used in the pipeline. Ensure the GTF file is valid. |
| `--skip-linting` | boolean |  | Skip linting checks during FASTQ preprocessing and filtering. |
| `--skip-markduplicates` | boolean |  | Skip picard MarkDuplicates step. |
| `--skip-multiqc` | boolean |  | Skip MultiQC. |
| `--skip-preseq` | boolean | True | Skip Preseq. |
| `--skip-pseudo-alignment` | boolean |  | Skip all of the pseudoalignment-based processes within the pipeline. |
| `--skip-qc` | boolean |  | Skip all QC steps except for MultiQC. |
| `--skip-qualimap` | boolean |  | Skip Qualimap. |
| `--skip-quantification-merge` | boolean |  | Skip cross-sample count merging. Runs tximport per-sample instead of merged, producing individual gene/transcript-level TSVs per sample. Skips SummarizedExperiment and RSEM merge counts. Useful for very large cohorts. |
| `--skip-rseqc` | boolean |  | Skip RSeQC. |
| `--skip-stringtie` | boolean |  | Skip StringTie. |
| `--skip-trimming` | boolean |  | Skip the adapter trimming step. |
| `--skip-umi-extract` | boolean |  | Skip the UMI extraction from the read in case the UMIs have been moved to the headers in advance of the pipeline run. |
| `--use-rustqc` | boolean | False | Experimental. Use RustQC instead of dupRadar, featureCounts biotype QC, RSeQC, Preseq, Qualimap, and samtools stats/flagstat/idxstats. Recommend trialling on pilot data first. |

## quality_control

| parameter | type | default | description |
|---|---|---|---|
| `--bracken-precision` | string | S | Taxonomic level for Bracken abundance estimations. (one of: D, P, C, O, F, G, S) |
| `--contaminant-screening` | string |  | Tool to use for detecting contaminants in the selected screening reads - available options are 'sylph', 'kraken2', or 'kraken2_bracken' (one of: kraken2, kraken2_bracken, sylph) |
| `--contaminant-screening-input` | string | unmapped | Read set to screen for contaminants: aligner-unmapped reads (default) or trimmed/filter-passed reads before alignment. (one of: trimmed, unmapped) |
| `--deseq2-vst` | boolean | True | Use vst transformation instead of rlog with DESeq2. |
| `--extra-fqlint-args` | string | --disable-validator P001 | Extra arguments to pass to the fq lint command. |
| `--kraken-db` | string |  | Database when using Kraken2/Bracken for contaminant screening. |
| `--rseqc-modules` | string | bam_stat,inner_distance,infer_experiment,junction_annotation,junction_saturation,read_distribution,read_duplication | Comma-separated list of RSeQC modules to run. |
| `--sylph-db` | string |  | Comma separated list of databases to profile against when using Sylph for contamination detection |
| `--sylph-taxonomy` | string |  | Comma separated list of taxonomies when using Sylph for contamination detection |

## read_filtering_options

| parameter | type | default | description |
|---|---|---|---|
| `--bbsplit-fasta-list` | string |  | Path to comma-separated file containing a list of reference genomes to filter reads against with BBSplit. You have to also explicitly set `--skip_bbsplit false` if you want to use BBSplit. |
| `--bbsplit-index` | string |  | Path to directory or tar.gz archive for pre-built BBSplit index. |
| `--remove-ribo-rna` | boolean |  | Enable the removal of reads derived from ribosomal RNA. |
| `--ribo-database-manifest` | string | ${projectDir}/workflows/rnaseq/assets/rrna-db-defaults.txt | Text file containing paths to fasta files (one per line) that will be used to create the database for SortMeRNA. |
| `--ribo-removal-tool` | string | sortmerna | Tool to use for rRNA removal. (one of: sortmerna, ribodetector, bowtie2) |
| `--sortmerna-index` | string |  | Path to directory or tar.gz archive for pre-built sortmerna index. |
| `--use-gpu-ribodetector` | boolean |  | Enable GPU acceleration for ribodetector. |

## read_trimming_options

| parameter | type | default | description |
|---|---|---|---|
| `--extra-fastp-args` | string |  | Extra arguments to pass to fastp command in addition to defaults defined by the pipeline. |
| `--extra-trimgalore-args` | string |  | Extra arguments to pass to Trim Galore! command in addition to defaults defined by the pipeline. |
| `--min-trimmed-reads` | integer | 10000 | Minimum number of trimmed reads below which samples are removed from further processing. Some downstream steps in the pipeline will fail if this threshold is too low. |
| `--trimmer` | string | trimgalore | Specifies the trimming tool to use - available options are 'trimgalore' and 'fastp'. (one of: trimgalore, fastp) |

## reference_genome_options

| parameter | type | default | description |
|---|---|---|---|
| `--additional-fasta` | string |  | FASTA file to concatenate to genome FASTA file e.g. containing spike-in sequences. |
| `--arm` | boolean |  | Use ARM architecture containers. |
| `--bowtie2-index` | string |  | Path to directory or tar.gz archive for pre-built Bowtie2 index. |
| `--fasta` | string |  | Path to FASTA genome file. |
| `--featurecounts-feature-type` | string | exon | By default, the pipeline assigns reads based on the 'exon' attribute within the GTF file. |
| `--featurecounts-group-type` | string | gene_biotype | The attribute type used to group feature types in the GTF file when generating the biotype plot with featureCounts. |
| `--gencode` | boolean |  | Specify if your GTF annotation is in GENCODE format. |
| `--gene-bed` | string |  | Path to BED file containing gene intervals. This will be created from the GTF file if not specified. |
| `--genome` | string |  | Name of a `params.genomes` catalogue entry (iGenomes or a user-defined catalogue). |
| `--gff` | string |  | Path to GFF3 annotation file. |
| `--gffread-transcript-fasta` | boolean |  | Use gffread to generate transcript FASTA instead of RSEM. |
| `--gtf` | string |  | Path to GTF annotation file. |
| `--gtf-extra-attributes` | string | gene_name | By default, the pipeline uses the `gene_name` field to obtain additional gene identifiers from the input GTF file when running Salmon. |
| `--gtf-group-features` | string | gene_id | Define the attribute type used to group features in the GTF file when running Salmon. |
| `--hisat2-build-memory` | string | 200.GB | Minimum memory required to use splice sites and exons in the HiSAT2 index build process. |
| `--hisat2-index` | string |  | Path to directory or tar.gz archive for pre-built HISAT2 index. |
| `--igenomes-base` | string | s3://ngi-igenomes/igenomes/ | The base path to the igenomes reference files |
| `--igenomes-ignore` | boolean |  | Do not load the iGenomes reference config. |
| `--kallisto-index` | string |  | Path to directory or tar.gz archive for pre-built Kallisto index. |
| `--prokaryotic` | boolean |  | Enable prokaryotic mode for bacterial/archaeal RNA-seq data. |
| `--rsem-index` | string |  | Path to directory or tar.gz archive for pre-built RSEM index. |
| `--salmon-index` | string |  | Path to directory or tar.gz archive for pre-built Salmon index. |
| `--splicesites` | string |  | Splice sites file required for HISAT2. |
| `--star-index` | string |  | Path to directory or tar.gz archive for pre-built STAR index. |
| `--transcript-fasta` | string |  | Path to FASTA transcriptome file. |

## umi_options

| parameter | type | default | description |
|---|---|---|---|
| `--umi-dedup-tool` | string | umitools | Specifies the tool to use for UMI deduplication - available options are 'umitools' and 'umicollapse'. (one of: umitools, umicollapse) |
| `--umi-discard-read` | integer |  | After UMI barcode extraction discard either R1 or R2 by setting this parameter to 1 or 2, respectively. |
| `--umitools-bc-pattern` | string |  | The UMI barcode pattern to use e.g. 'NNNNNN' indicates that the first 6 nucleotides of the read are from the UMI. |
| `--umitools-bc-pattern2` | string |  | The UMI barcode pattern to use if the UMI is located in read 2. |
| `--umitools-dedup-primary-only` | boolean |  | Filter to primary alignments before UMI-tools dedup. |
| `--umitools-dedup-stats` | boolean |  | Generate output stats when running "umi_tools dedup". |
| `--umitools-extract-method` | string | string | UMI pattern to use. Can be either 'string' (default) or 'regex'. |
| `--umitools-grouping-method` | string | directional | Method to use to determine read groups by subsuming those with similar UMIs. All methods start by identifying the reads with the same mapping position, but treat similar yet nonidentical UMIs differently. (one of: unique, percentile, cluster, adjacency, directional) |
| `--umitools-umi-separator` | string |  | The character that separates the UMI in the read name. Most likely a colon if you skipped the extraction with UMI-tools and used other software. |
| `--with-umi` | boolean |  | Enable UMI-based read deduplication. |

<!-- Generated from nf-core/rnaseq@e7ca46272c8f9d5ceee3f71759f4ba551d3217a4. Do not edit by hand. -->
