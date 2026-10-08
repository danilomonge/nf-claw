# Automated Updating & Maintenance

nf-claw maintains synchronization with upstream nf-core pipeline releases through fully automated
workflows and a strict, bidirectional schema drift gate. No context file (`skill.md`, `reference.md`,
or `catalog.*`) is ever edited manually.

---

## 1. Version Policy & Upstream Tracking

Tracking policies are declared in `sources.tsv`:
- Each row contains `name<TAB>url<TAB>version-policy`.
- The primary policy is `latest-release`, directing automation to track the newest official git release tag.
- Submodules pin immutable release tags (e.g. `tags/3.18.0`), never moving branches (`master`, `main`, `dev`).

---

## 2. Automated Daily Updates (`auto-update.yml`)

The `.github/workflows/auto-update.yml` workflow executes daily:

1. **Tag Discovery:** Queries upstream remotes via `git ls-remote --tags` (using standard git protocol to
   bypass GitHub REST API rate limits).
2. **Deterministic Bumping:** When a newer release tag is discovered for a `latest-release` pipeline, the
   workflow checks out that tag in `pipelines/<name>/upstream`.
3. **Context Regeneration:** Invokes `librarian/write_skill.py` and `librarian/write_catalog.py` to regenerate
   all parameter tables, input schemas, tool lists, and catalog manifests.
4. **Comprehensive In-Job Validation:**
   - Runs `scripts/nextflow_accept.sh` (`nextflow -preview`) to verify pipeline compilation, profile resolution,
     and parameter validation.
   - Executes the complete pytest suite.
   - Runs the drift gate (`python3 -m librarian.check_drift`).
5. **Automated Merging:** Only when all validation checks pass with exit code 0 is the PR automatically merged
   into `main`, which dispatches `deploy-pages.yml` to refresh the live site.
6. **Error Resiliency:** If any remote repository cannot be reached, the maintenance scan fails immediately
   rather than silently treating the failure as "no new releases."

---

## 3. Automated Weekly Discovery (`discover-pipelines.yml`)

The `.github/workflows/discover-pipelines.yml` workflow runs weekly to onboard newly created nf-core pipelines:

1. **DSL2 Filtering:** Inspects the nf-core pipeline registry, onboarding only **DSL2** pipelines (legacy DSL1
   workflows are permanently ignored).
2. **Name Sanitization & Security:**
   - Every candidate pipeline name is strictly validated: must consist solely of alphanumeric characters,
     dots, hyphens, and underscores, bounded by alphanumeric characters (`^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$`).
   - Remotes are deterministically constructed as `https://github.com/nf-core/<validated-name>.git`. Mutable
     catalog metadata cannot redirect automation to external repositories.
3. **Scaffolding:** Adds the submodule, pins its newest release tag, and generates initial context files.
4. **Strict Acceptance Gate:** Evaluates each candidate via `scripts/nextflow_accept.sh`.
   - Nextflow must compile, resolve configurations, and validate schema with **strict exit code 0**.
   - Any failure, timeout, or unresolved remote test data staging results in rejection (`staging-unverified`).
   - Rejected pipelines are pruned before committing.
5. **Batch Auto-Merge:** Validated additions that pass tests and drift checks are committed and merged.

---

## 4. The Schema Drift Gate (`librarian/check_drift.py`)

The drift gate guards against divergence between pinned code and documentation:

- **Manifest Equivalence:** Verifies that `sources.tsv`, `.gitmodules`, and filesystem directories in
  `pipelines/` describe the exact same pipeline set and remote URLs.
- **Context Parity:** Recompiles `skill.md`, `reference.md`, `catalog.json`, and `catalog.md` in memory and
  asserts character-for-character equivalence with committed files on disk.
- **Handoff Schema Verification:** Validates that every parameter mapping and column transformation in
  `handoffs/*.json` remains valid against the schemas of both participating pipelines.
- **Agent Guidelines Sync:** `tests/test_agent_docs.py` verifies that `AGENTS.md` and `CLAUDE.md` remain
  100% byte-identical.

If any upstream pipeline is updated without regenerating context, or if a manual edit is introduced,
`make check` fails immediately.

---

## 5. Manual Maintenance Commands

Developers can run maintenance tasks locally:

```bash
make update    # Check remotes, bump submodules to latest tags, and regenerate context
make build     # Regenerate skill.md, reference.md, and catalog.* from current submodules
make check     # Run schema drift gate and complete test suite
make test      # Run full pytest suite
```
