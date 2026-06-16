# Updating pipelines

Versions track upstream **release tags** (`latest-release` in `sources.tsv`).
`.github/workflows/auto-update.yml` runs daily: it finds the newest release per pipeline with
`git ls-remote --tags` (pure git, no API), checks out that tag, regenerates
`skill.md`/`reference.md`/`catalog.*`, runs the drift gate, and only then opens a PR. The gate runs
**in the job** (a PR opened with `GITHUB_TOKEN` would not trigger the `drift-check`/`tests` workflows
on its own), so a broken upstream release cannot land stale context. Manual: `make update`.
