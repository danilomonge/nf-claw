# Chaining pipelines

`nfclaw chain run` runs several nf-core pipelines in sequence — fetchngs, then rnaseq, then
differentialabundance — starting each one only after the one before it **succeeded**, and preparing
its inputs from that one's outputs. It is a linear runner, not a workflow engine: no DAG, no
scheduler, no daemon. Every stage is an ordinary `nfclaw run`, with the same checks, run log and
provenance bundle.

```bash
nfclaw chain edges                                   # which pipeline can follow which
nfclaw chain run spec.json --outdir /abs/chain --check   # validate everything, run nothing
nfclaw chain run spec.json --outdir /abs/chain           # run it
nfclaw chain status /abs/chain                           # stages, versions, verified lineage
```

## The spec

A JSON file (YAML when `pyyaml` is installed). Relative paths in it mean what they would on the
command line (they resolve against the current directory); the spec nfclaw records is absolute.

```json
{
  "profile": "docker",
  "nxf_env": {"NXF_JVM_ARGS": "-Djava.net.preferIPv6Addresses=true"},
  "limits": {"cpus": 8, "memory": "30.GB", "time": "12.h"},
  "stages": [
    {"pipeline": "fetchngs", "input": "/data/ids.csv", "retries": 2},
    {"pipeline": "rnaseq", "params": {"genome": "GRCh38"}, "pipeline_version": "3.27.0"}
  ]
}
```

**Run options** — on the chain, and on any stage to override it for that stage (`nxf_env` merges
over the chain's; the others replace it). Each means what the `nfclaw run` flag of the same name does:

| key | meaning |
|---|---|
| `profile` | Nextflow profile, default `docker` |
| `nxf_ver` | pin the Nextflow engine (`NXF_VER`) — releases of different ages can need different engines |
| `nxf_env` | `NXF_*` variables, e.g. the IPv6 JVM flag |
| `config` | extra Nextflow config files (`-c`) |
| `limits` | `{"cpus", "memory", "time"}` — the `process.resourceLimits` ceiling (`--limit-*`) |
| `allow_spaces` | chain only: allow spaces in paths |

**Stage keys:**

| key | meaning |
|---|---|
| `pipeline` | required — a pipeline of the library |
| `id` | default: the pipeline name; must be unique (`^[a-z0-9][a-z0-9_-]*$`) |
| `input` | the stage's own `--input` (also accepted as `params.input`); usually only the first stage has one |
| `params` | the stage's own pipeline parameters, as on the command line (`skip-busco` = `skip_busco`) — look them up in its `reference.md` |
| `params_file` | a params file for the stage |
| `pipeline_version` | a release, or `dev` (as `--pipeline-version`) |
| `demo` | add the release's `test` profile (its small references and resource ceiling); the handed-over `--input` still wins, because a params file beats a profile |
| `retries` | relaunch the stage (with Nextflow's `-resume`) after a pipeline failure — never after a validation error or a timeout. Default 0 |
| `handoff` | an inline rule (or a path to a rule file) used *into* this stage instead of the registry's |

A value a stage sets itself wins over the value handed to it (nfclaw says so). A rule that needs a
parameter on the stage before it (`--nf-core-pipeline rnaseq` on fetchngs) sets it there; a stage
setting it to something else is refused before anything runs.

## What happens

1. **Before anything launches**: every stage's pipeline and version are resolved, every handoff is
   checked against both pipelines' schemas, every stage's own parameters are validated as
   `nfclaw run --check` would (the ones a handoff will supply are deferred), and `nextflow config`
   parses every stage's configuration with the engine it will run under. A typo in the last
   stage, or a release the engine cannot parse, fails here — not after the first stage ran for hours.
2. Stage 1 runs in `<outdir>/01-<id>/`. Only when it **succeeded** (Nextflow exited 0 and its
   provenance bundle says `"outcome": "success"`) does the chain continue.
3. The handoff writes the next stage's inputs into `<outdir>/chain/handoffs/02-<id>/` — a samplesheet
   with absolute paths, validated against the next pipeline's samplesheet schema — and records
   where every value came from.
4. Stage 2 runs in `<outdir>/02-<id>/`, and so on.

```
<outdir>/
  01-fetchngs/                    an ordinary nfclaw run: results + provenance/
  02-rnaseq/
  chain/
    chain.json                    the spec as run (absolute paths)
    state.json                    chain id, outcome, each stage's status, version, commit, attempts
    handoffs/02-rnaseq/input.csv  the samplesheet stage 2 ran with
    handoffs/02-rnaseq/handoff.json   the rule, the values, and their lineage
    logs/chain.log                the chain's log — its last line states the outcome
```

A chain started in the background (`nohup nfclaw chain run … &`) is polled with
`tail -n 1 <outdir>/chain/logs/chain.log` — its last line is
`==> nfclaw chain finished <time>: <outcome>` (`success`, `failed at stage 02-rnaseq: failed (exit
status 1)`, `failed at stage 02-rnaseq: handoff`, `terminated by SIGTERM (stage 01-fetchngs)`,
`timed out after N s`) — and stopped with `kill <pid>`: the running stage's Nextflow is shut down and
nothing further starts. Each stage keeps its own `provenance/logs/run.log`.

## Handoff rules

A rule says how one pipeline's finished run becomes the next pipeline's parameters. The library's
rules are data in `handoffs/<upstream>/<downstream>.json`; `nfclaw chain edges [pipeline]` lists them,
and each pipeline's `skill.md` has a **Chaining** section. Where a pipeline publishes a samplesheet,
and which columns it holds, is in no schema — but everything a rule claims about the two pipelines'
*parameters and samplesheet columns* is checked against their pinned schemas by the drift gate, so a
release that breaks a rule is caught the day it is pinned.

```json
{
  "description": "one line: shown in skill.md and `nfclaw chain edges`",
  "upstream_params": {"nf_core_pipeline": "rnaseq"},
  "params": {
    "input": {"samplesheet": "samplesheet/samplesheet.csv",
              "provides": ["sample", "fastq_1", "fastq_2", "strandedness"]}
  }
}
```

`upstream_params` are set on the upstream stage so it writes what is handed over. `params` maps each
downstream parameter to one source:

| source | meaning | example |
|---|---|---|
| `samplesheet` | **direct handoff**: a sheet the upstream wrote for the target, copied. `provides` lists the columns it is guaranteed to have (the static check uses them); optional `rename` `{old: new}` and `set` `{column: template}`, where `{column}` is that row's value, and `drop_rows_not_allowed` `[column, …]`: drop the rows whose value in those columns the downstream's schema does not allow (recorded and reported). Path columns (per the downstream's samplesheet schema) are made absolute against the upstream outdir. | fetchngs → rnaseq; fetchngs → mag (`rename` + `set`) |
| `build` | **mapping**: a sheet built from output files. `rows` is a pattern with `{placeholders}` — one row per matching file; `columns` maps each column to a template. A path column's template names a file under the upstream outdir, which must exist unless it ends in `?` (then it is left empty). Optional `format`: `csv` or `tsv`. | bamtofastq → rnaseq |
| `file` | one result file: a glob that must match exactly one, or an ordered list of globs (the first that matches anything wins) | rnaseq → differentialabundance `--matrix` |
| `upstream_param` | a value the upstream run used: from its `pipeline_info/params_*.json` (every resolved parameter, including a profile's), else its `provenance/params.json` | rnaseq `--gtf` → differentialabundance `--gtf` |

Any source may be `"optional": true`: a source that cannot be produced leaves the parameter unset
instead of failing. Paths and patterns stay inside the upstream outdir (relative, no `..`).

A stage can use its own rule instead of the registry's — `"handoff": {...}` inline, or a path to a
rule file — for a pair the registry lacks, or to fix a case it does not cover.

### Adding a rule to the library
1. Write `handoffs/<upstream>/<downstream>.json` (read the upstream's `docs/output.md` for where it
   publishes the file, and the downstream's samplesheet schema for the columns).
2. `python3 -m librarian.check_drift` — the rule must fit both pinned schemas.
3. `make build` — regenerates the Chaining sections of `skill.md` and the catalog.
4. `nfclaw chain run spec.json --outdir DIR --check`, then one real chain.

## Failure, retry and resume

| event | what happens |
|---|---|
| a problem found before launch | nothing runs; exit 1 |
| a stage fails and has `retries` left | it is relaunched with `-resume` (cached tasks reused); every attempt is in `state.json` |
| a stage fails for good (or with a validation error, or a timeout) | the chain stops; later stages stay `pending`; exit 1 |
| a handoff cannot be produced (`[handoff_failed]`) | the upstream stays succeeded; the next stage is not launched |
| `kill`, a closing terminal, Ctrl-C | the running stage is stopped cleanly; exit 128+signal / 130 |

`nfclaw chain run [spec.json] --outdir DIR --resume` continues a chain (without a spec it re-reads
`chain/chain.json`). Stages that succeeded are skipped — and frozen: a spec that changes one of them
(its pipeline, version, input, params or handoff) is refused; use a fresh `--outdir` for that. The
stage that failed may be edited — that is how it is fixed — and resumes with Nextflow's cache; stages
may be appended to extend a finished chain. `--timeout SECONDS` bounds the whole chain.

## Provenance and lineage

Each stage's `provenance/run_manifest.json` carries a `chain` record: the chain's id, its record
directory, the stage, and — for every stage but the first — the run that fed it and the SHA-256 of
the handoff record. `handoff.json` keeps the rule exactly as applied, every value handed over, the
snapshot's hash, and, for every upstream result a value was derived from, the digest the upstream run
recorded in its `outputs.sha256`. The snapshot is also the downstream's `--input`, so its own
`inputs.sha256` hashes it.

`nfclaw chain status DIR` (DIR is the chain, or any one of its stages) reconstructs the chain and
verifies each link — the downstream ran with exactly that handoff, the snapshot is unchanged and is
the input it hashed, and every file it was derived from is what the upstream produced — and exits 1
if any link is broken.

To reproduce a chain: `nfclaw chain run DIR/chain/chain.json --outdir FRESH`, then
`nfclaw verify FRESH/NN-<stage> --against DIR/NN-<stage>` per stage. (Each stage's own
`provenance/commands.sh` still replays that stage alone, against the original handoff.)
