---
name: drugresponseeval
pipeline: nf-core/drugresponseeval
version: 1.2.2
commit: 84cb752a7ca4584fcb95fcb7492aceb4137a3df7
description: This pipeline evaluates drug response models in various settings on a variety of datasets.
summary: DrEval is a bioinformatics framework that includes a PyPI package (drevalpy) and a Nextflow pipeline (this repo). DrEval ensures that evaluations are statistically sound, biologically meaningful, and reproducible. DrEval simplifies the implementation of drug response prediction models, allowing researchers to focus on advancing their modeling innovations by automating standardized evaluation protocols and preprocessing workflows. With DrEval, hyperparameter tuning is fair and consistent. With its flexible model interface, DrEval supports any model type, ranging from statistical models to complex neural networks. By contributing your model to the DrEval catalog, you can increase your work's exposure, reusability, and transferability.
has_samplesheet: false
input: parameters (no samplesheet)
output: --outdir/ (per-module results); pipeline_info/ (reports, versions)
tools: DrEvalPy, CurveCurator, DIPK, MOLI, SRMF, SuperFELT
---
# drugresponseeval

DrEval is a bioinformatics framework that includes a PyPI package (drevalpy) and a Nextflow pipeline (this repo). DrEval ensures that evaluations are statistically sound, biologically meaningful, and reproducible. DrEval simplifies the implementation of drug response prediction models, allowing researchers to focus on advancing their modeling innovations by automating standardized evaluation protocols and preprocessing workflows. With DrEval, hyperparameter tuning is fair and consistent. With its flexible model interface, DrEval supports any model type, ranging from statistical models to complex neural networks. By contributing your model to the DrEval catalog, you can increase your work's exposure, reusability, and transferability.

## Run it
```bash
git submodule update --init pipelines/drugresponseeval/upstream   # first time only
nfclaw run drugresponseeval --outdir results -profile docker
# raw equivalent (the submodule is already pinned to this release, so no -r is needed):
nextflow run pipelines/drugresponseeval/upstream -profile docker --outdir results
```

This is the pinned latest release. To run a different one, list the available releases with `nfclaw versions drugresponseeval` and add `--pipeline-version X.Y.Z` to the command above (`nfclaw show drugresponseeval --pipeline-version X.Y.Z` prints that release's docs).

## Inputs
This pipeline does not use a samplesheet; configure inputs via parameters.

## Required parameters
| parameter | type | default | allowed values | constraints | description |
|---|---|---|---|---|---|
| `--models` | string | NaiveDrugMeanPredictor |  |  | Model to be tested. |
| `--baselines` | string | NaiveMeanEffectsPredictor |  |  | Baselines to be tested. |
| `--run-id` | string | my_run |  |  | Run name for the pipeline. The subdirectory in results will be named like this. |
| `--dataset-name` | string | CTRPv2 |  |  | Name of the dataset. Pre-supplied datasets are CTRPv2, CTRPv1, CCLE, GDSC1, GDSC2, TOYv1, TOYv2, BeatAML2, and PDX_Bruna. |
| `--outdir` | string (directory path) | results |  |  | The output directory where the results will be saved. Default is results/ |
| `--test-mode` | string | LCO |  | matches ^((LPO\|LCO\|LTO\|LDO)?,?)*(?<!,)$ | Run the pipeline in test mode LPO (Leave-random-Pairs-Out), LCO (Leave-Cell-line-Out), or LDO (Leave-Drug-Out). |

## Other parameters
Every parameter not listed above is optional as far as the schema is concerned. [reference.md](reference.md) documents them all — type, default, allowed values and constraints — organised into these groups (counts are full group sizes, so they include any parameter already listed above):
- **Additional options** (`additional_options`) — 7 parameters
- **Data options** (`data_options`) — 4 parameters
- **Generic options** (`generic_options`) — 11 parameters
- **Input/output options** (`input_output_options`) — 4 parameters
- **Institutional config options** (`institutional_config_options`) — 6 parameters
- **Mode options (LPO/LCO/LTO/LDO)** (`mode_options`) — 1 parameter
- **Model options** (`model_options`) — 2 parameters
- **Randomization options** (`randomization_options`) — 2 parameters
- **Robustness options** (`robustness_options`) — 1 parameter

## Resources
A real (non-`--demo`) run requests the resources the pipeline's `conf/base.config` asks for, which are sized for a server — a single step can request far more memory than a workstation has, and Nextflow retries a failed step with more still. If a run fails with `Process requirement exceeds available memory` (or CPUs), cap every request, and every retry, at what this machine actually has:

```bash
nfclaw run drugresponseeval --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```

nfclaw turns those into Nextflow's `process.resourceLimits` and passes them as a `-c` config — the mechanism nf-core prescribes for exactly this ([docs](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)). Set them to the machine's real capacity. The generated config is kept in `<outdir>/provenance/`, so `commands.sh` replays the run under the same ceiling.

## Outputs
Results land in `--outdir`, organised into one sub-directory per pipeline step/module; standardized run metadata in `<outdir>/pipeline_info/` (execution report, software versions). `nfclaw run` also writes `<outdir>/provenance/` with the exact params file and run logs; unless `--no-provenance` it adds a run manifest (pinned version, commit and exact command), input/output SHA-256 checksums, and a replayable `commands.sh`.

The exact output files and directory layout for this release are documented upstream: https://github.com/nf-core/drugresponseeval/blob/1.2.2/docs/output.md

## Tools this pipeline runs
The tools/methods this pipeline runs, per the authors' own list: DrEvalPy, CurveCurator, DIPK, MOLI, SRMF, SuperFELT.

Full list with references: https://github.com/nf-core/drugresponseeval/blob/1.2.2/CITATIONS.md

## Demo
```bash
nfclaw run drugresponseeval --demo --outdir results   # adds the upstream test profile (-profile test,docker)
```

## Full reference
Every parameter — name, type, required, hidden, allowed values, constraints, default and description — is in [reference.md](reference.md). Use it as the source of truth; do not guess flags. Nextflow's nf-schema validates every parameter against this schema at runtime, so an unknown or invalid value fails fast. Upstream usage: https://github.com/nf-core/drugresponseeval/blob/1.2.2/docs/usage.md

<!-- Generated from nf-core/drugresponseeval@84cb752a7ca4584fcb95fcb7492aceb4137a3df7. Do not edit by hand. -->
