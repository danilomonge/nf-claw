---
name: differentialabundance
version: 1.5.0
commit: 3dd360fed0dca1780db1bdf5dce85e5258fa2253
---

# differentialabundance — full parameter reference

nf-core/differentialabundance pipeline parameters. Every parameter from the pinned `nextflow_schema.json`, validated by nf-schema at runtime. `hidden` marks nf-core's generic/boilerplate parameters; `constraints` lists each parameter's declared value bounds (pattern, min/max, length) — conditional or composed rules (e.g. anyOf/oneOf) are enforced by nf-schema at runtime.

## abundance_values

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--affy-cel-files-archive` | string |  |  |  |  | null | Alternative to matrix: a compressed CEL files archive such as often found in GEO |
| `--matrix` | string (file path) |  |  |  | matches ^\S+\.(tsv\|csv\|txt)$ |  | TSV-format abundance matrix |
| `--querygse` | string |  |  |  |  | null | Use SOFT files from GEO by providing the GSE study identifier |
| `--transcript-length-matrix` | string |  |  |  |  |  | (RNA-seq only): optional transcript length matrix with samples and genes as the abundance matrix |

## affy_input_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--affy-background` | boolean |  |  |  |  | true | logical value. If TRUE, then background correct using RMA background correction. |
| `--affy-bgversion` | integer |  |  |  |  | 2 | integer value indicating which RMA background to use |
| `--affy-build-annotation` | boolean |  |  |  |  | true | logical value. If TRUE, a matrix of probe annotations will be derived. |
| `--affy-cdfname` | string |  |  |  |  | null | Used to specify the name of an alternative cdf package. If set to NULL, then the usual cdf package based on Affymetrix' mappings will be used. |
| `--affy-destructive` | boolean |  |  |  |  |  | logical value. If TRUE, then works on the PM matrix in place as much as possible, good for large datasets. |
| `--affy-file-name-col` | string |  |  |  |  | file | Column of the sample sheet containing the Affymetrix CEL file name |
| `--affy-rm-extra` | boolean |  |  |  |  |  | if TRUE, then overrides what is in rm.mask and rm.oultiers. |
| `--affy-rm-mask` | boolean |  |  |  |  |  | should the spots marked as 'MASKS' set to NA? |
| `--affy-rm-outliers` | boolean |  |  |  |  |  | should the spots marked as 'OUTLIERS' set to NA? |

## deseq2_specific_options_rna_seq_only

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--deseq2-alpha` | number |  |  |  |  | 0.1 | `alpha` parameter passed to results() |
| `--deseq2-alt-hypothesis` | string |  |  |  |  | greaterAbs | `altHypothesis` parameter passed to results() |
| `--deseq2-cores` | integer |  |  |  |  | 1 | Number of cores |
| `--deseq2-fit-type` | string |  |  | parametric, local, mean, glmGamPoi |  | parametric | `fitType` parameter passed to DESeq() |
| `--deseq2-independent-filtering` | boolean |  |  |  |  | true | `independentFiltering` parameter passed to results() |
| `--deseq2-lfc-threshold` | integer |  |  |  |  | 0 | `lfcThreshold` parameter passed to results() |
| `--deseq2-min-replicates-for-replace` | integer |  |  |  |  | 7 | 'minReplicatesForReplace' parameter passed to DESeq() |
| `--deseq2-minmu` | number |  |  |  |  | 0.5 | `minmu` parameter passed to results() |
| `--deseq2-p-adjust-method` | string |  |  |  |  | BH | `pAdjustMethod` parameter passed to results() |
| `--deseq2-sf-type` | string |  |  | ratio, poscounts, iterate |  | ratio | `sfType` parameter passed to DESeq() |
| `--deseq2-shrink-lfc` | boolean |  |  |  |  | true | Shink fold changes in results? |
| `--deseq2-test` | string |  |  | Wald, LRT |  | Wald | `test` parameter passed to DESeq() |
| `--deseq2-use-t` | boolean |  |  |  |  |  | `useT` parameter passed to DESeq2 |
| `--deseq2-vs-blind` | boolean |  |  |  |  | true | `blind` parameter for rlog() and/ or vst() |
| `--deseq2-vs-method` | string |  |  | rlog, vst, rlog,vst |  | vst | variance stabilisation method to use when making a variance stabilised matrix |
| `--deseq2-vst-nsub` | integer |  |  |  |  | 1000 | `nsub` parameter passed to vst() |

## differential_analysis

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--differential-fc-column` | string | yes |  |  |  | log2FoldChange | The fold change column in differential results tables |
| `--differential-feature-id-column` | string | yes |  |  |  | gene_id | The feature identifier column in differential results tables |
| `--differential-feature-name-column` | string |  |  |  |  | gene_name | Where a features file (GTF) has been provided, what attributed to use to name features |
| `--differential-file-suffix` | string |  |  |  |  |  | Advanced option: the suffix associated tabular differential results tables. Will by default use the appropriate suffix according to the study_type. |
| `--differential-foldchanges-logged` | boolean |  |  |  |  | true | Indicate whether or not fold changes are on the log scale (default is to assume they are) |
| `--differential-max-pval` | number | yes |  |  |  | 1.0 | Maximum p value used to calculate differential feature numbers |
| `--differential-max-qval` | number | yes |  |  |  | 0.05 | Maximum q value used to calculate differential feature numbers |
| `--differential-min-fold-change` | number | yes |  |  |  | 2.0 | Minimum fold change used to calculate differential feature numbers |
| `--differential-palette-name` | string | yes |  |  |  | Set1 | Valid R palette name |
| `--differential-pval-column` | string |  |  |  |  | pvalue | The p value column in differential results tables |
| `--differential-qval-column` | string | yes |  |  |  | padj | The q value column in differential results tables. |
| `--differential-subset-to-contrast-samples` | boolean |  |  |  |  |  | In differential analysis (DEseq2 or Limma), subset to the contrast samples before modelling variance? |

## exploratory_analysis

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--exploratory-assay-names` | string |  | yes |  |  | raw,normalised,variance_stabilised | Specifies assay names to be used for matrices, platform-specific. |
| `--exploratory-clustering-method` | string | yes |  |  |  | ward.D2 | Clustering method used in dendrogram creation |
| `--exploratory-cor-method` | string | yes |  |  |  | spearman | Correlation method used in dendrogram creation |
| `--exploratory-final-assay` | string |  | yes |  |  | variance_stabilised | Specifies final assay to be used for exploratory analysis, platform-specific |
| `--exploratory-log2-assays` | string |  |  |  |  |  | Of which assays to compute the log2 during exploratory analysis. Not necessary for maxquant data as this is controlled by the pipeline. |
| `--exploratory-mad-threshold` | integer |  |  |  |  | -5 | Threshold on MAD score for outlier identification |
| `--exploratory-main-variable` | string | yes |  |  |  | auto_pca | How should the main grouping variable be selected? 'auto_pca', 'contrasts', or a valid column name from the observations table. |
| `--exploratory-n-features` | integer | yes |  |  |  | 500 | Number of features selected before certain exploratory analyses. If -1, will use all features. |
| `--exploratory-palette-name` | string | yes |  |  |  | Set1 | Valid R palette name |
| `--exploratory-whisker-distance` | number |  |  |  |  | 1.5 | Length of the whiskers in boxplots as multiple of IQR. Defaults to 1.5. |

## features_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--control-features` | string (file path) |  |  |  |  |  | A text file listing technical features (e.g. spikes) |
| `--features` | string |  |  |  | matches ^\S+\.(csv\|tsv\|txt)$ |  | This parameter allows you to supply your own feature annotations. These can often be automatically derived from the GTF used upstream for RNA-seq, or from the Bioconductor annotation package (for affy arrays). |
| `--features-gtf-feature-type` | string |  |  |  |  | transcript | Where a GTF file is supplied, which feature type to use |
| `--features-gtf-table-first-field` | string |  |  |  |  | gene_id | Where a GTF file is supplied, which field should go first in the converted output table |
| `--features-id-col` | string | yes |  |  |  | gene_id | Feature ID attribute in the abundance table as well as in the GTF file (e.g. the gene_id field) |
| `--features-metadata-cols` | string |  |  |  |  | gene_id,gene_name,gene_biotype | Comma-separated string, specifies feature metadata columns to be used for exploratory analysis, platform-specific |
| `--features-name-col` | string | yes |  |  |  | gene_name | Feature name attribute in the abundance table as well as in the GTF file (e.g. the gene symbol field) |
| `--features-type` | string | yes |  |  |  | gene | Type of feature we have, often 'gene' |
| `--sizefactors-from-controls` | boolean |  |  |  |  |  | When set, use the control features in scaling/ normalisation |

## filtering

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--filtering-grouping-var` | string |  |  |  |  |  | An optional grouping variable to be used to calculate a min_samples value |
| `--filtering-min-abundance` | number | yes |  |  |  | 1.0 | Minimum abundance value |
| `--filtering-min-proportion` | number |  |  |  |  |  | A minimum proportion of observations, given as a number between 0 and 1, that must pass the threshold. Overrides minimum_samples |
| `--filtering-min-proportion-not-na` | number |  |  |  |  | 0.5 | A minimum proportion of observations, given as a number between 0 and 1, that must have a value (not NA) to retain the row/ feature (e.g. gene). |
| `--filtering-min-samples` | number |  |  |  |  | 1.0 | Minimum observations that must pass the threshold to retain the row/ feature (e.g. gene). |
| `--filtering-min-samples-not-na` | number |  |  |  |  |  | Minimum observations that must have a value (not NA) to retain the row/ feature (e.g. gene). Overrides filtering_min_proportion_not_na. |

## gene_set_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--gene-sets-files` | string |  |  |  |  | null | Gene sets in GMT or GMX-format; for GSEA: multiple comma-separated input files in either format are possible. For gprofiler2: A single file in GMT format is possible; this has lowest priority and will be overridden by --gprofiler2_token and --gprofiler2_organism. |

## generic_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--email-on-fail` | string |  |  |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary, only when pipeline fails. |
| `--help` | boolean |  | yes |  |  |  | Display help text. |
| `--hook-url` | string |  | yes |  |  |  | Incoming hook URL for messaging service |
| `--monochrome-logs` | boolean |  | yes |  |  |  | Do not use coloured log outputs. |
| `--plaintext-email` | boolean |  | yes |  |  |  | Send plain-text email instead of HTML. |
| `--publish-dir-mode` | string |  |  | symlink, rellink, link, copy, copyNoFollow, move |  | copy | Method used to save pipeline results to output directory. |
| `--validate-params` | boolean |  |  |  |  | true | Boolean whether to validate parameters against the schema at runtime |
| `--validationFailUnrecognisedParams` | boolean |  | yes |  |  |  | Validation of parameters fails when an unrecognised parameter is found. |
| `--validationLenientMode` | boolean |  | yes |  |  |  | Validation of parameters in lenient more. |
| `--validationShowHiddenParams` | boolean |  | yes |  |  |  | Show all params when using `--help` |
| `--version` | boolean |  | yes |  |  |  | Display version and exit. |

## gprofiler2

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--gprofiler2-background-column` | string |  |  |  |  |  | Which column to use as gene IDs in the background matrix. |
| `--gprofiler2-background-file` | string |  |  |  | matches ^\S+\.(csv\|tsv\|txt)$\|auto\|false |  | Path to CSV/TSV/TXT file that should be used as a background for the query; alternatively, 'auto' (default) or 'false'. |
| `--gprofiler2-correction-method` | string |  |  | gSCS, analytical, g_SCS, fdr, false_discovery_rate, bonferroni |  |  | The method that should be used for multiple testing correction. |
| `--gprofiler2-domain-scope` | string |  |  | annotated, known, custom, custom_annotated |  | annotated | How to calculate the statistical domain size. |
| `--gprofiler2-evcodes` | boolean |  |  |  |  | false | Whether to include evcodes in the results. |
| `--gprofiler2-max-qval` | number |  |  |  |  | 0.05 | Maximum q value used for significance testing. |
| `--gprofiler2-measure-underrepresentation` | boolean |  |  |  |  | false | Should underrepresentation be measured instead of overrepresentation? |
| `--gprofiler2-min-diff` | integer |  |  |  |  | 1 | How many genes must be differentially expressed in a pathway for it to be considered enriched? Default 1. |
| `--gprofiler2-organism` | string |  |  |  |  |  | Short name of the organism that is analyzed, e.g. hsapiens for homo sapiens. |
| `--gprofiler2-palette-name` | string |  |  |  |  | Blues | Valid R palette name |
| `--gprofiler2-run` | boolean |  |  |  |  |  | Set to run gprofiler2 and do a pathway enrichment analysis. |
| `--gprofiler2-significant` | boolean |  |  |  |  | true | Should only significant enrichment results be considered? |
| `--gprofiler2-sources` | string |  |  |  |  |  | On which source databases to run the gprofiler query |
| `--gprofiler2-token` | string |  |  |  |  |  | Token that should be used as a query. |

## gsea

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--gsea-make-sets` | boolean |  |  |  |  | true | Make detailed geneset report? |
| `--gsea-median` | boolean |  |  |  |  |  | Use median for class metrics |
| `--gsea-metric` | string |  |  | Signal2Noise, tTest, Ratio_of_Classes, Diff_of_Classes, log2_Ratio_of_Classes |  | Signal2Noise | Metric for ranking genes |
| `--gsea-norm` | string |  |  | meandiv, null |  | meandiv | Normalisation mode |
| `--gsea-nperm` | integer |  |  |  |  | 1000 | Number of permutations |
| `--gsea-num` | integer |  |  |  |  | 100 | Number of markers |
| `--gsea-order` | string |  |  | descending, ascending |  | descending | Gene list ordering mode |
| `--gsea-permute` | string |  |  | phenotype, gene_set |  | phenotype | Permutation type |
| `--gsea-plot-top-x` | integer |  |  |  |  | 20 | Plot graphs for the top sets of each phenotype |
| `--gsea-rnd-seed` | string |  |  |  |  | timestamp | Seed for permutation |
| `--gsea-rnd-type` | string |  |  | no_balance, equalize_and_balance |  | no_balance | Randomization mode |
| `--gsea-run` | boolean |  |  |  |  |  | Set to run GSEA to infer differential gene sets in contrasts |
| `--gsea-save-rnd-lists` | boolean |  |  |  |  |  | Save random ranked lists |
| `--gsea-scoring-scheme` | string |  |  | weighted, weighted_p2, weighted_p1.5, classic |  | weighted | Enrichment statistic |
| `--gsea-set-max` | integer |  |  |  |  | 500 | Max size: exclude larger sets |
| `--gsea-set-min` | integer |  |  |  |  | 15 | Min size: exclude smaller sets |
| `--gsea-sort` | string |  |  | real, absolute |  | real | Gene list sorting mode |
| `--gsea-zip-report` | boolean |  |  |  |  |  | Make a zipped file with all reports |

## input_output_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--contrasts` | string (file path) | yes |  |  | matches ^\S+\.(csv\|tsv\|txt)$ |  | A CSV file describing sample contrasts |
| `--input` | string (file path) | yes |  |  | matches ^\S+\.(csv\|tsv\|txt)$ |  | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) | yes |  |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |
| `--study-abundance-type` | string | yes |  |  |  | counts | Type of abundance measure used, platform-dependent |
| `--study-name` | string | yes |  |  |  | study | A string to identify results in the output directory |
| `--study-type` | string | yes |  | rnaseq, affy_array, maxquant, geo_soft_file |  | rnaseq | A string identifying the technology used to produce the data |

## institutional_config_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--config-profile-contact` | string |  | yes |  |  |  | Institutional config contact information. |
| `--config-profile-description` | string |  | yes |  |  |  | Institutional config description. |
| `--config-profile-name` | string |  | yes |  |  |  | Institutional config name. |
| `--config-profile-url` | string |  | yes |  |  |  | Institutional config URL link. |
| `--custom-config-base` | string |  | yes |  |  | https://raw.githubusercontent.com/nf-core/configs/master | Base directory for Institutional configs. |
| `--custom-config-version` | string |  | yes |  |  | master | Git commit id for Institutional configs. |

## limma_specific_options_microarray_only

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--limma-adjust-method` | string |  |  | holm, hochberg, hommel, bonferroni, BH, BY, fdr, null |  | BH | passed to topTable(), method used to adjust the p-values for multiple testing. |
| `--limma-block` | string |  |  |  |  | null | Sample sheet column to be used to derive a vector or factor specifying a blocking variable on the arrays |
| `--limma-confint` | boolean |  |  |  |  |  | passed to topTable(), logical, should confidence 95% intervals be output for logFC? Alternatively, can take a numeric value between zero and one specifying the confidence level required. |
| `--limma-correlation` | string |  |  |  |  | null | passed to lmFit(), the inter-duplicate or inter-technical replicate correlation |
| `--limma-lfc` | integer |  |  |  |  | 0 | passed to topTable(), minimum absolute log2-fold-change required |
| `--limma-method` | string |  |  | ls, robust |  | ls | passed to lmFit(), the fitting method |
| `--limma-ndups` | number |  |  |  |  |  | passed to lmFit(), positive integer giving the number of times each distinct probe is printed on each array. |
| `--limma-p-value` | number |  |  |  |  | 1.0 | cutoff value for adjusted p-values. Only genes with lower p-values are listed. |
| `--limma-proportion` | number |  |  |  |  | 0.01 | passed to eBayes(), a numeric value between 0 and 1, assumed proportion of genes which are differentially expressed |
| `--limma-robust` | boolean |  |  |  |  |  | passed to eBayes(), logical, should the estimation of df.prior and var.prior be robustified against outlier sample variances? |
| `--limma-spacing` | string |  |  |  |  | null | passed to lmFit(), positive integer giving the spacing between duplicate occurrences of the same probe, spacing=1 for consecutive rows. |
| `--limma-stdev-coef-lim` | string |  |  |  |  | 0.1,4 | passed to eBayes, comma separated string of two values, assumed lower and upper limits for the standard deviation of log2-fold-changes for differentially expressed genes |
| `--limma-trend` | boolean |  |  |  |  |  | passed to eBayes(), logical, should an intensity-dependent trend be allowed for the prior variance? |
| `--limma-winsor-tail-p` | string |  |  |  |  | 0.05,0.1 | passed to eBayes, comma separated string of length 1 or 2, giving left and right tail proportions of x to Winsorize. Used only when robust=TRUE. |

## max_job_request_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--max-cpus` | integer |  | yes |  |  | 16 | Maximum number of CPUs that can be requested for any single job. |
| `--max-memory` | string |  | yes |  | matches ^\d+(\.\d+)?\.?\s*(K\|M\|G\|T)?B$ | 128.GB | Maximum amount of memory that can be requested for any single job. |
| `--max-time` | string |  | yes |  | matches ^(\d+\.?\s*(s\|m\|h\|d\|day)\s*)+$ | 240.h | Maximum amount of time that can be requested for any single job. |

## observations_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--observations-id-col` | string | yes |  |  |  | sample | Column in the samples sheet to be used as the primary sample identifier |
| `--observations-name-col` | string |  |  |  |  |  | Column in the sample sheet to be used as the display identifier for observations. If unset, will use value of --observations_id_col. |
| `--observations-type` | string | yes |  |  |  | sample | Type of observation |

## proteus_input_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--proteus-measurecol-prefix` | string |  |  |  |  | LFQ intensity | Prefix of the column names of the MaxQuant proteingroups table in which the intensity values are saved; the prefix has to be followed by the sample names that are also found in the samplesheet. Default: 'LFQ intensity'; will search for both the prefix as entered and the prefix followed by one whitespace. |
| `--proteus-norm-function` | string |  |  | normalizeMedian, normalizeQuantiles |  | normalizeMedian | Normalization function to use on the MaxQuant intensities. |
| `--proteus-palette-name` | string |  |  |  |  | Set1 | Valid R palette name |
| `--proteus-plotmv-loess` | boolean |  |  |  |  | true | Should a loess line be added to the plot of mean-variance relationship of the conditions? Default: true. |
| `--proteus-plotsd-method` | string |  |  | violin, dist, box |  | violin | Which method to use for plotting sample distributions of the MaxQuant intensities; one of 'violin', 'dist', 'box'. |

## reference_genome_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--genome` | string |  |  |  |  |  | Name of iGenomes reference. |
| `--gtf` | string (file path) |  |  |  | matches ^\S+\.gtf(\.gz)? |  | Genome annotation file in GTF format |
| `--igenomes-ignore` | boolean |  | yes |  |  |  | Do not load the iGenomes reference config. |

## reporting_options

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--citations-file` | string |  |  |  |  | ${projectDir}/CITATIONS.md | A markdown file containing citations to include in the fiinal report |
| `--css-file` | string | yes |  |  |  | ${projectDir}/assets/nf-core_style.css | CSS to use to style the output, in lieu of the default nf-core styling |
| `--email` | string |  |  |  | matches ^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$ |  | Email address for completion summary. |
| `--logo-file` | string | yes |  |  |  | ${projectDir}/docs/images/nf-core-differentialabundance_logo_light.png | A logo to display in the report instead of the generic pipeline logo |
| `--report-author` | string |  |  |  |  | null | An author for reporting outputs |
| `--report-contributors` | string |  |  |  |  |  | Semicolon-separated string of contributor info that should be listed in the report. |
| `--report-description` | string |  |  |  |  | null | A description for reporting outputs |
| `--report-file` | string (file path) | yes |  |  | matches ^\S+\.Rmd$ | ${projectDir}/assets/differentialabundance_report.Rmd | Rmd report template from which to create the pipeline report |
| `--report-round-digits` | integer |  |  |  |  | 4 | To how many digits should numeric output in different modules be rounded? If -1, will not round. |
| `--report-scree` | boolean |  |  |  |  | true | Whether to generate a scree plot in the report |
| `--report-title` | string |  |  |  |  | null | A title for reporting outputs |

## shiny_app_settings

| parameter | type | required | hidden | allowed values | constraints | default | description |
|---|---|---|---|---|---|---|---|
| `--shinyngs-build-app` | boolean |  |  |  |  | true | Should a Shiny app be built? |
| `--shinyngs-deploy-to-shinyapps-io` | boolean |  |  |  |  |  | Should the app be deployed to shinyapps.io? |
| `--shinyngs-guess-unlog-matrices` | boolean |  |  |  |  | true | Should we guess the log status of matrices and unlog for the app? |
| `--shinyngs-shinyapps-account` | string |  |  |  |  | null | Your shinyapps.io account name |
| `--shinyngs-shinyapps-app-name` | string |  |  |  |  | null | The name of the app to push to in your shinyapps.io account |

<!-- Generated from nf-core/differentialabundance@3dd360fed0dca1780db1bdf5dce85e5258fa2253. Do not edit by hand. -->
