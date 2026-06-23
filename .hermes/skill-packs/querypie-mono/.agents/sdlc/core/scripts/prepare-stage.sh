#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: prepare-stage.sh <case-id> <stage> [--root <dir>] [--run-root <dir>] [--no-write]

Print the documents a stage must read and write. By default the same context is
also saved under .agents/runs/sdlc-stage/<case-id>/<stage>-context.md.

Stages:
  plan design build test review documentation release
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
repo_root="$(cd "${skill_dir}/../../.." && pwd)"
case_root="${repo_root}/.sdlc/cases"
run_root="${repo_root}/.agents/runs/sdlc-stage"
write_context="true"
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
    --no-write)
      write_context="false"
      shift
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

case_dir="${case_root}/${case_id}"

require_stage() {
  case "$1" in
    plan|design|build|test|review|documentation|release) ;;
    *)
      echo "unknown stage: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
}

if [[ -z "$case_id" || -z "$stage" ]]; then
  echo "case-id and stage are required" >&2
  usage >&2
  exit 1
fi

require_stage "$stage"

if [[ ! -d "$case_dir" ]]; then
  echo "missing case directory: $case_dir" >&2
  exit 1
fi

required_docs() {
  case "$stage" in
    plan)
      printf '%s\n' "README.md" "metadata.yaml" "evidence.md"
      ;;
    design)
      printf '%s\n' "README.md" "metadata.yaml" "plan/result.md" "plan/handoff.md"
      ;;
    build)
      printf '%s\n' "README.md" "metadata.yaml" "design/result.md" "design/handoff.md" "build/tasks.md"
      ;;
    test)
      printf '%s\n' "README.md" "metadata.yaml" "build/result.md" "build/handoff.md"
      ;;
    review)
      printf '%s\n' "README.md" "metadata.yaml" "test/result.md" "test/handoff.md"
      ;;
    documentation)
      printf '%s\n' "README.md" "metadata.yaml" "review/result.md" "review/handoff.md"
      ;;
    release)
      printf '%s\n' "README.md" "metadata.yaml" "documentation/result.md" "documentation/handoff.md"
      ;;
  esac
}

write_docs() {
  case "$stage" in
    plan)
      printf '%s\n' "plan/result.md" "plan/handoff.md" "README.md" "metadata.yaml" "evidence.md"
      ;;
    design)
      printf '%s\n' "design/result.md" "design/handoff.md" "build/tasks.md" "README.md" "metadata.yaml"
      ;;
    build)
      printf '%s\n' "build/result.md" "build/handoff.md" "README.md" "metadata.yaml"
      ;;
    test)
      printf '%s\n' "test/result.md" "test/handoff.md" "README.md" "metadata.yaml"
      ;;
    review)
      printf '%s\n' "review/result.md" "review/handoff.md" "README.md" "metadata.yaml"
      ;;
    documentation)
      printf '%s\n' "documentation/result.md" "documentation/handoff.md" "README.md" "metadata.yaml"
      ;;
    release)
      printf '%s\n' "release/result.md" "release/handoff.md" "README.md" "metadata.yaml"
      ;;
  esac
}

context_file="${run_root}/${case_id}/${stage}-context.md"
tmp_context="$(mktemp)"

{
  echo "# Stage Context"
  echo
  echo "- Case ID: \`${case_id}\`"
  echo "- Stage: \`${stage}\`"
  echo "- Case directory: \`${case_dir}\`"
  echo "- Generated at: \`$(date -u +%Y-%m-%dT%H:%M:%SZ)\`"
  echo
  echo "## 반드시 읽을 문서"
  while IFS= read -r doc; do
    echo "- \`${doc}\`"
  done < <(required_docs)
  echo
  echo "## 필요할 때만 읽을 문서"
  echo "- \`evidence.md\`"
  echo
  echo "## 작성해야 할 문서"
  while IFS= read -r doc; do
    echo "- \`${doc}\`"
  done < <(write_docs)
  echo
  echo "## 공통 규칙"
  echo "- chat history를 공식 상태로 간주하지 않는다."
  echo "- 사용자 결정은 현재 단계 문서와 metadata.yaml에 기록한다."
  echo "- 단계 lifecycle status는 metadata.yaml에만 기록한다."
  echo "- 앞 단계 결정 수정이 필요하면 stage-backtrack 절차를 따른다."
  echo "- 단계 종료 전 validate-case.sh를 실행한다."
  echo "- 공식 산출물은 한국어로 작성한다."
} > "$tmp_context"

cat "$tmp_context"

if [[ "$write_context" == "true" ]]; then
  mkdir -p "$(dirname "$context_file")"
  cp "$tmp_context" "$context_file"
  echo
  echo "saved stage context: ${context_file}"
fi

rm -f "$tmp_context"
