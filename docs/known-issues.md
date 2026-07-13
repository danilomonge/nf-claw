# Known issues & troubleshooting

Most run-time failures fall into two buckets: **environment** (your host or path — fixable with
an `nfclaw run` flag or a setup change) and **upstream pipeline bugs** (a defect in one pinned
nf-core release). nf-claw wraps pipelines **unmodified**, so upstream bugs are documented here and
reported upstream, never patched into the submodule.

`nfclaw run` flags used below come from the runner; `--nxf-ver`, `--nxf-env` and `--config` are
recorded in `<outdir>/provenance/` so a working invocation is reproducible. Flag names accept either
dashes or underscores — `nfclaw` normalises `--skip-busco` and `--skip_busco` alike (the raw
`nextflow run` needs the pipeline's exact spelling, usually underscores).

**Passing a value that begins with a dash** (e.g. an "extra args" pass-through such as rnaseq's
`--extra_star_align_args`): use the `--param=value` form so the value is not mistaken for another
flag — `--extra_star_align_args='--outFilterMismatchNmax 5'` (or put it in a `--params-file`). The
two-token form `--extra_star_align_args '--outFilterMismatchNmax 5'` is rejected fast with an
`unknown parameter` error rather than run incorrectly, so this is never a silent failure.

When a run fails for any other reason, the error points at the full Nextflow log and back to this
file; match the symptom below and apply the fix.

## Environment

### `nfclaw` aborts with `ModuleNotFoundError: No module named 'runner'`
**Symptom:** the installed `nfclaw` command fails immediately — before doing any work — with
`ModuleNotFoundError: No module named 'runner'` (or `'librarian'`).
**Why:** `nfclaw` is a console script that imports the repo's `runner` package, which relies on the
`pip install -e .` editable install being active in the **same** Python the command runs under. Two
things break that import: **(1) a space in the install path** — Python's `site` module does not
execute an editable install's path hook when the virtualenv/site-packages path contains a space, so
`runner` never lands on `sys.path` (this repo already requires a space-free path for *runs*; the same
applies to the *install*); **(2)** the editable install was done with a **different Python** than the
one `nfclaw`'s shebang points to (e.g. a `--user` install whose site-packages isn't on that
interpreter's path). This happens before any nfclaw code runs, so it can't be caught by the run-time
space check.
**Fix:**
- Use a **space-free path** for both the repo and the virtualenv (on macOS also avoid iCloud paths),
  and run `pip install -e .` inside the virtualenv you actually use.
- Or skip the console script and use the **no-install equivalent from the repo root**:
  `python3 -m runner <cmd>` (maintenance runs the same way: `make <target>`, or
  `python3 -m librarian.<module>` — e.g. `python3 -m librarian.write_skill --all`). It needs no
  install — the repo root is already on `sys.path` — and resolves the pinned pipelines correctly.

### Path contains a space — checked before the run, fails fast
**Symptom:** a tool fails with a split path, e.g. `cannot create /vol/draft 2/...: Permission
denied`, `Got unexpected extra argument(s)`, or a module that builds shell commands breaks.
**Why:** many bioinformatics tools (and Nextflow's work directory) build shell commands without
quoting their paths, so a space splits the argument. This affects **macOS and Linux** alike.
**How nfclaw handles it:** `nfclaw run` checks the **repo path, the Nextflow work directory and
`--outdir`** *before* launching and **fails fast**, naming exactly which path has the space — a
deterministic check, no guessing. Fixes:
- move the repo to a space-free path (recommended);
- or set a space-free work directory: `--nxf-env NXF_WORK=/a/space-free/dir`, and use a space-free
  `--outdir`;
- or, if you know your pipeline tolerates spaces, pass `--allow-spaces` to run anyway.

### IPv6-only host — JVM can't reach GitHub
**Symptom:** `java.net.SocketException: Network is unreachable` while Nextflow downloads
`https://raw.githubusercontent.com/nf-core/configs/master/nfcore_custom.config`.
**Why:** the host has no default IPv4 route; the JVM prefers IPv4 and never tries IPv6.
**Fix:** `--nxf-env NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true`. To skip remote config
fetches entirely (offline): `--nxf-env NXF_OFFLINE=true`.
**On an IPv6-only host you usually need BOTH this *and* the Docker host-network config (next
section), together:** the JVM flag fixes Nextflow's own GitHub download, while host-network fixes
DNS *inside* containers — neither alone is enough.
```bash
nfclaw run <name> --nxf-env NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true \
                  --config host-net.config …
```

### No network at run time — a tool downloads a database
**Symptom:** a step (e.g. BUSCO) hangs then fails trying to fetch a database it needs.
**Fix:** disable that step. Booleans work from the CLI now, e.g. `--skip-busco true` (or put
`{"skip_busco": true}` in a JSON file and pass it as `--params-file params.json`).

### A process requests more memory than the host has — aborts before any work
**Symptom:** a run aborts at scheduling time because a single step requests more RAM than the
machine has, e.g. `Process requirement exceeds available memory -- req: 80 GB; avail: 62.8 GB`.
Seen with `detaxizer` 1.3.0 run with `--classification_bbduk`: its `BBMAP_BBDUK` step carries
nf-core's `process_high` label, which `conf/base.config` sizes at `80.GB * task.attempt` — more
than a typical workstation or small VM has.
**Why:** an nf-core `base.config` sizes each process by a resource *label*
(`process_low/medium/high/high_memory`) tuned for an HPC cluster; one high-memory step can exceed
a small host's physical RAM, and Nextflow refuses to schedule a task it knows can't fit.
**Fix:** put a ceiling on the whole run with `--limit-cpus` / `--limit-memory` / `--limit-time`,
sized to the machine:
```bash
nfclaw run rnaseq --input ss.csv --outdir results -profile docker \
  --limit-cpus 4 --limit-memory 15.GB --limit-time 1.h
```
nfclaw writes these as Nextflow's [`process.resourceLimits`](https://nf-co.re/docs/running/configuration/nextflow-for-your-system#set-max-resources)
and passes the generated config with `-c` — the mechanism nf-core prescribes, and the same one its
own `test` profiles use (which is why `--demo` never hits this and a real run does). The ceiling
applies to **every** process *and every retry*, so one flag covers whatever the pipeline asks for
next; the generated config is kept in `<outdir>/provenance/resource_limits.config`, so
`commands.sh` replays the run under the same ceiling.

Do **not** cap by naming processes (`withName: 'STAR_GENOMEGENERATE' { memory = '15.GB' }`) unless
you mean to re-size that one step: `withName` changes a single process's *initial* request, so you
must name every step that might exceed the host — miss one and the run dies there instead
(`STAR_GENOMEGENERATE`, then `BBMAP_BBSPLIT`, then the next). It also does not cap the retry, which
asks for more. Use `withName` (via `--config`) only to tune one specific step, e.g. giving a tool
*less* than its label implies:
```groovy
// tune-one-step.config
process {
    withName: 'BBMAP_BBDUK' { memory = '12.GB' }
}
```
(Size any cap to the host *and* to what the tool actually needs — too low and the step itself fails
or is OOM-killed.)

### Nextflow too new for an older release
**Symptom:** `Unexpected input: ':'`, `Unexpected token`, `Invalid include source`, or
`import ...` rejected — on Nextflow **26.x**, whose strict parser rejects older Groovy config
syntax (typed declarations, functions with params, `manifest.*`/`validation.*` accessed at parse
time, `import` in `.nf`). Many older releases hit this.
**Fix:** pin an engine the release was written for: `--nxf-ver 25.10.2` (must still satisfy the
pipeline's declared `nextflowVersion` minimum). If you hit it on most pipelines, set it once for the
shell: `export NXF_VER=25.10.2` (nfclaw passes it through). See [`compatibility.md`](compatibility.md).
Confirmed-affected releases that **do** run with `--nxf-ver 25.10.2` include `epitopeprediction`,
`fetchngs`, `hgtseq`, `callingcards`, `coproid`, `denovotranscript` 1.2.1, `chipseq` 2.1.0,
`fastqrepair` 1.0.0, `atacseq` 2.1.2, `circdna` 1.1.0, `sarek` 3.8.1, `genomeassembler` 1.1.0,
`detaxizer` 1.3.0, `scrnaseq` 4.1.0, `cutandrun` 3.2.2 and `marsseq` 1.0.3. Examples of what NF 26
rejects: chipseq's **and** marsseq's `def check_max(obj, type)` in `nextflow.config` (marsseq 1.0.3
declares only `!>=23.04.0`, so unpinned it parses under NF 26 and fails at launch with a
`nextflow.cli.Launcher` error — `--nxf-ver 25.10.2` fixes it; note its `test` profile also sets
`genome = 'mm10'`, which pulls the mm10 reference from AWS iGenomes and needs network); scrnaseq
4.1.0's `Invalid include source: conf/test_multiome.config` (the `test_multiome` profile
`includeConfig`s a file not committed at the tag — NF 26 validates it at parse time even though the
profile is unused, while the legacy parser skips it and the `--demo` run completes); and cutandrun
3.2.2's `Cannot invoke method optional() on null object`, from the deprecated output syntax
`emit: html optional true` in `modules/local/for_patch/trimgalore/main.nf` (sibling modules already
use the current `emit: …, optional: true`).
**Exception — some releases need a _newer_ engine, not an older one:** `funcscan` 4.0.0 and
`lsmquant` 1.0.2 declare `nextflowVersion = '!>=25.10.4'`, so `--nxf-ver 25.10.2` is rejected at the
version gate (the symptom can read as a parameter/validation failure); use `--nxf-ver 25.10.4`.
(`bactmap` 1.0.0 hits the parser issue *and* further bugs and can't run in demo here — see the
upstream table.)

### Docker bridge network has no DNS (IPv6-only host)
**Symptom:** containers can't resolve hostnames; downloads inside a container fail even though the
host has connectivity. Docker's bridge uses the IPv4 DNS `8.8.8.8`, unreachable on an IPv6-only host.
**Fix:** give containers the host network via a config file, passed with `--config`. `docker.runOptions`
is a single string that a `--config` **replaces** (it does not merge with the pipeline's value), so keep
nf-core's default user mapping in the same string — otherwise the container reverts to running as root
and its outputs become root-owned (see the next section):
```groovy
// host-net.config — one runOptions string: host network + nf-core's default user mapping
docker { runOptions = "--network host -u $(id -u):$(id -g)" }
```
`nfclaw run <name> --config host-net.config …`. `--config` is repeatable, but two files that each set
`docker.runOptions` do **not** combine — the last one wins — so put every option you need in one string.
`--config` accepts any Nextflow config (also handy for custom resources, below).

### A container creates root-owned files that block publishing
**Symptom:** a step writes a file/dir owned by root with restrictive permissions, and Nextflow —
running as your user — can't read or publish it. Examples: `CUSTOM_SRATOOLSNCBISETTINGS` and
`macrel` (mode `600`), or STAR in `rnaseq` (`_STARgenome/` / `_STARpass1/` as `drwx------`,
failing with `AccessDeniedException`).
**Why:** nf-core's `docker` profile already maps your host user into the container
(`docker.runOptions = '-u $(id -u):$(id -g)'`), which normally prevents this. The trap is that
`docker.runOptions` is a single string: any `--config` that sets it (for example the host-network file
above) **replaces** the pipeline's value instead of adding to it, so the mapping is dropped and the
container falls back to root — its outputs then land in the work dir owned by root.
**Fix:** keep the user mapping in your `--config`, folded into the same `runOptions` string as any other
option you set. Use nf-core's own mapping — Nextflow writes it into the generated `.command.run`, where
the shell evaluates `$(id -u)`/`$(id -g)` at launch:
```groovy
// run-as-user.config
docker { runOptions = "-u $(id -u):$(id -g)" }
```
If your shell ever trips over the substitution (`syntax error near unexpected token ')'`), hardcode the
numeric ids instead — find them with `id -u` / `id -g` (commonly `1000:1000`):
`docker { runOptions = "-u 1000:1000" }`. `nfclaw run <name> --config run-as-user.config …`. (Or fix
the file's permissions in the work dir and `--resume`.)

### `--resume` resumed the wrong session
**Status: fixed.** `nfclaw run` now launches Nextflow **from the `--outdir`**, so each run owns its
own `.nextflow/` history and cache. `--resume` resumes *this* outdir's session — it can no longer
pick up another pipeline's run. Use a distinct `--outdir` per pipeline.

### `--resume` fails with "Unable to acquire lock on session …"
**Symptom:** after a run was interrupted (killed/timed out), re-running with `--resume` fails to
acquire the session lock.
**Why:** a hard kill leaves Nextflow's session lock behind; Nextflow refuses to resume because it
can't tell the lock is stale rather than held by a live process (it never auto-clears it, by design,
to avoid corrupting a concurrent run).
**Fix:** make sure no Nextflow process for that `--outdir` is still running, then remove the stale
lock under that outdir's state — `rm -f <outdir>/.nextflow/cache/*/LOCK` (or just start fresh in a
new `--outdir`) — and `--resume` again. Because each run owns its `--outdir`'s `.nextflow/`, this only
affects that one run.

### Launching several pipelines in parallel
**Status: fixed.** Starting 2+ pipelines at once whose submodules were uninitialised used to race on
`.git/config` (`could not lock config file`). `nfclaw run` now serialises submodule initialisation
with a per-repo file lock (and re-checks under it), so concurrent first-time runs initialise each
submodule exactly once. No action needed; for many pipelines you can also pre-init up front with
`git submodule update --init`.

### Replaying a run: `provenance/commands.sh` reproduces into a *fresh* directory
**Status: fixed.** The replay script used to re-run into the original `--outdir` and failed on
contact: an nf-core pipeline publishes into `--outdir`, and it cannot re-publish over a previous
run's files. Nextflow refuses to overwrite the reports it is configured to write
(`pipeline_info/execution_trace_*.txt`, and the report/timeline/DAG beside it), and a module that
emits a fixed-name artefact — sarek's BCO `pipeline_info/manifest_*.bco.json` — collides outright.

`commands.sh` now reproduces the run into a **new** directory, defaulting to `<outdir>.replay`:
```bash
./results/provenance/commands.sh                 # → results.replay/
./results/provenance/commands.sh /tmp/check-it   # or name the target yourself
```
It refuses a target that already holds files (rather than half-overwriting one), launches Nextflow
from the target so the engine's `.nextflow/` state never touches the original run, and passes
`--outdir "$target"` — which overrides the value in the recorded params file, so one argument
redirects the whole run. Everything else is byte-for-byte the recorded command, so the reproduction
can be compared against the original bundle's `outputs.sha256`.

A replay re-executes the pipeline: that *is* the reproduction. It is not a `--resume`, and it does
not read the original run's cache unless the recorded command's work directory still exists.

### `--check` never writes into `--outdir`
**Status: fixed.** `--check` validates parameters and prints the command without launching, so it
must leave the output directory exactly as it found it. It used to create `--outdir` and stage
`provenance/params.json` in it, which then made the *next* real run fail preflight with
`--outdir is not empty` — over a directory that held no results at all. The files `--check` stages
now go to a temp directory instead (the printed command still runs as printed, since it names them
by absolute path).

## Warnings a run prints that are not faults

These appear in a **normal run and in its replay alike** — the replay executes the identical
recorded command, so any warning the original printed, it prints too. None of them affects results,
and none originates in nf-claw. They are catalogued here with their real cause so they are not
re-investigated, and not mistaken for a defect in the run.

### `WARN: Unrecognized config option 'validation.defaultIgnoreParams'` / `'validation.monochromeLogs'`
**Nextflow's config linter, not the pipeline and not nf-claw. Harmless.** Both options are set by the
*pipeline's own* `nextflow.config` (e.g. `nf-core/scrnaseq` 4.2.0 lines 361–364) inside the
`validation` scope, which is contributed by the `nf-schema` plugin that same file declares. Nextflow's
strict config parser validates config options against the scopes it knows *before* plugins are
loaded, and nf-schema does not register a `ConfigScope` for `validation` — so the parser reports a
scope it cannot see as unrecognised. The option is read correctly by the plugin at run time and the
pipeline behaves normally. Tracked upstream:
[nextflow-io/nf-schema#117](https://github.com/nextflow-io/nf-schema/issues/117).
Nothing to do; the warning depends on the engine version, not on how the run was launched.

### `WARN: --validationSchemaIgnoreParams: genomes` is not a valid parameter (scrnaseq `--demo`)
**A real bug — but in the pinned release, not in nf-claw.** `nf-core/scrnaseq` 4.2.0 declares
`nf-schema@2.5.1`, yet three of its test profiles (`conf/test.config`, `conf/test_full.config`,
`conf/test_cellranger_multi.config`) still set `validationSchemaIgnoreParams`, an **nf-validation
1.x** parameter that nf-schema 2.x removed (its replacement is the `validation.defaultIgnoreParams`
config option, which the same file already sets — see the
[migration guide](https://nextflow-io.github.io/nf-schema/latest/migration_guide/)). The pipeline's
own `nextflow_schema.json` does not declare it either, so nf-schema reports the parameter as invalid.
The option is **inert**: it does nothing and results are unaffected.

nf-claw wraps releases **unmodified**, so this cannot be fixed here — but `nfclaw run` now *detects*
it from the pinned tree and prints an advisory before launching, so the warning arrives explained:

```
warning: conf/test.config sets `validationSchemaIgnoreParams`, an nf-validation 1.x parameter
removed in nf-schema 2.x ... the option is inert and does not affect results.
```

The check is deliberately narrow: a release that declares **nf-validation 1.x** is using that
parameter *correctly* and is never flagged (nine pinned releases do, including `fetchngs` and
`chipseq`). Only the nf-schema-2.x-with-a-1.x-parameter combination — the actual defect — is
reported. Today `scrnaseq` is the only pipeline in the library that hits it.

### rnaseq `--demo`: `--gtf` with `--gff`, `--transcript_fasta`, and the `first` operator
**The test dataset, not a misconfiguration.** rnaseq's own `conf/test.config` deliberately sets
`gtf`, `gff` *and* `transcript_fasta` together (lines 22–24) so the test profile exercises those code
paths; the pipeline then warns that it will prefer `--gtf` over `--gff`, and Nextflow warns about the
`first` operator on a single-item channel. These come from the profile's parameters, which nf-claw
passes through untouched — the same warnings appear in a plain `nextflow run nf-core/rnaseq -profile
test`. A real run with your own reference does not set both, and does not warn.

## Upstream pipeline bugs (documented, not patched)

These are defects in a specific pinned release. The robust fix lives upstream in nf-core; below
is the nf-claw-side workaround.

| pipeline @ version | symptom | why it happens | workaround |
|---|---|---|---|
| `bamtofastq` (incl. 2.1.2 / 2.2.1) | `SAMTOOLS_FAIDX ([])` fails immediately | the `test` profile sets `genome = null` + `igenomes_ignore = true`, so `prepare_indices` routes an empty dummy channel into `SAMTOOLS_FAIDX` | provide a reference (`--fasta` / `--genome`); no fix in pure `--demo` mode — report upstream |
| `bacass` 2.6.1 (Unicycler) | `SyntaxWarning: invalid escape sequence '\d'` then failure on Python 3.12 | the `unicycler:0.5.1` container ships Python code not updated for 3.12 | choose another assembler: `--assembler megahit` |
| `hgtseq` 1.1.0 | `a column named input1 ... is mandatory!` | the release contradicts itself: its `assets/schema_input.json` (and the schema-valid demo CSV) use `sample,fastq_1[,fastq_2]`, but the custom parser `create_input_channel` in `workflows/hgtseq.nf` instead requires `sample` + `input1` (+ optional `input2`), where `input1`/`input2` hold the fastq/bam paths (the `group` column in its comment is vestigial — unused) | supply a `sample,input1[,input2]` sheet via `--input` — the bundled `assets/samplesheet_fastq.csv` is the correct shape; don't rely on `--demo` |
| `funcscan` 2.1.0 – 4.0.0 (current pin), **DRAMP DB only** | `TypeError` in `ampcombi_download.py` when AMPcombi downloads the **DRAMP** database (`amp_ampcombi_db_id='DRAMP'`, the pipeline-wide default) — **not** hit by `--demo`, whose `test` profile overrides the id to `APD` (verified by source inspection through 4.0.0; funcscan 4.0.0 declares `!>=25.10.4`, so run it with `--nxf-ver 25.10.4` — `25.10.2` is rejected at the version gate) | the DRAMP loop in `bin/ampcombi_download.py` calls `valid_sequence_pattern.match(row['Sequence'])` with no NaN guard; rows with an empty `Sequence` are read as `NaN` (a float), so the regex match raises. The APD code path parses FASTA records (always strings), so it has no such call on a `NaN` | for a production DRAMP run, pre-build the DB with the NaN rows filtered and pass `--amp_ampcombi_db /path/to/amp_DRAMP_database` |
| `bactmap` 1.0.0 | won't run in `--demo` on any Nextflow here | three chained issues: NF 26 strict parser rejects `def check_max(obj, type)`; NF 25 treats `file("https://…", checkIfExists: true)` (bactmap.nf:13) as a local path → `No such file or directory: https://…`; NF 23's CAPSULE bootstrapper can't resolve Maven deps on this host | not runnable in demo — wait for an upstream fix / report; pin a different release with `--pipeline-version` if one works |

When a workaround relies on a different release, confirm the symptom is gone there before relying
on it — `nfclaw show <name> --pipeline-version X.Y.Z` prints that release's docs.

## Pipeline-specific run notes

These are not bugs — just a flag or samplesheet value that a constrained environment or a strict
schema requires:

- **`fetchngs`** — if accessions have no ENA FTP URL, the pipeline falls back to `SRATOOLS_PREFETCH`
  (needs NCBI SRA Cloud). With no such access, run metadata-only: `--skip_fastq_download`. (The
  accession list may be `.csv`, `.tsv` **or `.txt`** at the pinned 1.12.0 — pattern
  `^\S+\.(csv|tsv|txt)$`; a plain `.txt` id list is accepted.)
- **`coproid`** — needs **two** samplesheets: `--input` (the fastq sheet documented in `skill.md`)
  and a separate, required `--genome_sheet`. Each `--genome_sheet` row needs
  `genome_name,taxid,genome_size` plus **exactly one** of `igenome` or `fasta` — these are mutually
  exclusive (`assets/schema_genomes.json` declares `oneOf`), so filling both fails with `Value
  matches against more than one schema`; for a custom reference, leave `igenome` blank and give a
  `fasta` path. `--kraken2_db` is also required and has no default — supply a real Kraken2 database.
  Separately, `SAM2LCA_UPDATEDB` downloads the NCBI taxonomy over FTP/IPv4 at run time; on a
  restricted host pre-build it and pass `--sam2lca_db /path/to/db`.
- **`crisprseq`** — the samplesheet `reference` column is a **raw DNA sequence** (schema pattern
  `^[ACTGNactgn]+$`), not a FASTA path as in most pipelines; put the sequence itself (e.g. `ACTG…`)
  in that column.
- **`circdna`** — two parameters are **required by the schema** for a real `--input` run:
  `--input_format` (`FASTQ` or `BAM`) and `--circle_identifier` (one or more of
  `circle_map_realign`, `circle_map_repeats`, `circle_finder`, `circexplorer2`,
  `ampliconarchitect`, comma-separated). The `--demo`/`test` profile sets both, so a demo run needs
  neither; a manual samplesheet run without them fails parameter validation at launch.
- **`metapep`** — the `--demo`/`test` profile runs `DOWNLOAD_PROTEINS`, which fetches protein
  sequences from **NCBI Entrez** at run time (`download_proteins_entrez.py --email $NCBI_EMAIL`) and
  reads a Nextflow **secret** named `NCBI_EMAIL` (the module declares `secret "NCBI_EMAIL"`). Without
  it the step fails with a `ProcessFailedException` in `DOWNLOAD_PROTEINS`. Set the secret once
  before running and ensure outbound NCBI access: `nextflow secrets set NCBI_EMAIL you@example.com`
  (and `nextflow secrets set NCBI_KEY <key>` for a higher NCBI rate limit). Secrets live in the
  Nextflow store and are inherited by `nfclaw run`.
- **`createtaxdb`** — give each sample a **non-numeric** `id` (e.g. `seq1`, `chr1`). nf-schema
  coerces a purely numeric string (`"1"`) to an integer, which then fails the `id` column's
  `type: string` (pattern `^\S+$`) validation.
- **`genomeassembler`** — set at least one of `--ont true` / `--hifi true` (it aborts at start with
  `At least one of params.ont, params.hifi needs to be true.`), even when you supply short reads.
- **`funcscan`** — run it with `--nxf-ver 25.10.4` (it declares `!>=25.10.4`; `25.10.2` is rejected
  at the version gate). The `--demo`/`test` profile turns on **all three** screenings
  (`run_amp_screening`, `run_arg_screening`, `run_cazyme_screening`), each of which fetches a
  database at run time: AMP/AMPcombi downloads **APD** from `aps.unmc.edu`, ARG/DeepARG downloads its
  model from Zenodo, and CAZyme/dbCAN downloads a **~2.18 GB** database — slow downloads that can
  appear to hang. On a constrained or slow network, pre-supply the AMP DB with
  `--amp_ampcombi_db /path/to/db` (this also sidesteps the DRAMP bug in the table above) and skip the
  heavy steps with `--run_cazyme_screening false` and `--arg_skip_deeparg true`.
- **`sarek` 3.9.0** — upstream usage examples for cache/index-only runs show
  `--build_only_index --input false`, but the pinned release's nf-schema rejects `--input false`
  because `input` is declared as a string path. For cache/index-only runs, omit `--input` instead
  and set the cache/index parameters explicitly (for example `--build_only_index true`,
  `--download_cache true`, and the relevant `--tools` value). Normal analysis runs should still pass
  a real samplesheet with `--input`.
- **`sarek` 3.9.0** — do not use
  `--config pipelines/sarek/upstream/conf/test.config` to turn a normal analysis run into a
  test-data run with a custom samplesheet. Extra config files are loaded after Sarek's profile/config
  initialisation wires iGenomes paths, so the run can still validate default S3 iGenomes paths before
  the test config overrides them. Use the real test profile instead:
  `nfclaw run sarek --input samplesheet_sarek.csv --outdir results -profile test,docker`. For the
  bundled upstream test data, prefer `nfclaw run sarek --demo --outdir results`.
- **`ampliseq`** — the `test` profile caps memory at 6 GB; visualisation/export steps (e.g.
  `QIIME2_EXPORT_RELTAX`) may be OOM-killed (exit 137) without failing the pipeline. In production
  raise it with `--max_memory '<N>.GB'` (or a custom `--config`).
