#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: checkpoint-stage.sh <case-id> <stage> [--note <text>] [--decision <text>] [--status <status>] [--root <dir>]

Record important progress in the current stage result document. If --status is provided,
metadata.yaml is updated as the only lifecycle status source.
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
repo_root="$(cd "${skill_dir}/../../.." && pwd)"
case_root="${repo_root}/.sdlc/cases"
case_id=""
stage=""
note=""
decision=""
status=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --note)
      note="${2:-}"
      shift 2
      ;;
    --decision)
      decision="${2:-}"
      shift 2
      ;;
    --status)
      status="${2:-}"
      shift 2
      ;;
    --root)
      case_root="${2:-}"
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
      elif [[ -z "$stage" ]]; then
        stage="$1"
      else
        echo "unexpected argument: $1" >&2
        usage >&2
        exit 1
      fi
      shift
      ;;
  esac
done

case "$stage" in
  plan|design|build|test|review|documentation|release) ;;
  *)
    echo "unknown stage: $stage" >&2
    usage >&2
    exit 1
    ;;
esac

if [[ -z "$case_id" || -z "$stage" ]]; then
  echo "case-id and stage are required" >&2
  usage >&2
  exit 1
fi

if [[ -z "$note" && -z "$decision" && -z "$status" ]]; then
  echo "at least one of --note, --decision, or --status is required" >&2
  usage >&2
  exit 1
fi

case_dir="${case_root}/${case_id}"
result_file="${case_dir}/${stage}/result.md"
metadata_file="${case_dir}/metadata.yaml"
readme_file="${case_dir}/README.md"
timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [[ ! -s "$result_file" ]]; then
  echo "missing stage result: $result_file" >&2
  exit 1
fi

append_section_item() {
  local file="$1"
  local section="$2"
  local text="$3"

  if ! rg -q "^## ${section}$" "$file"; then
    printf '\n## %s\n\n' "$section" >> "$file"
  fi
  printf -- '- `%s`: %s\n' "$timestamp" "$text" >> "$file"
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
  local target_stage="$2"
  local target_status="$3"
  local tmp
  tmp="$(mktemp)"

  awk -v stage="$target_stage" -v status="$target_status" '
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

if [[ -n "$note" ]]; then
  append_section_item "$result_file" "체크포인트" "$note"
  append_section_item "$readme_file" "최근 체크포인트" "${stage}: ${note}"
fi

if [[ -n "$decision" ]]; then
  append_section_item "$result_file" "결정 기록" "$decision"
  append_section_item "$readme_file" "최근 체크포인트" "${stage} decision: ${decision}"
fi

if [[ -n "$status" ]]; then
  set_yaml_key "$metadata_file" "current_stage" "$stage"
  set_yaml_key "$metadata_file" "current_status" "$status"
  set_stage_status "$metadata_file" "$stage" "$status"
  append_section_item "$readme_file" "최근 체크포인트" "${stage} lifecycle status updated in metadata.yaml"
fi

echo "checkpoint recorded for ${case_id}/${stage}"
