#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
repo_root="$(cd "${skill_dir}/../../.." && pwd)"
core_dir="${repo_root}/.agents/sdlc/core"
run_root="${repo_root}/.agents/runs/sdlc-build-validation"

required_files=(
  "SKILL.md"
  "agents/openai.yaml"
  "assets/prompts/stage-content-review.md"
  "assets/templates/build-result.md"
  "assets/templates/build-handoff.md"
  "references/workflow.md"
  "references/user-guide.md"
  "references/agent-routing.md"
  "references/roles/backend-builder.md"
  "references/roles/frontend-builder.md"
  "references/roles/core-builder.md"
  "references/roles/infrastructure-builder.md"
  "references/roles/security-risk-reviewer.md"
  "references/roles/qa-build-reviewer.md"
  "references/roles/release-build-reviewer.md"
  "scripts/validate-sdlc-build.sh"
)

core_files=(
  "references/stage-workflow.md"
  "references/stage-contracts.md"
  "references/stage-backtrack.md"
  "references/output-contracts.md"
  "references/document-quality.md"
  "references/stage-finish.md"
  "references/completion-review.md"
  "scripts/scaffold-case.sh"
  "scripts/backtrack-stage.sh"
  "scripts/prepare-stage.sh"
  "scripts/finish-stage.sh"
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

template_terms_file="$(mktemp)"
trap 'rm -f "$template_terms_file"' EXIT

if rg -n "completion_decision|needs-semantic-review|finalize-stage" \
  "${skill_dir}/assets/templates" >"$template_terms_file"; then
  echo "stage templates expose internal completion terms:" >&2
  cat "$template_terms_file" >&2
  exit 1
fi

if rg -n '(^|[[:space:]])/sdlc-build([[:space:]]|$)' \
  "${repo_root}/AGENTS.md" "${skill_dir}" >"$template_terms_file"; then
  echo "sdlc-build docs must not imply a slash command adapter exists:" >&2
  cat "$template_terms_file" >&2
  exit 1
fi

if ! rg -q '^## 주요 내용$' "${skill_dir}/assets/templates/build-result.md"; then
  echo "build result template must include ## 주요 내용" >&2
  exit 1
fi

find "$skill_dir" -type f -name '*.md' -print0 | \
  xargs -0 "${core_dir}/scripts/validate-document-quality.sh"

rm -rf "$run_root"
mkdir -p "${run_root}/cases"

case_id="2026-01-01-sample-build-validation"
case_root="${run_root}/cases"

"${core_dir}/scripts/scaffold-case.sh" "$case_id" \
  --title "Sample Build Validation" \
  --ticket "SAMPLE-1" \
  --root "$case_root" \
  --stage-template-root "${skill_dir}/assets/templates" \
  --force >/dev/null

python3 - "$case_root/$case_id/metadata.yaml" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
replacements = {
    'current_stage: "plan"': 'current_stage: "build"',
    'next_stage: "design"': 'next_stage: "test"',
    'approved_by: ""': 'approved_by: "validation"',
    '  plan: "draft"': '  plan: "completed"',
    '  design: "not-started"': '  design: "completed"',
    '  build: "not-started"': '  build: "draft"',
}
for source, target in replacements.items():
    text = text.replace(source, target)
path.write_text(text, encoding="utf-8")
PY

"${core_dir}/scripts/validate-case.sh" "$case_id" build --root "$case_root" >/dev/null

"${core_dir}/scripts/backtrack-stage.sh" "$case_id" design \
  --reason "Sample build discovered a design decision gap." \
  --question "Should the sample design include the missing contract?" \
  --root "$case_root" \
  --run-root "$run_root" >/dev/null

"${core_dir}/scripts/validate-case.sh" "$case_id" design --root "$case_root" >/dev/null

rg -n 'current_stage: "design"|current_status: "draft"|next_stage: "build"' \
  "$case_root/$case_id/metadata.yaml" >/dev/null
rg -n '^[[:space:]]{2}design: "draft"$|^[[:space:]]{2}build: "blocked"$' \
  "$case_root/$case_id/metadata.yaml" >/dev/null

echo "sdlc-build skill is valid"
