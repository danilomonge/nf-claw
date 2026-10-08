#!/usr/bin/env bash
# Verify that Nextflow ACCEPTS each pipeline without running the analysis.
#
# Usage: scripts/nextflow_accept.sh [pipeline ...]   (no args = every pipeline)
#
# For each pipeline this initialises the pinned submodule and runs
# `nextflow run <upstream> -profile test,docker -preview` with the Nextflow
# version the release declares (a release declaring an engine older than 22.10.0
# is checked on 24.10.5, a -preview-capable lenient-parser version). "Accepted" means Nextflow compiled the
# pipeline, resolved its config/profile and validated its parameters, and the
# preview exited successfully. Every nonzero exit fails this gate. A clearly
# identified remote-input staging failure is labelled "staging-unverified":
# it could not finish the preview, so it is never accepted for auto-merge.
#
# Env:
#   NFCLAW_RESULT_FILE      if set, write "<name>\t(accepted|staging-unverified|rejected)" per line
#   NFCLAW_KEEP_SUBMODULES  if "1", do not deinit submodules after checking
#
# Exits non-zero unless every pipeline completed its preview successfully.
set -uo pipefail

_run_with_timeout() {
  seconds="$1"
  shift
  if command -v timeout >/dev/null 2>&1; then
    timeout "$seconds" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$seconds" "$@"
  else
    "$@"
  fi
}

names=("$@")
if [ "${#names[@]}" -eq 0 ]; then
  mapfile -t names < <(nfclaw list | cut -f1)
  # An empty list would "accept" nothing and exit 0 — a vacuous green check.
  if [ "${#names[@]}" -eq 0 ]; then
    echo "::error::no pipelines found (nfclaw list returned nothing)"
    exit 1
  fi
fi

tmp="${RUNNER_TEMP:-/tmp}"
summary="${GITHUB_STEP_SUMMARY:-/dev/null}"
result="${NFCLAW_RESULT_FILE:-/dev/null}"
: > "$result"

cfg="$tmp/no-reports.config"
# -preview builds the DAG but produces no trace; disable the report/timeline/
# trace/dag outputs nf-core configs enable (rendering them with no data fails).
printf 'report.enabled=false\ntimeline.enabled=false\ntrace.enabled=false\ndag.enabled=false\n' > "$cfg"

{
  echo "## Nextflow acceptance ( -preview )"
  echo "| pipeline | nextflow | accepted |"
  echo "|---|---|---|"
} >> "$summary"

fail=0
for name in "${names[@]}"; do
  if [[ ! "$name" =~ ^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$ ]]; then
    echo "::error::Invalid pipeline name: $name"
    printf '%s\trejected\n' "$name" >> "$result"
    fail=1
    continue
  fi
  up="pipelines/$name/upstream"
  out="$tmp/prev-$name"
  work="$tmp/work-$name"
  if ! git submodule update --init --depth 1 "$up" >"$tmp/$name-submodule.out" 2>&1; then
    cat "$tmp/$name-submodule.out"
    echo "::error::Could not initialize $name submodule"
    echo "| \`$name\` | n/a | ❌ |" >> "$summary"
    printf '%s\trejected\n' "$name" >> "$result"
    fail=1
    continue
  fi
  ver=$(grep -hoE "nextflowVersion[[:space:]]*=[[:space:]]*'[^']+'" "$up/nextflow.config" 2>/dev/null \
        | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
  ver="${ver:-25.10.4}"
  if [ "$(printf '%s\n22.10.0\n' "$ver" | sort -V | head -1)" = "$ver" ] && [ "$ver" != "22.10.0" ]; then
    ver="24.10.5"
  fi
  echo "::group::$name (nextflow $ver)"
  log="$tmp/$name.out"
  NXF_VER="$ver" _run_with_timeout 900 nextflow run "$up" -profile test,docker \
    -c "$cfg" --outdir "$out" -work-dir "$work" -preview > "$log" 2>&1 && rc=0 || rc=$?
  if [ "$rc" = 0 ]; then
    tail -6 "$log"
    echo "| \`$name\` | $ver | ✅ |" >> "$summary"
    printf '%s\taccepted\n' "$name" >> "$result"
  elif [ "$rc" = 1 ] && grep -qiE '^ERROR[[:space:]]*~[[:space:]]*(No such file or directory|Cannot access remote file|Unable to access (remote )?file):?[[:space:]]+(https?://|s3://|gs://)' "$log"; then
    cat "$log"
    echo "::warning::$name staging-unverified: remote test inputs prevented a completed preview (exit $rc)"
    echo "| \`$name\` | $ver | ⚠️ staging-unverified |" >> "$summary"
    printf '%s\tstaging-unverified\n' "$name" >> "$result"
    fail=1
  else
    cat "$log"
    echo "::error::Nextflow did not accept $name (exit $rc)"
    echo "| \`$name\` | $ver | ❌ |" >> "$summary"
    printf '%s\trejected\n' "$name" >> "$result"
    fail=1
  fi
  echo "::endgroup::"
  if [ "${NFCLAW_KEEP_SUBMODULES:-}" != "1" ]; then
    git submodule deinit -f "$up" >/dev/null 2>&1 || true
  fi
  rm -rf "$work" "$out"
done

{
  echo ""
  echo "Only exit-zero previews are accepted. Staging-unverified previews fail the gate and cannot be auto-merged."
} >> "$summary"
exit $fail
