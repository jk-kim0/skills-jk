#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scaffold-case.sh <case-id> [--title <title>] [--ticket <ticket>] [--root <dir>] [--stage-template-root <dir>] [--force]

Create the approved SDLC case directory and all stage documents.

Example:
  scaffold-case.sh 2026-06-04-qpd-5294 --title "KAC WEB ACL issue" --ticket QPD-5294
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
repo_root="$(cd "${skill_dir}/../../.." && pwd)"
template_dir="${skill_dir}/assets/templates"

case_id=""
title=""
ticket=""
case_root="${repo_root}/.sdlc/cases"
stage_template_root=""
force="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --title)
      title="${2:-}"
      shift 2
      ;;
    --ticket)
      ticket="${2:-}"
      shift 2
      ;;
    --root)
      case_root="${2:-}"
      shift 2
      ;;
    --stage-template-root)
      stage_template_root="${2:-}"
      shift 2
      ;;
    --force)
      force="true"
      shift
      ;;
    -*)
      echo "unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
    *)
      if [[ -n "$case_id" ]]; then
        echo "unexpected argument: $1" >&2
        usage >&2
        exit 1
      fi
      case_id="$1"
      shift
      ;;
  esac
done

if [[ -z "$case_id" ]]; then
  echo "case-id is required" >&2
  usage >&2
  exit 1
fi

if [[ ! "$case_id" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9][a-z0-9-]*$ ]]; then
  echo "case-id must match yyyy-mm-dd-name" >&2
  exit 1
fi

title="${title:-$case_id}"
ticket="${ticket:-없음}"
created_at="$(date +%Y-%m-%d)"
case_dir="${case_root}/${case_id}"

sed_escape() {
  printf '%s' "$1" | sed 's/[\/&]/\\&/g'
}

stage_name() {
  case "$1" in
    plan) echo "계획" ;;
    design) echo "설계" ;;
    build) echo "구현" ;;
    test) echo "테스트" ;;
    review) echo "리뷰" ;;
    documentation) echo "문서화" ;;
    release) echo "배포/유지보수" ;;
    *) echo "$1" ;;
  esac
}

render_template() {
  local template="$1"
  local dest="$2"
  local stage="${3:-}"
  local label="${4:-}"

  if [[ -e "$dest" && "$force" != "true" ]]; then
    return
  fi

  mkdir -p "$(dirname "$dest")"
  sed \
    -e "s/{{CASE_ID}}/$(sed_escape "$case_id")/g" \
    -e "s/{{TITLE}}/$(sed_escape "$title")/g" \
    -e "s/{{TICKET}}/$(sed_escape "$ticket")/g" \
    -e "s/{{CREATED_AT}}/$(sed_escape "$created_at")/g" \
    -e "s/{{STAGE}}/$(sed_escape "$stage")/g" \
    -e "s/{{STAGE_NAME}}/$(sed_escape "$label")/g" \
    "$template" > "$dest"
}

template_path() {
  local name="$1"

  if [[ -n "$stage_template_root" && -s "${stage_template_root}/${name}" ]]; then
    printf '%s\n' "${stage_template_root}/${name}"
    return
  fi

  printf '%s\n' "${template_dir}/${name}"
}

mkdir -p "$case_dir"

render_template "$(template_path case-readme.md)" "${case_dir}/README.md"
render_template "$(template_path case-metadata.yaml)" "${case_dir}/metadata.yaml"
render_template "$(template_path case-evidence.md)" "${case_dir}/evidence.md"

stages=(plan design build test review documentation release)
for stage in "${stages[@]}"; do
  mkdir -p "${case_dir}/${stage}"
  label="$(stage_name "$stage")"
  result_template="$(template_path stage-result.md)"
  handoff_template="$(template_path stage-handoff.md)"
  if [[ -n "$stage_template_root" && -s "${stage_template_root}/${stage}-result.md" ]]; then
    result_template="${stage_template_root}/${stage}-result.md"
  fi
  if [[ -n "$stage_template_root" && -s "${stage_template_root}/${stage}-handoff.md" ]]; then
    handoff_template="${stage_template_root}/${stage}-handoff.md"
  fi
  render_template "$result_template" "${case_dir}/${stage}/result.md" "$stage" "$label"
  render_template "$handoff_template" "${case_dir}/${stage}/handoff.md" "$stage" "$label"
done

render_template "$(template_path build-tasks.md)" "${case_dir}/build/tasks.md"

echo "created SDLC case: ${case_dir}"
