#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: collect-jira.sh <issue-key> --run-id <run-id> [options]

Collect a Jira issue through jira-cli and store raw/plain output as run artifacts.

Options:
  --comments <n>   Number of comments for plain output. Default: 50
  --jira-bin <bin> Jira CLI executable. Default: jira
  --run-root <dir> Run artifact root. Default: .agents/runs/sdlc-plan
  --help           Show this help.

Example:
  collect-jira.sh QPD-5294 --run-id 2026-06-04-qpd-5294
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
repo_root="$(cd "${skill_dir}/../../.." && pwd)"

issue_key=""
run_id=""
comments="50"
jira_bin="jira"
run_root="${repo_root}/.agents/runs/sdlc-plan"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --run-id)
      run_id="${2:-}"
      shift 2
      ;;
    --comments)
      comments="${2:-}"
      shift 2
      ;;
    --jira-bin)
      jira_bin="${2:-}"
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
      if [[ -n "$issue_key" ]]; then
        echo "unexpected argument: $1" >&2
        usage >&2
        exit 1
      fi
      issue_key="$1"
      shift
      ;;
  esac
done

if [[ -z "$issue_key" || -z "$run_id" ]]; then
  echo "issue-key and --run-id are required" >&2
  usage >&2
  exit 1
fi

if [[ ! "$issue_key" =~ ^[A-Z][A-Z0-9]+-[0-9]+$ ]]; then
  echo "issue-key must look like QPD-5294" >&2
  exit 1
fi

if [[ ! "$comments" =~ ^[0-9]+$ ]]; then
  echo "--comments must be a non-negative integer" >&2
  exit 1
fi

if [[ "$jira_bin" == */* ]]; then
  if [[ ! -x "$jira_bin" ]]; then
    echo "jira CLI not found: $jira_bin" >&2
    exit 127
  fi
elif ! command -v "$jira_bin" >/dev/null 2>&1; then
  echo "jira CLI not found: $jira_bin" >&2
  exit 127
fi

source_dir="${run_root}/${run_id}/sources/jira"
mkdir -p "$source_dir"

raw_file="${source_dir}/${issue_key}.raw.json"
plain_file="${source_dir}/${issue_key}.plain.txt"
meta_file="${source_dir}/${issue_key}.meta.md"
raw_err="${source_dir}/${issue_key}.raw.stderr.txt"
plain_err="${source_dir}/${issue_key}.plain.stderr.txt"
retrieved_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

set +e
"$jira_bin" issue view "$issue_key" --raw >"$raw_file" 2>"$raw_err"
raw_status=$?
"$jira_bin" issue view "$issue_key" --plain --comments "$comments" >"$plain_file" 2>"$plain_err"
plain_status=$?
set -e

{
  echo "# Jira Source"
  echo
  echo "- Issue: \`${issue_key}\`"
  echo "- Retrieved at: \`${retrieved_at}\`"
  echo "- CLI: \`${jira_bin}\`"
  echo "- Raw command: \`${jira_bin} issue view ${issue_key} --raw\`"
  echo "- Plain command: \`${jira_bin} issue view ${issue_key} --plain --comments ${comments}\`"
  echo "- Raw status: \`${raw_status}\`"
  echo "- Plain status: \`${plain_status}\`"
  echo "- Raw output: \`${raw_file}\`"
  echo "- Plain output: \`${plain_file}\`"
  echo
  echo "## Evidence Note"
  if [[ "$raw_status" -eq 0 && "$plain_status" -eq 0 ]]; then
    echo "Jira CLI 조회에 성공했다."
    echo "승인 case에는 원문을 그대로 복사하지 말고 요약한다."
  else
    echo "Jira CLI 조회에 실패했다. 이 실패를 evidence gap으로 기록한다."
    echo
    echo "## Failure Files"
    echo
    echo "- Raw stderr: \`${raw_err}\`"
    echo "- Plain stderr: \`${plain_err}\`"
  fi
} > "$meta_file"

if [[ "$raw_status" -ne 0 || "$plain_status" -ne 0 ]]; then
  echo "failed to collect Jira issue: ${issue_key}" >&2
  echo "metadata: ${meta_file}" >&2
  exit 1
fi

echo "collected Jira issue: ${issue_key}"
echo "raw: ${raw_file}"
echo "plain: ${plain_file}"
echo "metadata: ${meta_file}"
