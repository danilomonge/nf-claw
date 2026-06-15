---
name: sarek
version: 3.8.1
commit: 4bd2948f98c5bf7b785c91cf6708fffccab25467
---

# sarek — full parameter reference

## annotation

| parameter | type | default | description |
|---|---|---|---|
| `--bcftools-annotations` | string |  | A vcf file containing custom annotations to be used with bcftools annotate. Needs to be bgzipped. |
| `--bcftools-annotations-tbi` | string |  | Index file for `bcftools_annotations` |
| `--bcftools-columns` | string |  | Optional text file with list of columns to use from `bcftools_annotations`, one name per row |
| `--bcftools-header-lines` | string |  | Text file with the header lines of `bcftools_annotations` |
| `--condel-config` | string |  | Path to Condel config file. |
| `--dbnsfp` | string |  | Path to dbNSFP processed file. |
| `--dbnsfp-consequence` | string |  | Consequence to annotate with |
| `--dbnsfp-fields` | string | rs_dbSNP,HGVSc_VEP,HGVSp_VEP,1000Gp3_EAS_AF,1000Gp3_AMR_AF,LRT_score,GERP++_RS,gnomAD_exomes_AF | Fields to annotate with |
| `--dbnsfp-tbi` | string |  | Path to dbNSFP tabix indexed file. |
| `--mastermind-file` | string |  | Path to Mastermind cited variants VCF file. |
| `--mastermind-mutations` | boolean |  | Mastermind plugin mutations parameter. |
| `--mastermind-url` | boolean |  | Mastermind plugin url parameter. |
| `--mastermind-var-iden` | boolean |  | Mastermind plugin var_iden parameter. |
| `--outdir-cache` | string |  | The output directory where the cache will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--phenotypes-file` | string |  | Path to phenotype annotation GFF/GVF file. |
| `--phenotypes-file-tbi` | string |  | Path to phenotype annotation tabix indexed file. |
| `--phenotypes-include-types` | string |  | Phenotypes plugin feature types to include. |
| `--snpsift-databases` | string |  | Path to CSV samplesheet specifying SnpSift annotation databases. |
| `--spliceai-indel` | string |  | Path to spliceai raw scores indel file. |
| `--spliceai-indel-tbi` | string |  | Path to spliceai raw scores indel tabix indexed file. |
| `--spliceai-snv` | string |  | Path to spliceai raw scores snv file. |
| `--spliceai-snv-tbi` | string |  | Path to spliceai raw scores snv tabix indexed file. |
| `--vep-condel` | boolean |  | Enable the use of the VEP Condel plugin. |
| `--vep-custom-args` | string | --everything --filter_common --per_gene --total_length --offline --format vcf | Add an extra custom argument to VEP. |
| `--vep-dbnsfp` | boolean |  | Enable the use of the VEP dbNSFP plugin. |
| `--vep-include-fasta` | boolean |  | Allow usage of fasta file for annotation with VEP |
| `--vep-loftee` | boolean |  | Enable the use of the VEP LOFTEE plugin. |
| `--vep-mastermind` | boolean |  | Enable the use of the VEP Mastermind plugin. |
| `--vep-out-format` | string | vcf | VEP output-file format. (one of: json, tab, vcf) |
| `--vep-phenotypes` | boolean |  | Enable the use of the VEP Phenotypes plugin. |
| `--vep-spliceai` | boolean |  | Enable the use of the VEP SpliceAI plugin. |
| `--vep-spliceregion` | boolean |  | Enable the use of the VEP SpliceRegion plugin. |
| `--vep-version` | string | 115.0-0 | Should reflect the VEP version used in the container. |

## fastq_preprocessing

| parameter | type | default | description |
|---|---|---|---|
| `--clip-r1` | integer | 0 | Remove bp from the 5' end of read 1 |
| `--clip-r2` | integer | 0 | Remove bp from the 5' end of read 2 |
| `--length-required` | integer | 15 | Minimum length of reads to keep |
| `--save-split-fastqs` | boolean |  | If set, publishes split FASTQ files. Intended for testing purposes. |
| `--save-trimmed` | boolean |  | Save trimmed FastQ file intermediates. |
| `--three-prime-clip-r1` | integer | 0 | Remove bp from the 3' end of read 1 |
| `--three-prime-clip-r2` | integer | 0 | Remove bp from the 3' end of read 2 |
| `--trim-fastq` | boolean |  | Run FastP for read trimming |
| `--trim-nextseq` | boolean |  | Removing poly-G tails. |

## general_reference_genome_options

| parameter | type | default | description |
|---|---|---|---|
| `--build-only-index` | boolean |  | Only built references. |
| `--download-cache` | boolean |  | Download annotation cache. |
| `--igenomes-base` | string | s3://ngi-igenomes/igenomes/ | The base path to the igenomes reference files |
| `--igenomes-ignore` | boolean |  | Do not load the iGenomes reference config. |
| `--save-reference` | boolean |  | Save built references. |

## generic_options

| parameter | type | default | description |
|---|---|---|---|
| `--email` | string |  | Email address for completion summary. |
| `--email-on-fail` | string |  | Email address for completion summary, only when pipeline fails. |
| `--help` | ['boolean', 'string'] |  | Display the help message. |
| `--help-full` | boolean |  | Display the full detailed help message. |
| `--hook-url` | string |  | Incoming hook URL for messaging service |
| `--max-multiqc-email-size` | string | 25.MB | File size limit when attaching MultiQC reports to summary emails. |
| `--monochrome-logs` | boolean |  | Do not use coloured log outputs. |
| `--multiqc-config` | string |  | Custom config file to supply to MultiQC. |
| `--multiqc-logo` | string |  | Custom logo file to supply to MultiQC. File name must also be set in the MultiQC config file |
| `--multiqc-methods-description` | string |  | Custom MultiQC yaml file containing HTML including a methods description. |
| `--multiqc-title` | string |  | MultiQC report title. Printed as page header, used for filename if not otherwise specified. |
| `--pipelines-testdata-base-path` | string | https://raw.githubusercontent.com/nf-core/test-datasets/ | Base URL or local path to location of pipeline test dataset files |
| `--plaintext-email` | boolean |  | Send plain-text email instead of HTML. |
| `--publish-dir-mode` | string | copy | Method used to save pipeline results to output directory. (one of: symlink, rellink, link, copy, copyNoFollow, move) |
| `--show-hidden` | boolean |  | Display hidden parameters in the help message (only works when --help or --help_full are provided). |
| `--trace-report-suffix` | string |  | Suffix to add to the trace report filename. Default is the date and time in the format yyyy-MM-dd_HH-mm-ss. |
| `--validate-params` | boolean | True | Boolean whether to validate parameters against the schema at runtime |
| `--version` | boolean |  | Display version and exit. |

## input_output_options

| parameter | type | default | description |
|---|---|---|---|
| `--input` | string |  | Path to comma-separated file containing information about the samples in the experiment. |
| `--input-restart` | string |  | Automatic retrieval for restart |
| `--outdir` | string |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--step` | string | mapping | Starting step (one of: mapping, markduplicates, prepare_recalibration, recalibrate, variant_calling, annotate) |

## institutional_config_options

| parameter | type | default | description |
|---|---|---|---|
| `--config-profile-contact` | string |  | Institutional config contact information. |
| `--config-profile-description` | string |  | Institutional config description. |
| `--config-profile-name` | string |  | Institutional config name. |
| `--config-profile-url` | string |  | Institutional config URL link. |
| `--custom-config-base` | string | https://raw.githubusercontent.com/nf-core/configs/master | Base directory for Institutional configs. |
| `--custom-config-version` | string | master | Git commit id for Institutional configs. |
| `--modules-testdata-base-path` | string |  | Base path / URL for data used in the modules |
| `--seq-center` | string |  | Sequencing center information to be added to read group (CN field). |
| `--seq-platform` | string | ILLUMINA | Sequencing platform information to be added to read group (PL field). |
| `--test-data-base` | string | https://raw.githubusercontent.com/nf-core/test-datasets/sarek3 | Base path / URL for data used in the test profiles |

## main_options

| parameter | type | default | description |
|---|---|---|---|
| `--intervals` | string |  | Path to target bed file in case of whole exome or targeted sequencing or intervals file. |
| `--no-intervals` | boolean |  | Disable usage of intervals. |
| `--nucleotides-per-second` | integer | 200000 | Estimate interval size. |
| `--skip-tools` | string |  | Disable specified tools. |
| `--split-fastq` | integer | 50000000 | Specify how many reads each split of a FastQ file contains. Set 0 to turn off splitting at all. |
| `--tools` | string |  | Tools to use for contamination removal, duplicate marking, variant calling and/or for annotation. |
| `--wes` | boolean |  | Enable when exome or panel data is provided. |

## post_variant_calling

| parameter | type | default | description |
|---|---|---|---|
| `--bcftools-filter-criteria` | string | -f PASS,. | Filter criteria. Uses bcftools view filter options. To customize, follow instructions here: https://samtools.github.io/bcftools/bcftools.html#view |
| `--concatenate-vcfs` | boolean |  | Option for concatenating germline vcf-files. |
| `--consensus-min-count` | integer | 2 | Minimum number of variant callers calling a variant for consensus results |
| `--filter-vcfs` | boolean |  | Enable filtering of VCFs with bcftools view |
| `--normalize-vcfs` | boolean |  | Option for normalization of vcf-files. |
| `--snv-consensus-calling` | boolean |  | Enable consensus calling of multiple VCF files from one sample |
| `--varlociraptor-chunk-size` | integer | 15 | Number of chunks to split the vcf-files for varlociraptor. Minimum 1, indicates no splitting |
| `--varlociraptor-scenario-germline` | string |  | Yte compatible scenario file for germline samples. Defaults to assets/varlociraptor_germline.yte.yaml |
| `--varlociraptor-scenario-somatic` | string |  | Yte compatible scenario file for somatic samples. Defaults to assets/varlociraptor_somatic.yte.yaml |
| `--varlociraptor-scenario-tumor-only` | string |  | Yte compatible scenario file for tumor only samples. Defaults to assets/varlociraptor_tumor_only.yte.yaml |

## preprocessing

| parameter | type | default | description |
|---|---|---|---|
| `--aligner` | string | bwa-mem | Specify aligner to be used to map reads to reference genome. (one of: bwa-mem, bwa-mem2, dragmap, sentieon-bwamem, parabricks) |
| `--markduplicates-pixel-distance` | integer |  |  |
| `--save-mapped` | boolean |  | Save mapped files. |
| `--save-output-as-bam` | boolean |  | Saves output from mapping (if `--save_mapped`), Markduplicates & Baserecalibration as BAM file instead of CRAM |
| `--sentieon-consensus` | boolean |  | Generate consensus reads with Sentieon dedup rather than choosing one best read. |
| `--use-gatk-spark` | string |  | Enable usage of GATK Spark implementation for duplicate marking and/or base quality score recalibration |

## reference_genome_options

| parameter | type | default | description |
|---|---|---|---|
| `--ascat-alleles` | string |  | Path to ASCAT allele zip file. |
| `--ascat-genome` | string |  | ASCAT genome. (one of: hg19, hg38) |
| `--ascat-loci` | string |  | Path to ASCAT loci zip file. |
| `--ascat-loci-gc` | string |  | Path to ASCAT GC content correction file. |
| `--ascat-loci-rt` | string |  | Path to ASCAT RT (replictiming) correction file. |
| `--bwa` | string |  | Path to BWA mem indices. |
| `--bwamem2` | string |  | Path to bwa-mem2 mem indices. |
| `--chr-dir` | string |  | Path to chromosomes folder used with ControLFREEC. |
| `--dbsnp` | string |  | Path to dbsnp file. |
| `--dbsnp-tbi` | string |  | Path to dbsnp index. |
| `--dbsnp-vqsr` | string |  | Label string for VariantRecalibration (haplotypecaller joint variant calling). If you use AWS iGenomes, this has already been set for you appropriately. |
| `--dict` | string |  | Path to FASTA dictionary file. |
| `--dragmap` | string |  | Path to dragmap indices. |
| `--fasta` | string |  | Path to FASTA genome file. |
| `--fasta-fai` | string |  | Path to FASTA reference index. |
| `--genome` | string | GATK.GRCh38 | Name of iGenomes reference. |
| `--germline-resource` | string |  | Path to GATK Mutect2 Germline Resource File. |
| `--germline-resource-tbi` | string |  | Path to GATK Mutect2 Germline Resource Index. |
| `--known-indels` | string |  | Path to known indels file. |
| `--known-indels-tbi` | string |  | Path to known indels file index. |
| `--known-indels-vqsr` | string |  | Label string for VariantRecalibration (haplotypecaller joint variant calling). If you use AWS iGenomes, this has already been set for you appropriately. |
| `--known-snps` | string |  | Path to known snps file. |
| `--known-snps-tbi` | string |  | Path to known snps file snps. |
| `--known-snps-vqsr` | string |  | Label string for VariantRecalibration (haplotypecaller joint variant calling).If you use AWS iGenomes, this has already been set for you appropriately. |
| `--mappability` | string |  | Path to Control-FREEC mappability file. |
| `--msisensor2-models` | string |  | Path to models folder used with MSIsensor2. |
| `--msisensorpro-scan` | string |  | Path to scan file used with MSIsensorPro. |
| `--ngscheckmate-bed` | string |  | Path to SNP bed file for sample checking with NGSCheckMate |
| `--sentieon-dnascope-model` | string |  | Machine learning model for Sentieon Dnascope. |
| `--snpeff-cache` | string | s3://annotation-cache/snpeff_cache/ | Path to snpEff cache. |
| `--snpeff-db` | string |  | snpEff DB version. |
| `--vep-cache` | string | s3://annotation-cache/vep_cache/ | Path to VEP cache. |
| `--vep-cache-version` | string |  | VEP cache version. |
| `--vep-genome` | string |  | VEP genome. |
| `--vep-species` | string |  | VEP species. |

## umi_processing

| parameter | type | default | description |
|---|---|---|---|
| `--bbsplit-fasta-list` | string |  | Path to comma-separated file containing a list of reference genomes to filter reads against with BBSplit. You have to also explicitly set `--tools bbsplit` if you want to use BBSplit. |
| `--bbsplit-index` | string |  | Path to directory or tar.gz archive for pre-built BBSplit index. |
| `--group-by-umi-strategy` | string | Adjacency | Default strategy for fgbio UMI-based consensus read generation (one of: Identity, Edit, Adjacency, Paired) |
| `--save-bbsplit-reads` | boolean |  | If this option is specified, FastQ files split by reference will be saved in the results directory. |
| `--umi-base-skip` | integer |  | Number of bases to skip after the UMI(s) in the read when extracting with fastp. |
| `--umi-in-read-header` | boolean |  | Move UMIs from fastq read headers to a tag prior to deduplication. |
| `--umi-length` | integer |  | Length of the UMI(s) in the read. |
| `--umi-location` | string |  | Location of the UMI(s) to be extracted with fastp. (one of: read1, read2, per_read, index1, index2, per_index) |
| `--umi-read-structure` | string |  | Specify UMI read structure for fgbio UMI consensus read generation |
| `--umi-tag` | string |  | Tag detailing where UMIs are present inside the bam/cram file (e.g. RX). |

## variant_calling

| parameter | type | default | description |
|---|---|---|---|
| `--ascat-min-base-qual` | integer | 20 | Overwrite Ascat min base quality required for a read to be counted. |
| `--ascat-min-counts` | integer | 10 | Overwrite Ascat minimum depth required in the normal for a SNP to be considered. |
| `--ascat-min-map-qual` | integer | 35 | Overwrite Ascat min mapping quality required for a read to be counted. |
| `--ascat-ploidy` | number |  | Overwrite ASCAT ploidy. |
| `--ascat-purity` | number |  | Overwrite ASCAT purity. |
| `--cf-chrom-len` | string |  | Specify a custom chromosome length file. |
| `--cf-coeff` | number | 0.05 | Overwrite Control-FREEC coefficientOfVariation |
| `--cf-contamination` | integer | 0 | Design known contamination value for Control-FREEC |
| `--cf-contamination-adjustment` | boolean |  | Overwrite Control-FREEC contaminationAdjustement |
| `--cf-mincov` | integer | 0 | Minimal read coverage for a position to be considered in BAF analysis. |
| `--cf-minqual` | integer | 0 | Minimal sequencing quality for a position to be considered in BAF analysis. |
| `--cf-ploidy` | string | 2 | Genome ploidy used by ControlFREEC |
| `--cf-window` | number |  | Overwrite Control-FREEC window size. |
| `--cnvkit-reference` | string |  | Copy-number reference for CNVkit |
| `--freebayes-filter` | string | 30 | Filtering expression for vcflib/vcffilter |
| `--gatk-pcr-indel-model` | string | CONSERVATIVE |  |
| `--ignore-soft-clipped-bases` | boolean |  | Do not analyze soft clipped bases in the reads for GATK Mutect2. |
| `--joint-germline` | boolean |  | Turn on the joint germline variant calling for GATK haplotypecaller |
| `--joint-mutect2` | boolean |  | Runs Mutect2 in joint (multi-sample) mode for better concordance among variant calls of tumor samples from the same patient. Mutect2 outputs will be stored in a subfolder named with patient ID under `variant_calling/mutect2/` folder. Only a single normal sample per patient is allowed. Tumor-only mode is also supported. |
| `--only-paired-variant-calling` | boolean |  | If true, skips germline variant calling for matched normal to tumor sample. Normal samples without matched tumor will still be processed through germline variant calling tools. |
| `--pon` | string |  | Panel-of-normals VCF (bgzipped) for GATK Mutect2 |
| `--pon-tbi` | string |  | Index of PON panel-of-normals VCF. |
| `--sentieon-dnascope-emit-mode` | string | variant | Option for selecting output and emit-mode of Sentieon's Dnascope. |
| `--sentieon-dnascope-pcr-indel-model` | string | CONSERVATIVE | Option for selecting the PCR indel model used by Sentieon Dnascope. |
| `--sentieon-haplotyper-emit-mode` | string | variant | Option for selecting output and emit-mode of Sentieon's Haplotyper. |

<!-- Generated from nf-core/sarek@4bd2948f98c5bf7b785c91cf6708fffccab25467. Do not edit by hand. -->
