#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: finalize-stage.sh <case-id> <stage> --review <file> [--root <dir>] [--run-root <dir>]

Finalize a stage after hard gate and semantic review have passed.

Semantic review frontmatter must contain:
  completion_decision: pass

or:
  completion_decision: proceed-with-concerns
  user_approved_concerns: true

Stages:
  plan design build test review documentation release
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
repo_root="$(cd "${skill_dir}/../../.." && pwd)"
case_root="${repo_root}/.sdlc/cases"
run_root="${repo_root}/.agents/runs/sdlc-stage"
case_id=""
stage=""
review_file=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --review)
      review_file="${2:-}"
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
  "")
    echo "case-id and stage are required" >&2
    usage >&2
    exit 1
    ;;
  *)
    echo "unknown stage: $stage" >&2
    usage >&2
    exit 1
    ;;
esac

if [[ -z "$case_id" || -z "$review_file" ]]; then
  echo "case-id, stage, and --review are required" >&2
  usage >&2
  exit 1
fi

case_dir="${case_root}/${case_id}"
metadata_file="${case_dir}/metadata.yaml"
readme_file="${case_dir}/README.md"
report_file="${run_root}/${case_id}/${stage}-finalized.md"
timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

if [[ ! -s "$review_file" ]]; then
  echo "missing semantic review file: $review_file" >&2
  exit 1
fi

if ! "${script_dir}/validate-document-quality.sh" "$review_file"; then
  echo "semantic review document quality check failed" >&2
  exit 1
fi

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

yaml_value() {
  local key="$1"
  awk -F': *' -v key="$key" '$1 == key { gsub(/"/, "", $2); print $2; exit }' "$review_file"
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

append_readme_checkpoint() {
  if ! rg -q "^## 최근 체크포인트$" "$readme_file"; then
    printf '\n## 최근 체크포인트\n\n' >> "$readme_file"
  fi
  printf -- '- `%s`: `%s` 단계 완료 확정\n' "$timestamp" "$stage" >> "$readme_file"
}

"${script_dir}/validate-case.sh" "$case_id" "$stage" --root "$case_root" >/dev/null

decision="$(yaml_value completion_decision)"
approved="$(yaml_value user_approved_concerns)"

case "$decision" in
  pass) ;;
  proceed-with-concerns)
    if [[ "$approved" != "true" ]]; then
      echo "concerns require user_approved_concerns: true" >&2
      exit 1
    fi
    ;;
  blocked|pending|"")
    echo "semantic review does not allow finalize: ${decision:-missing}" >&2
    exit 1
    ;;
  *)
    echo "unknown completion_decision: $decision" >&2
    exit 1
    ;;
esac

finalized_next_stage="$(next_stage "$stage")"

if [[ "$finalized_next_stage" == "done" ]]; then
  set_yaml_key "$metadata_file" "current_stage" "$stage"
  set_yaml_key "$metadata_file" "current_status" "completed"
  set_yaml_key "$metadata_file" "next_stage" "done"
else
  set_yaml_key "$metadata_file" "current_stage" "$finalized_next_stage"
  set_yaml_key "$metadata_file" "current_status" "draft"
  set_yaml_key "$metadata_file" "next_stage" "$(next_stage "$finalized_next_stage")"
  set_stage_status "$metadata_file" "$finalized_next_stage" "draft"
fi

set_stage_status "$metadata_file" "$stage" "completed"
append_readme_checkpoint

mkdir -p "$(dirname "$report_file")"

{
  echo "# Stage Finalized"
  echo
  echo "- Case ID: \`${case_id}\`"
  echo "- Stage: \`${stage}\`"
  echo "- Status: \`completed\`"
  echo "- Next stage: \`${finalized_next_stage}\`"
  echo "- Semantic review: \`${review_file}\`"
  echo "- Finalized at: \`${timestamp}\`"
  echo
  echo "## 다음 행동"
  echo
  if [[ "$finalized_next_stage" == "done" ]]; then
    echo "- case 종료 상태를 확인한다."
  else
    echo "- 다음 단계는 \`prepare-stage.sh ${case_id} ${finalized_next_stage}\`로 시작한다."
  fi
} > "$report_file"

cat "$report_file"
