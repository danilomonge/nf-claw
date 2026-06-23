---
name: genomeassembler
pipeline: nf-core/genomeassembler
version: 1.1.0
commit: ccf1b89898cb720f46a966029c3a60dbcc25b012
description: Assemble genomes from long ONT or pacbio HiFi reads
summary: nf-core/genomeassembler is a bioinformatics pipeline that carries out genome assembly, polishing and scaffolding from long reads (ONT or pacbio). Assembly can be done via flye or hifiasm, polishing can be carried out with medaka (ONT), or pilon (requires short-reads), and scaffolding can be done using LINKS, Longstitch, or RagTag (if a reference is available). Quality control includes BUSCO, QUAST and merqury (requires short-reads). Currently, this pipeline does not implement phasing of polyploid genomes or HiC scaffolding.
has_samplesheet: true
input: samplesheet (sample, ontreads, hifireads, ref_fasta, ref_gff, shortread_F, shortread_R, paired)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions)
tools: lima, nanoq, porechop, TrimGalore, hifiasm, flye, pilon, medaka, LINKS, longstitch, RagTag, liftoff, BUSCO, genomescope2, jellyfish, meryl, QUAST, minimap2, samtools
---
# genomeassembler

nf-core/genomeassembler is a bioinformatics pipeline that carries out genome assembly, polishing and scaffolding from long reads (ONT or pacbio). Assembly can be done via flye or hifiasm, polishing can be carried out with medaka (ONT), or pilon (requires short-reads), and scaffolding can be done using LINKS, Longstitch, or RagTag (if a reference is available). Quality control includes BUSCO, QUAST and merqury (requires short-reads). Currently, this pipeline does not implement phasing of polyploid genomes or HiC scaffolding.

## Run it
```bash
git submodule update --init pipelines/genomeassembler/upstream   # first time only
nfclaw run genomeassembler --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/genomeassembler/upstream -profile docker --input samplesheet.csv --outdir results
```

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `ontreads` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `hifireads` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `ref_fasta` | string (file path) | no |  | matches ^\S+\.f(n\|ast)?a |
| `ref_gff` | string (file path) | no |  | matches ^\S+\.gff(3)? |
| `shortread_F` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `shortread_R` | string (file path) | no |  | matches ^\S+\.f(ast)?q\.gz$ |
| `paired` | boolean | no |  |  |

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,ontreads,hifireads,ref_fasta,ref_gff,shortread_F,shortread_R,paired
```

## Required parameters
| parameter | type | allowed values | constraints | description |
|---|---|---|---|---|
| `--input` | string (file path) |  | matches ^\S+\.csv$ | Path to comma-separated file containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `annotations_options` (1 parameter)
- `assembly_options` (6 parameters)
- `general_parameters` (3 parameters)
- `generic_options` (8 parameters)
- `hifi_options` (3 parameters)
- `input_output_options` (3 parameters)
- `institutional_config_options` (6 parameters)
- `ont_options` (7 parameters)
- `polishing_options` (3 parameters)
- `qc_options` (6 parameters)
- `scaffolding_options` (3 parameters)
- `short_read_options` (3 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/genomeassembler/blob/1.1.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: lima, nanoq, porechop, TrimGalore, hifiasm, flye, pilon, medaka, LINKS, longstitch, RagTag, liftoff, BUSCO, genomescope2, jellyfish, meryl, QUAST, minimap2, samtools.

Full list with references: https://github.com/nf-core/genomeassembler/blob/1.1.0/CITATIONS.md

## Demo
```bash
nfclaw run genomeassembler --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/genomeassembler/blob/1.1.0/docs/usage.md

<!-- Generated from nf-core/genomeassembler@ccf1b89898cb720f46a966029c3a60dbcc25b012. Do not edit by hand. -->
