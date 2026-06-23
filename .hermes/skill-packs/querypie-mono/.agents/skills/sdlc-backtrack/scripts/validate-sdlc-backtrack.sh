#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
repo_root="$(cd "${skill_dir}/../../.." && pwd)"
core_dir="${repo_root}/.agents/sdlc/core"
run_root="${repo_root}/.agents/runs/sdlc-backtrack-validation"

required_files=(
  "SKILL.md"
  "agents/openai.yaml"
  "assets/templates/backtrack-proposal.md"
  "assets/templates/backtrack-result.md"
  "references/workflow.md"
  "references/decision-model.md"
  "references/user-guide.md"
  "scripts/validate-sdlc-backtrack.sh"
)

core_files=(
  "references/stage-backtrack.md"
  "references/stage-contracts.md"
  "references/stage-workflow.md"
  "references/document-quality.md"
  "scripts/scaffold-case.sh"
  "scripts/prepare-stage.sh"
  "scripts/backtrack-stage.sh"
  "scripts/validate-case.sh"
  "scripts/validate-document-quality.sh"
)

missing=()

for file in "${required_files[@]}"; do
  if [[ ! -s "${skill_dir}/${file}" ]]; then
    missing+=("${skill_dir}/${file}")
  fi
done

for file in "${core_files[@]}"; do
  if [[ ! -s "${core_dir}/${file}" ]]; then
    missing+=("${core_dir}/${file}")
  fi
done

if ((${#missing[@]} > 0)); then
  echo "missing required files:" >&2
  printf '  %s\n' "${missing[@]}" >&2
  exit 1
fi

terms_file="$(mktemp)"
trap 'rm -f "$terms_file"' EXIT

if rg -n '(^|[[:space:]])/sdlc-backtrack([[:space:]]|$)' \
  "${repo_root}/AGENTS.md" "${skill_dir}" >"$terms_file"; then
  echo "sdlc-backtrack docs must not imply a slash command adapter exists:" >&2
  cat "$terms_file" >&2
  exit 1
fi

find "$skill_dir" -type f -name '*.md' -print0 | \
  xargs -0 "${core_dir}/scripts/validate-document-quality.sh"

rm -rf "$run_root"
mkdir -p "${run_root}/cases"

case_id="2026-01-01-sample-backtrack-validation"
case_root="${run_root}/cases"

"${core_dir}/scripts/scaffold-case.sh" "$case_id" \
  --title "Sample Backtrack Validation" \
  --ticket "SAMPLE-1" \
  --root "$case_root" \
  --force >/dev/null

python3 - "$case_root/$case_id/metadata.yaml" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
replacements = {
    'current_stage: "plan"': 'current_stage: "test"',
    'next_stage: "design"': 'next_stage: "review"',
    'approved_by: ""': 'approved_by: "validation"',
    '  plan: "draft"': '  plan: "completed"',
    '  design: "not-started"': '  design: "completed"',
    '  build: "not-started"': '  build: "completed"',
    '  test: "not-started"': '  test: "draft"',
}
for source, target in replacements.items():
    text = text.replace(source, target)
path.write_text(text, encoding="utf-8")
PY

"${core_dir}/scripts/validate-case.sh" "$case_id" test --root "$case_root" >/dev/null

"${core_dir}/scripts/backtrack-stage.sh" "$case_id" design \
  --reason "Sample test found a missing design decision." \
  --question "Should the sample contract be part of design scope?" \
  --root "$case_root" \
  --run-root "$run_root" >/dev/null

"${core_dir}/scripts/validate-case.sh" "$case_id" design --root "$case_root" >/dev/null

rg -n 'current_stage: "design"|current_status: "draft"|next_stage: "build"' \
  "$case_root/$case_id/metadata.yaml" >/dev/null
rg -n '^[[:space:]]{2}design: "draft"$|^[[:space:]]{2}build: "blocked"$|^[[:space:]]{2}test: "blocked"$' \
  "$case_root/$case_id/metadata.yaml" >/dev/null

echo "sdlc-backtrack skill is valid"
