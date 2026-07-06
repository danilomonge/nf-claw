---
name: methylong
pipeline: nf-core/methylong
version: 2.0.0
commit: 3513e80df682ad20f42d6429a2ee142b606949b5
description: Extract methylation calls from long reads
summary: nf-core/methylong is a bioinformatics pipeline that is tailored for long-read methylation calling. This pipeline requires a genome reference as input, and can take either modification-basecalled ONT reads, PacBio HiFi reads (modBam), raw sequencing Pod5 reads or raw Bam reads. The ONT workflow includes modcalling (optional), preprocessing (trim and repair) of reads, genome alignment and methylation calling. The PacBio HiFi workflow includes modcalling (optional), genome alignment and methylation calling. Methylation calls are extracted into BED/BEDGRAPH format, readily for direct downstream analysis. The downstream workflow includes SNV calling, phasing and DMR analysis.
has_samplesheet: true
input: samplesheet (group, sample, path, ref, method)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: FastQC, MultiQC, samtools, gunzip, pigz, minimap2, pbmm2, dorado, porechop, modkit, pb-CpG-tools, Clair3, WhatsHap, gawk, DSS, jasmine, ccsmeth, fibertools
---
# methylong

nf-core/methylong is a bioinformatics pipeline that is tailored for long-read methylation calling. This pipeline requires a genome reference as input, and can take either modification-basecalled ONT reads, PacBio HiFi reads (modBam), raw sequencing Pod5 reads or raw Bam reads. The ONT workflow includes modcalling (optional), preprocessing (trim and repair) of reads, genome alignment and methylation calling. The PacBio HiFi workflow includes modcalling (optional), genome alignment and methylation calling. Methylation calls are extracted into BED/BEDGRAPH format, readily for direct downstream analysis. The downstream workflow includes SNV calling, phasing and DMR analysis.

## Run it
```bash
git submodule update --init pipelines/methylong/upstream   # first time only
nfclaw run methylong --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/methylong/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions methylong` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show methylong --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `group` | string | yes |  | matches ^\S+$ |
| `sample` | string | yes |  | matches ^\S+$ |
| `path` | string | yes |  |  |
| `ref` | string (file path) | yes |  | matches ^\S+\.(fa\|fasta\|fna)(\.gz)?$ |
| `method` | string | yes | ont, pacbio |  |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
group,sample,path,ref,method
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  |  | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `alignment_options` (2 parameters)
- `dmr_options` (6 parameters)
- `fiberseq_options` (1 parameter)
- `generic_options` (8 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (6 parameters)
- `mod_calling_options` (6 parameters)
- `mod_pileup_options` (6 parameters)
- `multiqc` (8 parameters)
- `preprocessing_options` (2 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/methylong/blob/2.0.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: FastQC, MultiQC, samtools, gunzip, pigz, minimap2, pbmm2, dorado, porechop, modkit, pb-CpG-tools, Clair3, WhatsHap, gawk, DSS, jasmine, ccsmeth, fibertools.

Full list with references: https://github.com/nf-core/methylong/blob/2.0.0/CITATIONS.md

## Demo
```bash
nfclaw run methylong --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/methylong/blob/2.0.0/docs/usage.md

<!-- Generated from nf-core/methylong@3513e80df682ad20f42d6429a2ee142b606949b5. Do not edit by hand. -->
