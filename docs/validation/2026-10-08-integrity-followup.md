# Integrity audit follow-up

Date: 2026-10-08. Baseline: `e689896` (main). Environment: macOS arm64,
Python 3.13.13, Nextflow 25.10.4. This audit distinguishes fresh observations from
the historical Linux/cloud evidence in [the earlier audit](2026-10-08-audit.md).

## Reproduced defects and fixes

- Relative invocation of `commands.sh` failed after changing into the replay target.
  Moving a bundle also left its params and generated configs pointing at the old
  directory. Resolve the script directory before changing directories, rebase only
  bundle-owned config arguments, and compare relocated files against their original
  checksum identities. External datasets, pipeline trees and user configs retain
  their recorded paths and hashes.
- Replay bypassed the runner's writer lock. A standalone Python bootstrap now
  acquires the same sibling POSIX flock and keeps it through exec of the replay
  shell. Tests check refusal before target creation, lock retention during execution,
  signal shutdown, and subsequent lock release.
- JSON and YAML duplicate keys silently selected the last scientific parameter value.
  Reject duplicate keys at every nesting level while preserving valid YAML merge
  overrides. Reject cyclic aliases with a validation error; retain SafeLoader's
  refusal to instantiate Python objects.
- Directory-valued references bypassed handoff dependency verification. Compare the
  complete directory inventory and content with historical upstream input/output
  checksums, record every dependency, and recheck inventory during chain status and
  resume. Empty or unrecorded reference inventories cannot establish historical
  identity and are refused.
- Chain parsing treated `"demo": "false"` as true and discarded falsey values of
  the wrong shape in params, retries, config and resource limits. Validate boolean,
  integer, map and list types before applying defaults. The string `"false"` can no
  longer activate the bundled test profile or bypass space checks.
- Recursive glob enumeration could hide unreadable output directories on Python 3.13,
  and dangling result links disappeared from checksums. Use one explicit, error-propagating
  result walker for reporting and verification. Follow published directory symlinks,
  preserve their published paths, reject cycles and dangling links, and exclude the
  provenance/Nextflow state trees before scanning them.
- Input snapshots globally deduplicated directory symlink targets, so adding an alias
  could leave the checksum inventory unchanged despite adding logical sample paths.
  Preserve every alias path, detect cycles per traversal branch, and refuse cyclic
  directory inputs before launching.
- Handoff row patterns repeating a placeholder (for example,
  `fastq/{sample}/{sample}_1.fastq.gz`) raised a raw regex compilation error despite
  passing rule validation. Repeated placeholders now require the same captured value,
  preserving sample identity across directory and filename positions.
- The Nextflow acceptance script overwrote a fixed config in the shared temporary
  directory and removed an existing `prev-<pipeline>` directory. Use private scratch
  space with cleanup. Also reject failed/partial pipeline inventories and support
  macOS bash 3.2 without `mapfile`.

Every defect above was reproduced by a failing regression before its implementation
fix. Existing tests exposed an internal-directory handoff regression during development;
the final comparison excludes run metadata consistently with the output manifest.

## Fresh validation

- Baseline: 831 passed, 29 skipped. Skips were chiefly absent submodules, plus Linux-only
  process tests and the old bash-version restriction; they were not counted as passes.
- A real deterministic local Nextflow fixture computes an input digest with `shasum`.
  Its result matches Python's independently computed SHA-256 oracle. Its relocated
  replay is byte-identical; changing the original input prevents execution. This is
  now a committed integration test, also exercised by a dedicated GitHub Actions job.
  A real two-stage chain also matches an independently computed compound digest,
  verifies its handoff, and detects mutation of the upstream output.
- Website: TypeScript check and Next.js production export passed; 109 pages generated.
  `npm audit --package-lock-only` reported zero known vulnerabilities.
- Python dependency audit: zero known vulnerabilities after upgrading pip in the
  disposable validation environment. nfclaw has no mandatory third-party runtime
  dependencies. Wheel and source distribution builds succeeded.
- Ruff and bash syntax checks passed. Bandit's subprocess/PATH warnings concern the
  intentional local Git/Nextflow execution interface. Its URL-opening warning refers
  to the developer-controlled discovery catalog URL (HTTPS by default); it is not
  evidence that untrusted pipeline metadata controls that URL. The YAML loader uses
  a SafeLoader subclass and is tested against executable Python object tags.

- All 91 pinned submodules initialized without changing their gitlinks. The complete
  generated-document/catalog/handoff drift check passed. All 91 demo commands passed
  real wrapper preflight with Docker running (`check_only=True`); these checks did not
  execute analysis tasks or validate their Nextflow configs at runtime.
- Full local suite at `9e65baa`: 904 passed, 2 skipped (Linux `/proc` and
  `PR_SET_PDEATHSIG` tests). At `60539d8`, the full local suite passed 905 tests
  with the same two skips; all six GitHub software-validation jobs also passed.
  Statement coverage at `9e65baa`: 90.37%;
  branch coverage: 85.71%; combined coverage: 89.07%. Coverage is a measurement of
  exercised code, not a correctness guarantee; subprocess execution of the copied
  replay guard is checked by behavior but is not counted in parent-process coverage.

The PR adds Linux/macOS tests on Python 3.11 and 3.13, a real Nextflow integration job,
and a website dependency audit/typecheck/build job before merge. The complete engine
acceptance workflow partitions the independent pipeline checks into eight bounded
jobs; a regression verifies that all 91 pipelines are selected exactly once and a
failed inventory cannot produce a green check.
The tests workflow previously ran on both every push and every pull-request update,
launching the same six jobs twice for each PR commit (observed at `60539d8`). It now
runs once per PR update, on main pushes, and on manual dispatch. The full matrix,
website and real-engine jobs are retained. Workflow YAML parsing and all seven
workflow guards passed after this trigger change.
The Linux/macOS matrix, integration job, website job and drift check passed on
`9e65baa` in [PR 119](https://github.com/danilomonge/nf-claw/pull/119).

## Acceptance failures under investigation

The fresh [eight-shard acceptance run](https://github.com/danilomonge/nf-claw/actions/runs/37814228020)
at `aede646` has failed; it is not a passing release gate. Completed failures include:

- `bactmap` 1.0.0, Nextflow 24.10.5: missing bundled reference URL. Independent
  HTTP inspection returned 404, and the test-datasets branch contains no genome
  directory. The older known-issues explanation that the URL became a local path
  was unsupported and has been corrected.
- `marsseq` 1.0.3, Nextflow 23.04.0: required local references absent in a fresh
  output directory. A separate reference-building preview using the schema's
  `build_references=true` parameter passed on Nextflow 25.10.4. It exercises the
  reference-building DAG only; it does not validate the failed analysis DAG.
- `createpanelrefs` 1.0.0 (Nextflow 26.04.0), `proteinfamilies` 2.6.0
  (Nextflow 26.04.0), and `multiplesequencealign` 1.1.1 (Nextflow 25.04.2):
  previews did not finish within 900 seconds (exit 124). Their consoles do not
  establish the underlying causes.

All eight shards completed: three jobs passed and five failed. The workflow now retains
console logs, individual engine logs and a verdict table after scratch cleanup,
including failures and timeouts, to make subsequent diagnosis possible. No failure
is converted to acceptance, and no placeholder input is substituted to satisfy a
path check. All upstream gitlinks and source trees remain unchanged.

A real Docker `demo` run on macOS arm64 completed after a timeout and resume,
publishing 45 files and a MultiQC HTML report. It does not establish complete
component success: MultiQC's Chromium image-export subprocesses failed under QEMU
(0/36 exports completed), while MultiQC itself returned zero. The initial failed
attempt and the successful resumed attempt remain in the run log. A fresh run
completed with 40 files and reproduced the same plot-export failure. The five
additional files in the resumed run are metadata from its earlier attempt. Its
fresh replay is being checked separately; neither run establishes successful
static plot export.

Source inspection also disproved the known-issues claim that replay always produces
the same filenames: demo's `dumpParametersToJSON()` independently timestamps its
parameter report, outside the pinned `trace_report_suffix`. The verifier retains
such files and reports their missing/extra paths. The guide now explains this
limitation and distinguishes inventory equality from analytical agreement.

## Scientific limits

Passing software tests, schema checks and previews does not prove biological accuracy.
The fixture above tests execution, provenance and replay with known output; it is not
a biological benchmark. This session has not rerun the earlier cloud experiments or
independently benchmarked every nf-core algorithm, reference and parameter combination.

Local checksum verification establishes identity at observation time. It does not
prevent data mutation while an external task is reading it. Remote inputs, container
digests, indirect config includes and references supplied only by Nextflow profiles
are not comprehensively frozen. Published symlink outputs remain dependent on their
targets being readable. Checksums are integrity evidence, not authenticated signatures
against an adversary who can rewrite the entire provenance bundle.

No finite test suite establishes the absence of all bugs or vulnerabilities, nor does
an identical output establish the biological accuracy of an algorithm. The repository's
known upstream/environmental limitations remain documented in `docs/known-issues.md`.
