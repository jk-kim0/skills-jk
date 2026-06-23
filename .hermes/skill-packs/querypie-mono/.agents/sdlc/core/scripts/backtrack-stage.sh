#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  backtrack-stage.sh <case-id> <target-stage> --reason <text>
    [--question <text>] [--root <dir>] [--run-root <dir>]

Reopen an earlier stage from the current stage and mark downstream stages as stale.

Stages:
  plan design build test review documentation release
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
repo_root="$(cd "${skill_dir}/../../.." && pwd)"
case_root="${repo_root}/.sdlc/cases"
run_root="${repo_root}/.agents/runs/sdlc-stage"
metadata_schema="${skill_dir}/schemas/case-metadata.schema.json"
metadata_validator="${script_dir}/validate-metadata-schema.py"
case_id=""
target_stage=""
reason=""
question=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --reason)
      reason="${2:-}"
      shift 2
      ;;
    --question)
      question="${2:-}"
      shift 2
      ;;
    --root)
      case_root="${2:-}"
      shift 2
      ;;
    --run-root)
      run_root="${2:-}"
      shift 2
      ;;
    -*)
      echo "unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      if [[ -z "$case_id" ]]; then
        case_id="$1"
      elif [[ -z "$target_stage" ]]; then
        target_stage="$1"
      else
        echo "unexpected argument: $1" >&2
        usage >&2
        exit 1
      fi
      shift
      ;;
  esac
done

stages=(plan design build test review documentation release)

stage_index() {
  local stage="$1"
  local i
  for i in "${!stages[@]}"; do
    if [[ "${stages[$i]}" == "$stage" ]]; then
      echo "$i"
      return 0
    fi
  done
  return 1
}

next_stage() {
  case "$1" in
    plan) echo "design" ;;
    design) echo "build" ;;
    build) echo "test" ;;
    test) echo "review" ;;
    review) echo "documentation" ;;
    documentation) echo "release" ;;
    release) echo "done" ;;
  esac
}

if [[ -z "$case_id" || -z "$target_stage" || -z "$reason" ]]; then
  echo "case-id, target-stage, and --reason are required" >&2
  usage >&2
  exit 1
fi

if ! target_index="$(stage_index "$target_stage")"; then
  echo "unknown target stage: $target_stage" >&2
  usage >&2
  exit 1
fi

case_dir="${case_root}/${case_id}"
metadata_file="${case_dir}/metadata.yaml"
readme_file="${case_dir}/README.md"
target_result_file="${case_dir}/${target_stage}/result.md"
timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
timestamp_file="$(date -u +%Y%m%dT%H%M%SZ)"
report_file="${run_root}/${case_id}/backtrack-${timestamp_file}.md"

if [[ ! -s "$metadata_file" ]]; then
  echo "missing metadata.yaml: $metadata_file" >&2
  exit 1
fi

if [[ ! -s "$readme_file" ]]; then
  echo "missing README.md: $readme_file" >&2
  exit 1
fi

if [[ ! -s "$target_result_file" ]]; then
  echo "missing target stage result: $target_result_file" >&2
  exit 1
fi

yaml_value() {
  local file="$1"
  local key="$2"
  awk -F': *' -v key="$key" '$1 == key { gsub(/"/, "", $2); print $2; exit }' "$file"
}

set_yaml_key() {
  local file="$1"
  local key="$2"
  local value="$3"
  local tmp
  tmp="$(mktemp)"

  awk -v key="$key" -v value="$value" '
    BEGIN { done = 0 }
    $0 ~ "^" key ":" {
      print key ": \"" value "\""
      done = 1
      next
    }
    { print }
    END {
      if (done == 0) {
        print key ": \"" value "\""
      }
    }
  ' "$file" > "$tmp"
  mv "$tmp" "$file"
}

set_stage_status() {
  local file="$1"
  local target="$2"
  local status="$3"
  local tmp
  tmp="$(mktemp)"

  awk -v stage="$target" -v status="$status" '
    BEGIN {
      in_statuses = 0
      section_seen = 0
      updated = 0
    }
    /^stage_statuses:/ {
      print
      in_statuses = 1
      section_seen = 1
      next
    }
    in_statuses && /^[^[:space:]]/ {
      if (updated == 0) {
        print "  " stage ": \"" status "\""
        updated = 1
      }
      in_statuses = 0
    }
    in_statuses && $0 ~ "^  " stage ":" {
      print "  " stage ": \"" status "\""
      updated = 1
      next
    }
    { print }
    END {
      if (section_seen == 0) {
        print "stage_statuses:"
        print "  " stage ": \"" status "\""
      } else if (in_statuses == 1 && updated == 0) {
        print "  " stage ": \"" status "\""
      }
    }
  ' "$file" > "$tmp"
  mv "$tmp" "$file"
}

append_checkpoint() {
  local file="$1"
  local section="$2"
  local text="$3"
  local tmp
  tmp="$(mktemp)"

  awk -v section="$section" -v timestamp="$timestamp" -v text="$text" '
    BEGIN {
      heading = "## " section
      item = "- `" timestamp "`: " text
      in_target = 0
      seen = 0
      inserted = 0
    }
    $0 == heading {
      print
      in_target = 1
      seen = 1
      next
    }
    in_target == 1 && /^## / {
      if (inserted == 0) {
        print ""
        print item
        inserted = 1
      }
      in_target = 0
    }
    in_target == 1 && $0 == "- 없음" {
      next
    }
    { print }
    END {
      if (seen == 0) {
        print ""
        print heading
        print ""
        print item
      } else if (in_target == 1 && inserted == 0) {
        print item
      }
    }
  ' "$file" > "$tmp"
  mv "$tmp" "$file"
}

python3 "$metadata_validator" "$metadata_file" "$metadata_schema" --case-id "$case_id" >/dev/null

current_stage="$(yaml_value "$metadata_file" "current_stage")"
if ! current_index="$(stage_index "$current_stage")"; then
  echo "metadata.yaml has unknown current_stage: $current_stage" >&2
  exit 1
fi

if ((target_index >= current_index)); then
  echo "target-stage must be earlier than current_stage (${current_stage})" >&2
  exit 1
fi

set_yaml_key "$metadata_file" "current_stage" "$target_stage"
set_yaml_key "$metadata_file" "current_status" "draft"
set_yaml_key "$metadata_file" "next_stage" "$(next_stage "$target_stage")"
set_stage_status "$metadata_file" "$target_stage" "draft"

for ((i = target_index + 1; i <= current_index; i++)); do
  set_stage_status "$metadata_file" "${stages[$i]}" "blocked"
done

append_checkpoint "$readme_file" "최근 체크포인트" \
  "backtrack ${current_stage} -> ${target_stage}"
append_checkpoint "$readme_file" "최근 체크포인트" "reason: ${reason}"
append_checkpoint "$target_result_file" "체크포인트" \
  "backtrack ${current_stage} -> ${target_stage}"
append_checkpoint "$target_result_file" "체크포인트" "reason: ${reason}"

if [[ -n "$question" ]]; then
  append_checkpoint "$readme_file" "최근 체크포인트" "question: ${question}"
  append_checkpoint "$target_result_file" "체크포인트" "question: ${question}"
fi

python3 "$metadata_validator" "$metadata_file" "$metadata_schema" \
  --case-id "$case_id" --stage "$target_stage" >/dev/null

mkdir -p "$(dirname "$report_file")"

{
  echo "# Stage Backtrack"
  echo
  echo "- Case ID: \`${case_id}\`"
  echo "- From stage: \`${current_stage}\`"
  echo "- Target stage: \`${target_stage}\`"
  echo "- Reason: ${reason}"
  if [[ -n "$question" ]]; then
    echo "- Question: ${question}"
  fi
  echo "- Created at: \`${timestamp}\`"
  echo
  echo "## Status Updates"
  echo
  echo "- Current stage: \`${target_stage}\`"
  echo "- Current status: \`draft\`"
  echo "- Next stage: \`$(next_stage "$target_stage")\`"
  echo "- Downstream stages through \`${current_stage}\` are marked \`blocked\`."
  echo
  echo "## Next Action"
  echo
  echo "- Run \`prepare-stage.sh ${case_id} ${target_stage}\`."
  echo "- Close the backtrack question in \`${target_stage}/result.md\`."
  echo "- Re-check downstream artifacts before continuing."
} > "$report_file"

cat "$report_file"
