<p align="center">
  <img src="docs/images/nf-claw-logo-with-text.png" alt="nf-claw" width="220">
</p>

# nf-claw

A self-maintaining, token-minimal library of [nf-core](https://nf-co.re) pipelines for AI agents.
Each pipeline is a git submodule plus an auto-generated `skill.md` describing its declared
inputs, parameters, and run command. The pinned pipeline validates and executes the analysis.

**🌐 Live site: [danilomonge.github.io/nf-claw](https://danilomonge.github.io/nf-claw/)** — a data-driven
interface to the entire library (pipelines, parameters, documentation, and automation), rebuilt from the repository on every push.

## Layout
- `pipelines/<name>/` — `upstream/` (submodule, pinned to a release) + generated `skill.md` (run command, inputs, required parameters with allowed values/constraints, and parameter group maps) and `reference.md` (every parameter with required/hidden flags, allowed values, value constraints, and defaults).
- `runner/` — the `nfclaw` runtime (CLI, parameter validation, process isolation, provenance, chaining); the agent's primary tool.
- `librarian/` — builds context files, audits drift, and bumps submodules (invoked via `make`).
- `catalog.md` / `catalog.json` — index of available pipelines, including each pipeline's `input`
  (derived from its samplesheet schema), `output` (conditional on run settings), `summary`
  (upstream README description; in `skill.md` and `catalog.json`), and `tools` (from upstream `CITATIONS.md`).
- `sources.tsv` — upstream pipeline manifest (`name`, `url`, and version policy).
- `handoffs/` — chaining rules (`handoffs/<upstream>/<downstream>.json`), statically verified against pinned schemas by the drift gate.

Design details (the four zones and drift-free generation): [`docs/architecture.md`](docs/architecture.md).  
Version and engine compatibility (DSL2-only; parser compatibility): [`docs/compatibility.md`](docs/compatibility.md).  
Pipeline chaining and multi-stage handoffs: [`docs/chaining.md`](docs/chaining.md).  
Known issues and runtime troubleshooting: [`docs/known-issues.md`](docs/known-issues.md).  
Maintenance automation and drift checks: [`docs/updating.md`](docs/updating.md).  

## Quickstart
```bash
pip install -e .             # first time: puts `nfclaw` on PATH (or use `python3 -m runner <cmd>`)

nfclaw list                  # list all tracked pipelines and descriptions
nfclaw run rnaseq --input samplesheet.csv --outdir results -profile docker
nfclaw status results        # check status: success / running / outcome — from results/provenance/logs/run.log

# inspect the exact Nextflow command that would run without executing it
nfclaw run rnaseq --input samplesheet.csv --outdir results -profile docker --check

# reproduce a recorded run into a fresh target directory
./results/provenance/commands.sh                         # -> results.replay/

# verify a replayed run against the original
nfclaw verify results.replay --against results           # structural check (file inventory)
nfclaw verify results.replay --against results --strict  # byte-level agreement check

# run a specific (non-latest) release — default is always the pinned latest
nfclaw versions rnaseq                                   # list release tags (pinned latest flagged; dev last)
nfclaw show rnaseq --pipeline-version 3.14.0             # view skill.md generated on demand for that release
nfclaw run  rnaseq --pipeline-version 3.14.0 --input samplesheet.csv --outdir results -profile docker

# run unreleased development code: the head of nf-core's `dev` branch (like `nextflow run -r dev`),
# resolved to its exact commit at run time and recorded in provenance
nfclaw show rnaseq --pipeline-version dev                # view skill.md generated from current dev head
nfclaw run  rnaseq --pipeline-version dev --input samplesheet.csv --outdir results -profile docker

# pin the Nextflow engine / set NXF_* variables for a run (both recorded in provenance)
nfclaw run rnaseq --nxf-ver 25.10.4 --input ss.csv --outdir results -profile docker  # pin engine version
nfclaw run rnaseq --nxf-env NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true ...      # IPv6-only host (JVM → GitHub)

# chain pipelines: each stage starts only after the previous one succeeds, preparing inputs from outputs
nfclaw chain edges fetchngs                              # list pipelines fetchngs can feed
nfclaw chain run spec.json --outdir /abs/chain --check   # validate stages and handoffs; run nothing
nfclaw chain run spec.json --outdir /abs/chain           # run full chain; --resume continues a failed chain
nfclaw chain status /abs/chain                           # report stage status and verify cryptographic lineage

# cap process requests for machines smaller than nf-core HPC defaults
nfclaw run rnaseq --input ss.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h   # Nextflow process.resourceLimits
```

The editable install is intentional: `nfclaw` reads pinned submodules and generated context from
this repository checkout. A standalone wheel contains the Python runtime but not the pipeline library, so the
CLI exits with a descriptive setup error instead of silently reporting an empty catalog.

## Provenance, Replay & Verification

Every execution automatically generates a complete provenance record in `<outdir>/provenance/`:
- **`logs/run.log`** — Unified launch log recording command arguments, host, PID, Nextflow output streams, and a terminal outcome line (`==> nfclaw run finished <timestamp>: <outcome>`).
- **`commands.sh`** — Standalone bash script reproducing the exact execution into a fresh directory (default `<outdir>.replay`). Overwriting an existing output directory is refused to prevent artifact collisions.
- **`replay_guard.py`** — Pre-execution dependency validator executed by `commands.sh` before Nextflow starts. Verifies that tracked pipeline commits, local input files (including paths declared in samplesheets), and external configs (`-c`) match their recorded SHA-256 manifests (`source.sha256`, `inputs.sha256`, `configs.sha256`).
- **`run_manifest.json`** — Machine-readable summary capturing execution outcome, duration, engine pin, resolved parameters, environment variables (with sensitive credentials redacted), and chain linkage.
- **`inputs.sha256` / `outputs.sha256`** — Cryptographic digests of all inputs and generated output files.
- **Run Isolation & Locking** — On POSIX systems, `nfclaw run` holds an exclusive non-blocking sibling flock (`.{outdir.name}.nfclaw.lock`). Concurrent or overlapping runs into the same directory fail fast, eliminating race conditions.
- **Verification (`nfclaw verify`)** — Compares a replayed output directory against the original. Default mode verifies structural equivalence (file inventory matching; timestamped reports in `pipeline_info/` are paired without path collisions; changed bytes are reported for inspection). `--strict` mode requires byte-identical agreement across all non-timestamped files.

## Maintain
```bash
make build     # regenerate skill.md, reference.md, and catalog.* from pinned submodules
make update    # bump submodules to newest release tags, then rebuild context
make check     # run schema drift gate and complete test suite
make test      # run unit and integration test suite
```

## Adding Pipelines
Append a line to `sources.tsv` (`name<TAB>url<TAB>latest-release`), then run:
```bash
git submodule add <url> pipelines/<name>/upstream
git -C pipelines/<name>/upstream checkout tags/<X.Y.Z>   # pin to a release tag (not default branch)
make build
make check
```
Full contributor guidelines, naming constraints, and test procedures are in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## How It Stays Current
Five automated GitHub workflows keep the library and website continuously up to date:
- **`auto-update.yml`** (daily): Finds each pipeline's newest release via `git ls-remote --tags`
  (pure git, no API rate limits), checks out that tag, regenerates context files, runs unit tests, the drift gate,
  and Nextflow acceptance tests, then auto-merges the PR to trigger a site rebuild.
- **`discover-pipelines.yml`** (weekly): Identifies newly released **DSL2** nf-core pipelines,
  scaffolds submodules and context, verifies Nextflow acceptance (`nextflow -preview` requiring strict exit code 0),
  and auto-merges validated additions.
- **`deploy-pages.yml`** (on every push to `main`): Builds the website as a static export and publishes
  it to GitHub Pages, ensuring the live portal reflects the repository commit history and catalog.
- **`smoke.yml`** (weekly + on runner/pipeline changes): Builds and preflights demo commands across all pipelines
  (`nfclaw run --check --demo`), validating schemas, parameter composition, and submodule integrity without execution.
- **`nextflow-validate.yml`** (nightly + on pipeline changes): Runs `nextflow -preview` with `-profile test,docker`
  for every pipeline using its declared minimum engine version. Validates pipeline compilation, profile resolution,
  schema validation, and DAG construction. Nonzero exits or remote staging failures fail the gate.

More details on automation and drift prevention: [`docs/updating.md`](docs/updating.md).

## Scientific Validation & Limitations

nf-claw validates declared inputs, checks parameters against schemas, assembles commands, isolates execution,
and tracks cryptographic provenance. Successful parameter validation, exit code 0 completion, or identical output
filenames alone do not establish biological or analytical accuracy.

Before relying on results for scientific research:
- Validate the selected pipeline, parameters, and reference data using appropriate domain-specific truth datasets.
- Use `nfclaw verify ... --strict` to check byte agreement; use format-aware tools to inspect differences in scientific outputs.
- Review [known issues](docs/known-issues.md) for documented engine boundaries, upstream bug workarounds, and runtime guidance.

## Citation & Attribution
**The pipelines themselves are the work of the [nf-core](https://nf-co.re) community** — the heart of the library — and are wrapped **unmodified** as pinned git submodules; each maintains its own authors, license, and citations.

**nf-claw** was created by **Danilo Monge** (Eberhard Karls Universität Tübingen) and adapts design concepts and repository structure from [ClawBio](https://clawbio.ai) — created by **Manuel Corpas** (MIT; copyright retained in [`LICENSE`](LICENSE), provenance in [`NOTICE`](NOTICE)).

If you use nf-claw in your research, cite it via [`CITATION.cff`](CITATION.cff), alongside its foundational tools:
- **Nextflow** (workflow engine) — Di Tommaso P, *et al.* Nextflow enables reproducible computational workflows. *Nat Biotechnol* **35**, 316–319 (2017). [doi:10.1038/nbt.3820](https://doi.org/10.1038/nbt.3820)
- **nf-core** (pipeline framework) — Ewels PA, *et al.* The nf-core framework for community-curated bioinformatics pipelines. *Nat Biotechnol* **38**, 276–278 (2020). [doi:10.1038/s41587-020-0439-x](https://doi.org/10.1038/s41587-020-0439-x)
- The **specific pipeline** executed — listed in `pipelines/<name>/upstream/CITATIONS.md`.
- **ClawBio** (predecessor library by Manuel Corpas) — Corpas M. ClawBio: Bioinformatics-Native AI Agent Skill Library. Zenodo (2026). [doi:10.5281/zenodo.19420648](https://doi.org/10.5281/zenodo.19420648)

nf-claw is MIT-licensed and includes components adapted from ClawBio (© Manuel Corpas, MIT — see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE)); upstream nf-core pipelines are MIT, and Nextflow is Apache-2.0.

Requires: Python 3.11+, git, Nextflow (Java 17+), Docker or Singularity.
