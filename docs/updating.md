# Updating pipelines

Versions track upstream **release tags** (`latest-release` in `sources.tsv`).
`.github/workflows/auto-update.yml` runs daily: it finds the newest release per pipeline with
`git ls-remote --tags` (pure git, no API), checks out that tag, regenerates
`skill.md`/`reference.md`/`catalog.*`, and opens a PR. Every changed pipeline first passes Nextflow
acceptance, then the full unit suite and a final drift gate run **in the job** (a PR opened with
`GITHUB_TOKEN` would not trigger the `drift-check`/`tests` workflows on its own). Only then is the PR
**auto-merged** and `deploy-pages` dispatched, so an incompatible release or stale context cannot
land without review.
Every source is attempted, but any tag lookup, fetch or checkout failure makes the maintenance job
fail after the scan instead of silently treating an unreachable upstream as “no new release.”
Manual: `make update`.

New pipelines are onboarded separately by `discover-pipelines.yml` (weekly): it finds DSL2 nf-core
pipelines not yet tracked, scaffolds each, drops any Nextflow rejects, and — if the unit tests, the
drift gate and the `-preview` acceptance check all pass — auto-merges the batch. See
[`compatibility.md`](compatibility.md) for the version/engine rules.

Both update paths treat pipeline names as path components and git submodule identifiers, so the
librarian validates every name from `sources.tsv` and from remote discovery metadata before using it.
Only letters, numbers, dots, underscores and dashes are accepted, and every name must start and end
with a letter or number. Malformed names are skipped during discovery or rejected while reading the
source list.
Discovery also derives every remote as `https://github.com/nf-core/<validated-name>.git`; mutable
catalog metadata cannot redirect the write-capable automation to an unrelated repository.
The drift gate checks that `sources.tsv`, `.gitmodules`, and the pipeline directories contain the
same names and URLs, so maintenance and runtime code cannot silently use different remotes.
