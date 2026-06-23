#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: complete-stage.sh <case-id> <stage> [--root <dir>] [--run-root <dir>]

Run the deterministic hard gate for stage completion. If hard blockers are found,
print them and leave case state unchanged. If no hard blockers are found, create
a semantic review draft. The stage is not completed until finalize-stage.sh runs.

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

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
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

if [[ -z "$case_id" ]]; then
  echo "case-id and stage are required" >&2
  usage >&2
  exit 1
fi

case_dir="${case_root}/${case_id}"
metadata_file="${case_dir}/metadata.yaml"
readme_file="${case_dir}/README.md"
result_file="${case_dir}/${stage}/result.md"
handoff_file="${case_dir}/${stage}/handoff.md"
report_file="${run_root}/${case_id}/${stage}-completion.md"
semantic_review_file="${run_root}/${case_id}/${stage}-semantic-review.md"
timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
blocker_pattern='(^- $|`not-started`|: not-started|TODO|TBD|FIXME'
blocker_pattern="${blocker_pattern}|미작성|작성 필요|아직 시작하지 않음|아직 정리하지 않음"
blocker_pattern="${blocker_pattern}|\\[미완료\\]"
blocker_pattern="${blocker_pattern}|\\[blocker\\]|\\[blocked\\])"

collect_blockers() {
  local file
  for file in "$readme_file" "$result_file" "$handoff_file"; do
    if [[ ! -s "$file" ]]; then
      printf '%s: missing or empty file\n' "$file"
      continue
    fi

    rg -n --with-filename "$blocker_pattern" "$file" || true
  done

  "${script_dir}/validate-document-quality.sh" \
    "$readme_file" \
    "$result_file" \
    "$handoff_file" || true
}

"${script_dir}/validate-case.sh" "$case_id" "$stage" --root "$case_root" >/dev/null

mkdir -p "$(dirname "$report_file")"
blocker_file="$(mktemp)"

cleanup() {
  rm -f "$blocker_file"
}
trap cleanup EXIT

collect_blockers > "$blocker_file"

if [[ -s "$blocker_file" ]]; then
  {
    echo "# Stage Completion Check"
    echo
    echo "- Case ID: \`${case_id}\`"
    echo "- Stage: \`${stage}\`"
    echo "- Status: \`blocked\`"
    echo "- Checked at: \`${timestamp}\`"
    echo
    echo "## 미완료 사항"
    echo
    sed 's/^/- /' "$blocker_file"
    echo
    echo "## 처리 방법"
    echo
    echo "- 현재 단계에서 끝내야 하는 항목이면 해당 문서를 보완한다."
    echo "- 다음 단계로 넘길 항목이면 \`handoff.md\`에 명확히 인수인계한다."
    echo "- 빈 placeholder는 \`없음\` 또는 실제 내용으로 바꾼다."
  } > "$report_file"

  cat "$report_file"
  exit 1
fi

if [[ ! -s "$semantic_review_file" ]]; then
  cp "${skill_dir}/assets/templates/completion-review.md" "$semantic_review_file"
fi

{
  echo "# Stage Completion Check"
  echo
  echo "- Case ID: \`${case_id}\`"
  echo "- Stage: \`${stage}\`"
  echo "- Status: \`needs-semantic-review\`"
  echo "- Semantic review: \`${semantic_review_file}\`"
  echo "- Checked at: \`${timestamp}\`"
  echo
  echo "## Hard Gate 결과"
  echo
  echo "- 명시적 미완료 신호는 발견하지 못했다."
  echo "- 아직 단계 완료는 확정되지 않았다."
  echo
  echo "## 다음 행동"
  echo
  echo "1. Agent가 semantic review file을 작성한다."
  echo "2. \`completion_decision\`을 \`pass\`, \`proceed-with-concerns\`,"
  echo "   \`blocked\` 중 하나로 정한다."
  echo "3. 통과하면 아래 명령을 실행한다."
  echo "   \`finalize-stage.sh ${case_id} ${stage} --review ${semantic_review_file}\`"
} > "$report_file"

cat "$report_file"
