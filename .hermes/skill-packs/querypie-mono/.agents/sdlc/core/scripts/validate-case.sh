#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: validate-case.sh <case-id> [stage] [--root <dir>]

Validate the approved SDLC case directory and optional stage documents.

Stages:
  plan design build test review documentation release
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
repo_root="$(cd "${skill_dir}/../../.." && pwd)"
metadata_schema="${skill_dir}/schemas/case-metadata.schema.json"
metadata_validator="${script_dir}/validate-metadata-schema.py"
case_root="${repo_root}/.sdlc/cases"
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

if [[ -z "$case_id" ]]; then
  echo "case-id is required" >&2
  usage >&2
  exit 1
fi

case "$stage" in
  ""|plan|design|build|test|review|documentation|release) ;;
  *)
    echo "unknown stage: $stage" >&2
    usage >&2
    exit 1
    ;;
esac

case_dir="${case_root}/${case_id}"
stages=(plan design build test review documentation release)
missing=()

require_file() {
  local file="$1"
  if [[ ! -s "$file" ]]; then
    missing+=("$file")
  fi
}

require_dir() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    missing+=("$dir")
  fi
}

require_dir "$case_dir"
require_file "${case_dir}/README.md"
require_file "${case_dir}/metadata.yaml"
require_file "${case_dir}/evidence.md"
require_file "$metadata_schema"
require_file "$metadata_validator"

for item in "${stages[@]}"; do
  require_dir "${case_dir}/${item}"
  require_file "${case_dir}/${item}/result.md"
  require_file "${case_dir}/${item}/handoff.md"
done

require_file "${case_dir}/build/tasks.md"

if [[ -n "$stage" ]]; then
  require_file "${case_dir}/${stage}/result.md"
  require_file "${case_dir}/${stage}/handoff.md"
  if [[ "$stage" == "build" ]]; then
    require_file "${case_dir}/build/tasks.md"
  fi
fi

if ((${#missing[@]} > 0)); then
  echo "invalid SDLC case: ${case_id}" >&2
  printf 'missing or empty: %s\n' "${missing[@]}" >&2
  exit 1
fi

metadata_args=("--case-id" "$case_id")
if [[ -n "$stage" ]]; then
  metadata_args+=("--stage" "$stage")
fi

python3 "$metadata_validator" "${case_dir}/metadata.yaml" "$metadata_schema" "${metadata_args[@]}"

lifecycle_status_files=("${case_dir}/README.md")
for item in "${stages[@]}"; do
  lifecycle_status_files+=("${case_dir}/${item}/result.md" "${case_dir}/${item}/handoff.md")
done

if rg -n --with-filename "^- (현재 단계|상태):|^- Status:" \
  "${lifecycle_status_files[@]}" >&2; then
  echo "case markdown duplicates lifecycle status; use metadata.yaml only" >&2
  exit 1
fi

if ! find "$case_dir" -type f \( -name '*.md' -o -name '*.markdown' \) -print0 | \
  xargs -0 "${script_dir}/validate-document-quality.sh" >/dev/null; then
  echo "case markdown quality check failed" >&2
  find "$case_dir" -type f \( -name '*.md' -o -name '*.markdown' \) -print0 | \
    xargs -0 "${script_dir}/validate-document-quality.sh" >&2 || true
  exit 1
fi

echo "SDLC case is valid: ${case_id}"
