# Known issues & troubleshooting

Most run-time failures fall into two buckets: **environment** (your host or path — fixable with
an `nfclaw run` flag or a setup change) and **upstream pipeline bugs** (a defect in one pinned
nf-core release). nf-claw wraps pipelines **unmodified**, so upstream bugs are documented here and
reported upstream, never patched into the submodule.

`nfclaw run` flags used below come from the runner; `--nxf-ver`, `--nxf-env` and `--config` are
recorded in `<outdir>/provenance/` so a working invocation is reproducible. Flag names accept either
dashes or underscores — `nfclaw` normalises `--skip-busco` and `--skip_busco` alike (the raw
`nextflow run` needs the pipeline's exact spelling, usually underscores).

When a run fails for any other reason, the error points at the full Nextflow log and back to this
file; match the symptom below and apply the fix.

## Environment

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
**Fix:** disable that step. Booleans work from the CLI now, e.g. `--skip-busco true` (or a
`--params-file '{"skip_busco": true}'`).

### Nextflow too new for an older release
**Symptom:** `Unexpected input: ':'`, `Unexpected token`, `Invalid include source`, or
`import ...` rejected — on Nextflow **26.x**, whose strict parser rejects older Groovy config
syntax (typed declarations, functions with params, `manifest.*`/`validation.*` accessed at parse
time, `import` in `.nf`). Many older releases hit this.
**Fix:** pin an engine the release was written for: `--nxf-ver 25.10.2` (must still satisfy the
pipeline's declared `nextflowVersion` minimum). If you hit it on most pipelines, set it once for the
shell: `export NXF_VER=25.10.2` (nfclaw passes it through). See [`compatibility.md`](compatibility.md).
Confirmed-affected releases that **do** run with `--nxf-ver 25.10.2` include `epitopeprediction`,
`fetchngs`, `hgtseq`, `callingcards`, `funcscan`, `coproid`, `denovotranscript` 1.2.1,
`chipseq` 2.1.0 and `fastqrepair` 1.0.0 (e.g. chipseq's `def check_max(obj, type)` in
`nextflow.config`). (`bactmap` 1.0.0 hits this *and* further bugs and can't run in demo here — see
the upstream table.)

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
| `scrnaseq` 4.1.0 | `Invalid include source: conf/test_multiome.config` | the `test_multiome` profile references a config file that was not committed at the tag; Nextflow 26 validates every `includeConfig` at parse time, even for unused profiles | report upstream; try another release via `--pipeline-version`; or use an engine whose parser does not pre-validate unused profiles |
| `bamtofastq` (incl. 2.1.2 / 2.2.1) | `SAMTOOLS_FAIDX ([])` fails immediately | the `test` profile sets `genome = null` + `igenomes_ignore = true`, so `prepare_indices` routes an empty dummy channel into `SAMTOOLS_FAIDX` | provide a reference (`--fasta` / `--genome`); no fix in pure `--demo` mode — report upstream |
| `bacass` 2.6.1 (Unicycler) | `SyntaxWarning: invalid escape sequence '\d'` then failure on Python 3.12 | the `unicycler:0.5.1` container ships Python code not updated for 3.12 | choose another assembler: `--assembler megahit` |
| `hgtseq` 1.1.0 | `a column named input1 ... is mandatory!` | the `test` profile's CSV uses the old header `sample,fastq_1,fastq_2`, but the release's schema expects `sample_group,input1,input2` | provide a matching samplesheet via `--input` (don't rely on `--demo`) |
| `funcscan` (incl. 2.1.0, 3.0.0) | `TypeError` in `ampcombi_download.py` building the DRAMP DB (persists across releases; NF 26 also needs `--nxf-ver 25.10.2`) | rows with an empty `Sequence` become `NaN`; the script applies a regex to a float | pre-build the DB with the NaN rows filtered and pass `--amp_ampcombi_db /path/to/amp_DRAMP_database` |
| `bactmap` 1.0.0 | won't run in `--demo` on any Nextflow here | three chained issues: NF 26 strict parser rejects `def check_max(obj, type)`; NF 25 treats `file("https://…", checkIfExists: true)` (bactmap.nf:13) as a local path → `No such file or directory: https://…`; NF 23's CAPSULE bootstrapper can't resolve Maven deps on this host | not runnable in demo — wait for an upstream fix / report; pin a different release with `--pipeline-version` if one works |

When a workaround relies on a different release, confirm the symptom is gone there before relying
on it — `nfclaw show <name> --pipeline-version X.Y.Z` prints that release's docs.

## Pipeline-specific run notes

These are not bugs — just the right flag for a constrained environment:

- **`fetchngs`** — if accessions have no ENA FTP URL, the pipeline falls back to `SRATOOLS_PREFETCH`
  (needs NCBI SRA Cloud). With no such access, run metadata-only: `--skip_fastq_download`.
- **`coproid`** — `SAM2LCA_UPDATEDB` downloads the NCBI taxonomy over FTP/IPv4 at run time. On a
  restricted host, pre-build the database and pass `--sam2lca_db /path/to/db`.
- **`ampliseq`** — the `test` profile caps memory at 6 GB; visualisation/export steps (e.g.
  `QIIME2_EXPORT_RELTAX`) may be OOM-killed (exit 137) without failing the pipeline. In production
  raise it with `--max_memory '<N>.GB'` (or a custom `--config`).
