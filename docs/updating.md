# Updating pipelines

Versions track upstream **release tags** (`latest-release` in `sources.tsv`).
`.github/workflows/auto-update.yml` runs daily: it finds the newest release per pipeline with
`git ls-remote --tags` (pure git, no API), checks out that tag, regenerates
`skill.md`/`reference.md`/`catalog.*`, runs the drift gate, opens a PR and — because the gate
already validated it — **auto-merges** that PR, then dispatches `deploy-pages` to rebuild the site.
The gate runs **in the job** (a PR opened with `GITHUB_TOKEN` would not trigger the
`drift-check`/`tests` workflows on its own), so a broken upstream release cannot land stale context.
Manual: `make update`.

New pipelines are onboarded separately by `discover-pipelines.yml` (weekly): it finds DSL2 nf-core
pipelines not yet tracked, scaffolds each, drops any Nextflow rejects, and — if the unit tests, the
drift gate and the `-preview` acceptance check all pass — auto-merges the batch. See
[`compatibility.md`](compatibility.md) for the version/engine rules.
