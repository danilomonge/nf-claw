# Updating pipelines

Versions track upstream **release tags** (`latest-release` in `sources.tsv`).
`.github/workflows/auto-update.yml` runs daily: it finds the newest release per pipeline with
`git ls-remote --tags` (pure git, no API), checks out that tag, regenerates
`skill.md`/`reference.md`/`catalog.*`, and opens a PR. The PR is gated by `tests` and `drift-check`,
so a broken upstream release cannot land stale context. Manual: `make update`.
