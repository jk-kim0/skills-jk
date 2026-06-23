#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: finish-stage.sh <case-id> <stage> [--root <dir>] [--run-root <dir>]

Run the user-facing stage finish check. This command hides internal check terms
from normal output and tells the agent what to do next.

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

timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
report_file="${run_root}/${case_id}/${stage}-completion.md"
review_file="${run_root}/${case_id}/${stage}-semantic-review.md"
public_report_file="${run_root}/${case_id}/${stage}-finish-check.md"
public_review_file="${run_root}/${case_id}/${stage}-content-review.md"
check_output="$(mktemp)"

cleanup() {
  rm -f "$check_output"
}
trap cleanup EXIT

set +e
"${script_dir}/complete-stage.sh" "$case_id" "$stage" \
  --root "$case_root" \
  --run-root "$run_root" >"$check_output" 2>&1
status=$?
set -e

if [[ "$status" -eq 0 ]]; then
  if [[ -s "$review_file" && ! -s "$public_review_file" ]]; then
    cp "$review_file" "$public_review_file"
  fi

  {
    echo "# 단계 마무리 점검"
    echo
    echo "- Case ID: \`${case_id}\`"
    echo "- Stage: \`${stage}\`"
    echo "- 상태: \`내용 검토 필요\`"
    echo "- 점검 기록: 런타임 디렉터리에 저장됨"
    echo "- 확인 시각: \`${timestamp}\`"
    echo
    echo "## 다음 행동"
    echo
    echo "- Agent는 case 문서와 단계 문서를 다시 읽고 내용상 완료 가능 여부를 판단한다."
    echo "- 완료 가능하면 내부 완료 처리를 진행한다."
    echo "- 우려가 있으면 사용자에게 진행 여부를 묻는다."
  }
  exit 0
fi

if [[ -s "$report_file" && ! -s "$public_report_file" ]]; then
  cp "$report_file" "$public_report_file"
fi

{
  echo "# 단계 마무리 점검"
  echo
  echo "- Case ID: \`${case_id}\`"
  echo "- Stage: \`${stage}\`"
  echo "- 상태: \`보완 필요\`"
  echo "- 상세 기록: 런타임 디렉터리에 저장됨"
  echo "- 확인 시각: \`${timestamp}\`"
  echo
  echo "## 보완할 내용"
  echo
  if rg -q "^## 미완료 사항$" "$check_output"; then
    awk '
      /^## 미완료 사항$/ { capture = 1; next }
      /^## 처리 방법$/ { capture = 0 }
      capture == 1 && NF > 0 { print }
    ' "$check_output"
  else
    sed 's/^/- /' "$check_output"
  fi
  echo
  echo "## 다음 행동"
  echo
  echo "- Agent가 수정 가능한 문서 문제는 직접 보완한다."
  echo "- 제품 방향, 범위, 일정처럼 결정이 필요한 항목은 사용자에게 질문한다."
  echo "- 보완 후 다시 마무리 점검을 실행한다."
}

exit "$status"
