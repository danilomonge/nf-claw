---
name: proteinfamilies
pipeline: nf-core/proteinfamilies
version: 2.4.0
commit: ec55856845ba2396a9d32d23b1617e6c1b992e87
description: Generate protein family level models (Multiple Sequence Alignments (MSAs), Hidden Markov Models (HMMs)) starting from a FASTA amino acid sequence file.
summary: nf-core/proteinfamilies is a bioinformatics pipeline that generates protein families from amino acid sequences and/or updates existing families with new sequences. It takes a protein fasta file as input, clusters the sequences and then generates protein family Hidden Markov Models (HMMs) along with their multiple sequence alignments (MSAs). Optionally, paths to existing family HMMs and MSAs can be given (must have matching base filenames one-to-one) in order to update with new sequences in case of matching hits.
has_samplesheet: true
input: samplesheet (sample, fasta, existing_hmms_to_update, existing_msas_to_update)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions); MultiQC report
tools: SeqFu, SeqKit, MMseqs2, FAMSA, mafft, ClipKIT, hmmer, HH-suite3, Biopython, CMAPLE, MultiQC
---
# proteinfamilies

nf-core/proteinfamilies is a bioinformatics pipeline that generates protein families from amino acid sequences and/or updates existing families with new sequences. It takes a protein fasta file as input, clusters the sequences and then generates protein family Hidden Markov Models (HMMs) along with their multiple sequence alignments (MSAs). Optionally, paths to existing family HMMs and MSAs can be given (must have matching base filenames one-to-one) in order to update with new sequences in case of matching hits.

## Run it
```bash
git submodule update --init pipelines/proteinfamilies/upstream   # first time only
nfclaw run proteinfamilies --input samplesheet.csv --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/proteinfamilies/upstream -profile docker --input samplesheet.csv --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions proteinfamilies` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show proteinfamilies --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
| column | type | required | allowed values | constraints |
|---|---|---|---|---|
| `sample` | string | yes |  | matches ^\S+$ |
| `fasta` | string (file path) | yes |  | matches ^([\S\s]*\/)?[^\s\/]+\.(fa\|fasta\|faa\|fas)(\.gz)?$ |
| `existing_hmms_to_update` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.tar\.gz$ |
| `existing_msas_to_update` | string (file path) | no |  | matches ^([\S\s]*\/)?[^\s\/]+\.tar\.gz$ |

`--input` must match `^\S+\.csv$`.

The samplesheet is a CSV with this exact header; fill each value per the table above and `reference.md` (no example value is invented here):
```csv
sample,fasta,existing_hmms_to_update,existing_msas_to_update
```

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--input` | string (file path) |  |  | matches ^\S+\.csv$ | Path to comma-separated file '.csv' containing information about the samples in the experiment. |
| `--outdir` | string (directory path) |  |  |  | The output directory where the results will be saved. You have to use absolute paths to storage on Cloud infrastructure. |

## Other parameters
Beyond the required parameters above, every other parameter is optional. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any required parameters already listed above):
- `alignment_params` (12 parameters)
- `clustering_params` (8 parameters)
- `downstream_params` (2 parameters)
- `generic_options` (15 parameters)
- `input_output_options` (4 parameters)
- `institutional_config_options` (7 parameters)
- `phylogeny_params` (1 parameter)
- `quality_check_params` (4 parameters)
- `redundancy_params` (10 parameters)
- `update_params` (2 parameters)

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). A MultiQC HTML report aggregates QC across steps. `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/proteinfamilies/blob/2.4.0/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: SeqFu, SeqKit, MMseqs2, FAMSA, mafft, ClipKIT, hmmer, HH-suite3, Biopython, CMAPLE, MultiQC.

Full list with references: https://github.com/nf-core/proteinfamilies/blob/2.4.0/CITATIONS.md

## Demo
```bash
nfclaw run proteinfamilies --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/proteinfamilies/blob/2.4.0/docs/usage.md

<!-- Generated from nf-core/proteinfamilies@ec55856845ba2396a9d32d23b1617e6c1b992e87. Do not edit by hand. -->
