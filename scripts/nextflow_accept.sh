#!/usr/bin/env bash
# Verify that Nextflow ACCEPTS each pipeline without running the analysis.
#
# Usage: scripts/nextflow_accept.sh [pipeline ...]   (no args = every pipeline)
#
# For each pipeline this initialises the pinned submodule and runs
# `nextflow run <upstream> -profile test,docker -preview` with the Nextflow
# version the release declares (floored to a -preview-capable lenient-parser
# version for releases older than 22.06). "Accepted" means Nextflow compiled the
# pipeline, resolved its config/profile and validated its parameters; a real
# REJECTION is a parse / version / parameter / DSL error. A pipeline that gets
# past those but whose -preview cannot stage remote test inputs (analysis-time
# I/O, out of scope) is still accepted.
#
# Env:
#   NFCLAW_RESULT_FILE      if set, write "<name>\t(accepted|rejected)" per line
#   NFCLAW_KEEP_SUBMODULES  if "1", do not deinit submodules after checking
#
# Exits non-zero if any pipeline is rejected.
set -uo pipefail

names=("$@")
if [ "${#names[@]}" -eq 0 ]; then
  mapfile -t names < <(nfclaw list | cut -f1)
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
  up="pipelines/$name/upstream"
  out="$tmp/prev-$name"
  work="$tmp/work-$name"
  git submodule update --init --depth 1 "$up" >/dev/null 2>&1 || true
  ver=$(grep -hoE "nextflowVersion[[:space:]]*=[[:space:]]*'[^']+'" "$up/nextflow.config" 2>/dev/null \
        | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
  ver="${ver:-25.10.4}"
  if [ "$(printf '%s\n22.10.0\n' "$ver" | sort -V | head -1)" = "$ver" ] && [ "$ver" != "22.10.0" ]; then
    ver="24.10.5"
  fi
  echo "::group::$name (nextflow $ver)"
  log="$tmp/$name.out"
  NXF_VER="$ver" timeout 900 nextflow run "$up" -profile test,docker \
    -c "$cfg" --outdir "$out" -work-dir "$work" -preview > "$log" 2>&1 && rc=0 || rc=$?
  if [ "$rc" = 0 ]; then
    tail -6 "$log"
    echo "| \`$name\` | $ver | ✅ |" >> "$summary"
    printf '%s\taccepted\n' "$name" >> "$result"
  elif grep -qiE "Config parsing failed|Unexpected input|Invalid include source|does not match workflow required version|Unknown option: -preview|Validation of pipeline parameters failed|DSL ?1|Script compilation error|Unable to parse|MissingMethod" "$log"; then
    cat "$log"
    echo "::error::Nextflow rejected $name (compile/config/version/parameters)"
    echo "| \`$name\` | $ver | ❌ |" >> "$summary"
    printf '%s\trejected\n' "$name" >> "$result"
    fail=1
  elif grep -qiE "\* ?PREVIEW ?\*|Only displaying parameters that differ|Core Nextflow options|If you use nf-core" "$log"; then
    tail -6 "$log"
    echo "::warning::$name accepted (compiled + parameters validated); -preview could not stage test inputs"
    echo "| \`$name\` | $ver | ✅ ¹ |" >> "$summary"
    printf '%s\taccepted\n' "$name" >> "$result"
  else
    cat "$log"
    echo "::error::Nextflow did not accept $name"
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
  echo "¹ compiled + parameters validated; \`-preview\` could not stage remote test inputs (analysis-time I/O, out of scope)."
} >> "$summary"
exit $fail
