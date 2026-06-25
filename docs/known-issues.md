# Known issues & troubleshooting

Most run-time failures fall into two buckets: **environment** (your host or path — fixable with
an `nfclaw run` flag or a setup change) and **upstream pipeline bugs** (a defect in one pinned
nf-core release). nf-claw wraps pipelines **unmodified**, so upstream bugs are documented here and
reported upstream, never patched into the submodule.

`nfclaw run` flags used below come from the runner; both `--nxf-ver` and `--nxf-env` are recorded
in `<outdir>/provenance/` so a working invocation is reproducible.

## Environment

### Path contains a space
**Symptom:** a tool fails with a split path, e.g. `cannot create /vol/draft 2/...: Permission
denied`, `Got unexpected extra argument(s)`, or a module that builds shell commands breaks.
**Why:** many bioinformatics tools (and Nextflow's work directory) build shell commands without
quoting their paths, so a space splits the argument. This affects **macOS and Linux** alike.
**Fix:** use a space-free path for the repo. If you must keep a spaced path, at least move the
work directory off it: `--nxf-env NXF_WORK=/a/space-free/dir` (keep `--outdir` wherever you need
the results). `nfclaw run` prints a non-blocking advisory when it detects a space.

### IPv6-only host — JVM can't reach GitHub
**Symptom:** `java.net.SocketException: Network is unreachable` while Nextflow downloads
`https://raw.githubusercontent.com/nf-core/configs/master/nfcore_custom.config`.
**Why:** the host has no default IPv4 route; the JVM prefers IPv4 and never tries IPv6.
**Fix:** `--nxf-env NXF_JVM_ARGS=-Djava.net.preferIPv6Addresses=true`. To skip remote config
fetches entirely (offline): `--nxf-env NXF_OFFLINE=true`.

### No network at run time — a tool downloads a database
**Symptom:** a step (e.g. BUSCO) hangs then fails trying to fetch a database it needs.
**Fix:** disable that step. Booleans work from the CLI now, e.g. `--skip-busco true` (or a
`--params-file '{"skip_busco": true}'`).

### Nextflow too new for an older release
**Symptom:** `Unexpected input: ':'` / config-parser errors on Nextflow **26.x** (its strict
parser rejects config syntax an older release used).
**Fix:** pin an engine the release was written for: `--nxf-ver 25.10.2` (must still satisfy the
pipeline's declared `nextflowVersion` minimum). See [`compatibility.md`](compatibility.md).

## Upstream pipeline bugs (documented, not patched)

These are defects in a specific pinned release. The robust fix lives upstream in nf-core; below
is the nf-claw-side workaround.

| pipeline @ version | symptom | why it happens | workaround |
|---|---|---|---|
| `scrnaseq` 4.1.0 | `Invalid include source: conf/test_multiome.config` | the `test_multiome` profile references a config file that was not committed at the tag; Nextflow 26 validates every `includeConfig` at parse time, even for unused profiles | report upstream; try another release via `--pipeline-version`; or use an engine whose parser does not pre-validate unused profiles |
| `bamtofastq` 2.2.1 | `SAMTOOLS_FAIDX ([])` fails immediately | with no `--fasta`/`--genome`, the `prepare_indices` subworkflow routes an empty dummy channel into `SAMTOOLS_FAIDX` | provide a reference (`--fasta` / `--genome`); or report upstream |
| `bacass` 2.6.1 (Unicycler) | `SyntaxWarning: invalid escape sequence '\d'` then failure on Python 3.12 | the `unicycler:0.5.1` container ships Python code not updated for 3.12 | choose another assembler: `--assembler megahit` |

When a workaround relies on a different release, confirm the symptom is gone there before relying
on it — `nfclaw show <name> --pipeline-version X.Y.Z` prints that release's docs.
