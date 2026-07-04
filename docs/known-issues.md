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
**Fix:** cap the offending process with a `--config` file (repeatable). Target it by name so the
rest of the run keeps its normal resources:
```groovy
// cap-mem.config
process {
    withName: 'BBMAP_BBDUK' { memory = '12.GB' }
}
```
`nfclaw run detaxizer --classification_bbduk … --config cap-mem.config`. To put a ceiling on
*every* process at once, use Nextflow's native limit instead:
`process { resourceLimits = [ memory: '12.GB', cpus: 4 ] }`. (Size the cap to your host and to what
the tool actually needs — too low and the step itself fails or is OOM-killed.)

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
**Fix:** give containers the host network via a config file, passed with `--config`:
```groovy
// host-net.config
docker { runOptions = "--network host" }
```
`nfclaw run <name> --config host-net.config …`. `--config` is repeatable and accepts any Nextflow
config (also handy for custom resources, below).

### A container creates root-owned files that block publishing
**Symptom:** a step writes a file/dir owned by root with restrictive permissions, and Nextflow —
running as your user — can't read or publish it. Examples: `CUSTOM_SRATOOLSNCBISETTINGS` and
`macrel` (mode `600`), or STAR in `rnaseq` (`_STARgenome/` / `_STARpass1/` as `drwx------`,
failing with `AccessDeniedException`).
**Why:** Docker runs containers as root by default; outputs land in the work dir owned by root.
**Fix:** run the container as your user via a `--config` file. **Use literal numeric ids —
`$(id -u)` does _not_ work here:** Nextflow passes `runOptions` verbatim into the generated
`.command.run`, where `$(...)` is never shell-evaluated and breaks with
`syntax error near unexpected token ')'`. Find your ids with `id -u` / `id -g` (commonly
`1000:1000`) and hardcode them:
```groovy
// run-as-user.config
docker { runOptions = "-u 1000:1000" }
```
`nfclaw run <name> --config run-as-user.config …`. (Or fix the file's permissions in the work dir
and `-resume`.)

### `-resume` resumed the wrong session
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
- **`ampliseq`** — the `test` profile caps memory at 6 GB; visualisation/export steps (e.g.
  `QIIME2_EXPORT_RELTAX`) may be OOM-killed (exit 137) without failing the pipeline. In production
  raise it with `--max_memory '<N>.GB'` (or a custom `--config`).
