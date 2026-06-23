#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
skill_dir="$(cd "${script_dir}/.." && pwd)"
repo_root="$(cd "${skill_dir}/../../.." && pwd)"
core_dir="${repo_root}/.agents/sdlc/core"
run_root="${repo_root}/.agents/runs/sdlc-design-validation"

required_files=(
  "SKILL.md"
  "agents/openai.yaml"
  "assets/prompts/stage-content-review.md"
  "assets/templates/design-result.md"
  "assets/templates/design-handoff.md"
  "assets/templates/build-tasks.md"
  "references/workflow.md"
  "references/task-model.md"
  "references/agent-routing.md"
  "references/roles/backend-designer.md"
  "references/roles/frontend-designer.md"
  "references/roles/core-architect.md"
  "references/roles/infrastructure-designer.md"
  "references/roles/security-risk-reviewer.md"
  "references/roles/qa-design-reviewer.md"
  "references/roles/release-design-reviewer.md"
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

if rg -n "completion_decision|needs-semantic-review|finalize-stage" \
  "${skill_dir}/assets/templates" >/tmp/sdlc-design-template-internal-terms.txt; then
  echo "stage templates expose internal completion terms:" >&2
  cat /tmp/sdlc-design-template-internal-terms.txt >&2
  rm -f /tmp/sdlc-design-template-internal-terms.txt
  exit 1
fi
rm -f /tmp/sdlc-design-template-internal-terms.txt

find "$skill_dir" -type f -name '*.md' -print0 | \
  xargs -0 "${core_dir}/scripts/validate-document-quality.sh"

rm -rf "$run_root"
mkdir -p "${run_root}/cases"

case_id="2026-01-01-sample-design-validation"
case_root="${run_root}/cases"

"${core_dir}/scripts/scaffold-case.sh" "$case_id" \
  --title "Sample Design Validation" \
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
    'current_stage: "plan"': 'current_stage: "design"',
    'current_status: "draft"': 'current_status: "draft"',
    'next_stage: "design"': 'next_stage: "build"',
    'approved_by: ""': 'approved_by: "validation"',
    '  plan: "draft"': '  plan: "completed"',
    '  design: "not-started"': '  design: "draft"',
}
for source, target in replacements.items():
    text = text.replace(source, target)
path.write_text(text, encoding="utf-8")
PY

"${core_dir}/scripts/validate-case.sh" "$case_id" design --root "$case_root" >/dev/null

echo "sdlc-design skill is valid"
