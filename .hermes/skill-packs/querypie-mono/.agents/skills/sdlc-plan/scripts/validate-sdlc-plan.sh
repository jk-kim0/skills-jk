#!/usr/bin/env bash
set -euo pipefail

required_files=(
  ".agents/skills/sdlc-plan/SKILL.md"
  ".agents/skills/sdlc-plan/references/workflow.md"
  ".agents/skills/sdlc-plan/references/agent-routing.md"
  ".agents/skills/sdlc-plan/references/agent-invocation.md"
  ".agents/skills/sdlc-plan/references/evidence-collection.md"
  ".agents/skills/sdlc-plan/references/case-splitting.md"
  ".agents/skills/sdlc-plan/references/component-agent-registry.md"
  ".agents/skills/sdlc-plan/references/user-guide.md"
  ".agents/sdlc/core/README.md"
  ".agents/sdlc/core/references/output-contracts.md"
  ".agents/sdlc/core/references/case-structure.md"
  ".agents/sdlc/core/references/stage-workflow.md"
  ".agents/sdlc/core/references/stage-contracts.md"
  ".agents/sdlc/core/references/stage-finish.md"
  ".agents/sdlc/core/references/completion-review.md"
  ".agents/sdlc/core/references/document-quality.md"
  ".agents/sdlc/core/references/stage-skill-authoring.md"
  ".agents/sdlc/core/config/prettier.config.json"
  ".agents/sdlc/core/config/markdownlint.json"
  ".agents/sdlc/core/schemas/case-metadata.schema.json"
  ".agents/skills/sdlc-plan/assets/prompts/stage-content-review.md"
  ".agents/skills/sdlc-plan/references/source-adapters.md"
  ".agents/skills/sdlc-plan/scripts/collect-jira.sh"
  ".agents/skills/sdlc-plan/scripts/fixtures/mock-jira-success.sh"
  ".agents/skills/sdlc-plan/scripts/validate-sdlc-plan.sh"
  ".agents/sdlc/core/scripts/scaffold-case.sh"
  ".agents/sdlc/core/scripts/prepare-stage.sh"
  ".agents/sdlc/core/scripts/checkpoint-stage.sh"
  ".agents/sdlc/core/scripts/complete-stage.sh"
  ".agents/sdlc/core/scripts/finish-stage.sh"
  ".agents/sdlc/core/scripts/finalize-stage.sh"
  ".agents/sdlc/core/scripts/format-document-quality.sh"
  ".agents/sdlc/core/scripts/validate-document-quality.sh"
  ".agents/sdlc/core/scripts/validate-metadata-schema.py"
  ".agents/sdlc/core/scripts/validate-case.sh"
  ".claude/skills/sdlc-plan/SKILL.md"
  ".claude/commands/sdlc-plan.md"
)

roles=(
  "evidence-collector"
  "evidence-synthesizer"
  "case-split-advisor"
  "product-planner"
  "senior-engineer"
  "technical-manager"
  "ux-designer"
  "qa-manager"
  "release-manager"
  "planning-reviewer"
  "risk-reviewer"
)

all_roles=("plan-agent" "${roles[@]}")

core_templates=(
  "case-readme.md"
  "case-metadata.yaml"
  "case-evidence.md"
  "stage-result.md"
  "stage-handoff.md"
  "completion-review.md"
  "build-tasks.md"
)

plan_templates=(
  "plan-result.md"
  "plan-handoff.md"
  "planning-document.md"
  "case-group.md"
  "case-split-proposal.md"
  "discovery-report.md"
  "idea-validation-report.md"
  "context-brief.md"
  "triage-report.md"
)

for file in "${required_files[@]}"; do
  test -s "$file" || {
    echo "missing required file: $file"
    exit 1
  }
done

for role in "${all_roles[@]}"; do
  test -s ".agents/skills/sdlc-plan/references/roles/${role}.md" || {
    echo "missing role spec: $role"
    exit 1
  }
done

for role in "${roles[@]}"; do
  test -s ".codex/agents/sdlc-${role}.toml" || {
    echo "missing Codex adapter: $role"
    exit 1
  }

  test -s ".claude/agents/sdlc-${role}.md" || {
    echo "missing Claude adapter: $role"
    exit 1
  }
done

for template in "${core_templates[@]}"; do
  test -s ".agents/sdlc/core/assets/templates/${template}" || {
    echo "missing core template: $template"
    exit 1
  }
done

for template in "${plan_templates[@]}"; do
  test -s ".agents/skills/sdlc-plan/assets/templates/${template}" || {
    echo "missing plan template: $template"
    exit 1
  }
done

rg -n "name: sdlc-plan|description:|Humans decide" \
  .agents/skills/sdlc-plan/SKILL.md >/dev/null
rg -n "case 구조|상태 관리|문서 품질|완료 절차" \
  .agents/sdlc/core/README.md >/dev/null
rg -n "공통 파일을 복사하지 않는다|stage-skill-authoring.md|source of truth" \
  .agents/sdlc/core/README.md \
  .agents/sdlc/core/references/stage-skill-authoring.md >/dev/null
rg -n "sdlc-design|sdlc-build|validate-sdlc-<stage>|stage-template-root" \
  .agents/sdlc/core/references/stage-skill-authoring.md >/dev/null
rg -n "시작하기|계획 준비 요약|마무리해줘|산출물 위치" \
  .agents/skills/sdlc-plan/references/user-guide.md >/dev/null
rg -n "references/user-guide.md" \
  .agents/skills/sdlc-plan/SKILL.md >/dev/null
rg -n "한국어|Korean" \
  .agents/skills/sdlc-plan/SKILL.md \
  .agents/sdlc/core/references/output-contracts.md >/dev/null
rg -n "README.md|metadata.yaml|evidence.md|prepare-stage.sh|checkpoint-stage.sh" \
  .agents/sdlc/core/references/case-structure.md \
  .agents/sdlc/core/references/stage-contracts.md >/dev/null
rg -n "case-metadata.schema.json|metadata.yaml.*schema" \
  .agents/skills/sdlc-plan/SKILL.md \
  .agents/sdlc/core/references/case-structure.md \
  .agents/sdlc/core/references/document-quality.md \
  .agents/sdlc/core/references/output-contracts.md >/dev/null
rg -n "runtime artifact|\\.agents/runs|evidence.md" \
  .agents/sdlc/core/references/case-structure.md \
  .agents/skills/sdlc-plan/references/evidence-collection.md \
  .agents/sdlc/core/references/output-contracts.md \
  .agents/skills/sdlc-plan/assets/prompts/stage-content-review.md >/dev/null
rg -n "Lifecycle status|lifecycle status|단계 lifecycle status" \
  .agents/skills/sdlc-plan/SKILL.md \
  .agents/sdlc/core/references/case-structure.md \
  .agents/sdlc/core/references/document-quality.md \
  .agents/sdlc/core/references/output-contracts.md \
  .agents/sdlc/core/references/stage-contracts.md >/dev/null
rg -n "입력|티키타카|출력|출력 보정" \
  .agents/sdlc/core/references/stage-workflow.md \
  .agents/sdlc/core/references/stage-contracts.md \
  .agents/skills/sdlc-plan/SKILL.md >/dev/null
rg -n "계획 준비 요약|공식 case 생성|사용자 승인" \
  .agents/skills/sdlc-plan/references/workflow.md \
  .agents/skills/sdlc-plan/SKILL.md \
  .claude/commands/sdlc-plan.md >/dev/null
rg -n "자료가 부족|부족한 자료|한 가지 질문" \
  .agents/skills/sdlc-plan/references/workflow.md \
  .agents/skills/sdlc-plan/SKILL.md >/dev/null
rg -n "sdlc-plan|sdlc-design|sdlc-build|sdlc-test" \
  .agents/sdlc/core/references/stage-workflow.md >/dev/null
rg -n "complete-stage.sh|완료 의사|미완료" \
  .agents/sdlc/core/references/stage-contracts.md \
  .agents/sdlc/core/references/case-structure.md >/dev/null
rg -n "마무리해줘|finish-stage.sh|다음 단계로 넘겨" \
  .agents/skills/sdlc-plan/SKILL.md \
  .agents/sdlc/core/references/stage-finish.md \
  .claude/commands/sdlc-plan.md >/dev/null
rg -n "대화 기록에 의존하지 말라|마무리 완료|보완 필요|진행 승인 필요" \
  .agents/skills/sdlc-plan/assets/prompts/stage-content-review.md \
  .agents/sdlc/core/references/stage-finish.md >/dev/null
rg -n "README.md|metadata.yaml|result.md|handoff.md|evidence.md" \
  .agents/skills/sdlc-plan/assets/prompts/stage-content-review.md >/dev/null
rg -n "확정 결정|열린 결정|다음 단계|내용상 완료" \
  .agents/skills/sdlc-plan/assets/prompts/stage-content-review.md >/dev/null

user_facing_internal_terms="hard gate|semantic gate|\\bgate\\b|semantic[- ]review|finalize-stage"
user_facing_internal_terms="${user_facing_internal_terms}|complete-stage|completion_decision"
user_facing_internal_terms="${user_facing_internal_terms}|needs-semantic-review"
if rg -n -i "$user_facing_internal_terms" \
  .agents/skills/sdlc-plan/SKILL.md \
  .agents/sdlc/core/references/stage-finish.md \
  .claude/commands/sdlc-plan.md \
  .claude/skills/sdlc-plan/SKILL.md >/dev/null; then
  echo "user-facing finish flow exposes internal gate terms"
  rg -n -i "$user_facing_internal_terms" \
    .agents/skills/sdlc-plan/SKILL.md \
    .agents/sdlc/core/references/stage-finish.md \
    .claude/commands/sdlc-plan.md \
    .claude/skills/sdlc-plan/SKILL.md
  exit 1
fi

rg -n "semantic review|finalize-stage.sh|completion_decision" \
  .agents/sdlc/core/references/completion-review.md \
  .agents/sdlc/core/references/stage-contracts.md >/dev/null
rg -n "printWidth|80|100|읽기 쉬운|문서 품질" \
  .agents/sdlc/core/references/document-quality.md \
  .agents/sdlc/core/references/output-contracts.md >/dev/null
rg -n "proseWrap|MD013|markdownlint|Prettier" \
  .agents/sdlc/core/config/prettier.config.json \
  .agents/sdlc/core/config/markdownlint.json \
  .agents/sdlc/core/references/document-quality.md >/dev/null
rg -n "plan|design|build|test|review|documentation|release" \
  .agents/sdlc/core/references/stage-contracts.md >/dev/null
rg -n "Jira CLI|collect-jira.sh|jira issue view|--raw|--plain" \
  .agents/skills/sdlc-plan/references/source-adapters.md \
  .agents/skills/sdlc-plan/references/evidence-collection.md >/dev/null
rg -n "skill activation cannot force|explicit user approval|same-session role review" \
  .agents/skills/sdlc-plan/references/agent-invocation.md >/dev/null
rg -n "검토 방식|별도 역할 Agent|기본 검토" \
  .agents/skills/sdlc-plan/references/agent-invocation.md \
  .agents/skills/sdlc-plan/references/workflow.md >/dev/null
rg -n "역할 Agent 의견|사용자 승인|동일 세션" \
  .agents/skills/sdlc-plan/references/workflow.md \
  .agents/sdlc/core/references/stage-workflow.md >/dev/null
rg -n "source-adapters.md|collect-jira.sh" \
  .agents/skills/sdlc-plan/references/roles/evidence-collector.md \
  .codex/agents/sdlc-evidence-collector.toml \
  .claude/agents/sdlc-evidence-collector.md >/dev/null
rg -n "Korean|한국어" \
  .codex/agents/sdlc-*.toml \
  .claude/agents/sdlc-*.md \
  .claude/skills/sdlc-plan/SKILL.md \
  .claude/commands/sdlc-plan.md >/dev/null
rg -n "Do not edit product source code" .codex/agents/sdlc-*.toml .claude/agents/sdlc-*.md >/dev/null
rg -n "\.agents/runs/" .gitignore >/dev/null

bash .agents/sdlc/core/scripts/prepare-stage.sh --help >/dev/null
bash .agents/skills/sdlc-plan/scripts/collect-jira.sh --help >/dev/null
bash .agents/sdlc/core/scripts/scaffold-case.sh --help >/dev/null
bash .agents/sdlc/core/scripts/checkpoint-stage.sh --help >/dev/null
bash .agents/sdlc/core/scripts/complete-stage.sh --help >/dev/null
bash .agents/sdlc/core/scripts/finish-stage.sh --help >/dev/null
bash .agents/sdlc/core/scripts/finalize-stage.sh --help >/dev/null
bash .agents/sdlc/core/scripts/format-document-quality.sh --help >/dev/null
bash .agents/sdlc/core/scripts/validate-document-quality.sh --help >/dev/null
python3 .agents/sdlc/core/scripts/validate-metadata-schema.py --help >/dev/null
bash .agents/sdlc/core/scripts/validate-case.sh --help >/dev/null

rg -n "case-metadata.schema.json|validate-metadata-schema.py|validate-document-quality" \
  .agents/sdlc/core/scripts/validate-case.sh >/dev/null
rg -n "additionalProperties|required|stage_statuses|stage_outputs" \
  .agents/sdlc/core/schemas/case-metadata.schema.json >/dev/null
rg -n "validate_stage_outputs|validate_stage_statuses|--case-id|--stage" \
  .agents/sdlc/core/scripts/validate-metadata-schema.py >/dev/null
rg -n "stage_statuses|not-started" \
  .agents/sdlc/core/assets/templates/case-metadata.yaml >/dev/null
if rg -n "^- (현재 단계|상태):|^- Status:" \
  .agents/sdlc/core/assets/templates/case-readme.md \
  .agents/sdlc/core/assets/templates/build-tasks.md \
  .agents/sdlc/core/assets/templates/stage-result.md \
  .agents/sdlc/core/assets/templates/stage-handoff.md \
  .agents/skills/sdlc-plan/assets/templates/plan-result.md \
  .agents/skills/sdlc-plan/assets/templates/plan-handoff.md >/dev/null; then
  echo "official case templates duplicate lifecycle status"
  rg -n "^- (현재 단계|상태):|^- Status:" \
    .agents/sdlc/core/assets/templates/case-readme.md \
    .agents/sdlc/core/assets/templates/build-tasks.md \
    .agents/sdlc/core/assets/templates/stage-result.md \
    .agents/sdlc/core/assets/templates/stage-handoff.md \
    .agents/skills/sdlc-plan/assets/templates/plan-result.md \
    .agents/skills/sdlc-plan/assets/templates/plan-handoff.md
  exit 1
fi
rg -n "empty table cell|empty field" \
  .agents/sdlc/core/scripts/validate-document-quality.sh >/dev/null
rg -n "아직 작성하지 않음|없음|아직 시작하지 않음" \
  .agents/sdlc/core/assets/templates/build-tasks.md \
  .agents/sdlc/core/assets/templates/stage-result.md \
  .agents/sdlc/core/assets/templates/stage-handoff.md \
  .agents/sdlc/core/assets/templates/case-readme.md \
  .agents/sdlc/core/assets/templates/case-evidence.md \
  .agents/skills/sdlc-plan/assets/templates/plan-result.md \
  .agents/skills/sdlc-plan/assets/templates/plan-handoff.md >/dev/null

if command -v prettier >/dev/null 2>&1; then
  :
elif command -v mise >/dev/null 2>&1 && mise which prettier >/dev/null 2>&1; then
  :
else
  echo "prettier is required. Run: mise install"
  exit 1
fi

if command -v markdownlint-cli2 >/dev/null 2>&1; then
  :
elif command -v mise >/dev/null 2>&1 && mise which markdownlint-cli2 >/dev/null 2>&1; then
  :
elif command -v npx >/dev/null 2>&1; then
  :
else
  echo "markdownlint-cli2 or npx is required for Markdown linting"
  exit 1
fi

document_quality_root=".agents/runs/sdlc-plan-validation/document-quality"
rm -rf "$document_quality_root"
mkdir -p "$document_quality_root"

good_document="${document_quality_root}/good.md"
bad_document="${document_quality_root}/bad.md"
plain_bad_document="${document_quality_root}/plain-bad.md"

cat > "$good_document" <<'EOF'
# 좋은 문서

## 요약

다음 항목을 포함한다:

- 추천 방향: 현재 단계 산출물의 결론과 다음 행동을 짧게 쓴다.
- 남은 결정: 없음
EOF

cat > "$bad_document" <<'EOF'
# 나쁜 문서

## 요약

-
- 문제:
- 이 줄은 의도적으로 100자를 넘겨서 문서 품질 검증이 긴 문장을 차단하는지 확인하기 위해 만든 나쁜 예시 문장입니다. 읽는 사람이 한 번에 이해하기 어렵습니다.
EOF

cat > "$plain_bad_document" <<'EOF'
# 나쁜 일반 필드 문서

## 요약

작성일:
EOF

.agents/sdlc/core/scripts/validate-document-quality.sh "$good_document" >/dev/null

if .agents/sdlc/core/scripts/validate-document-quality.sh \
  "$bad_document" >/dev/null 2>&1; then
  echo "validate-document-quality accepted bad document"
  exit 1
fi

if .agents/sdlc/core/scripts/validate-document-quality.sh \
  "$plain_bad_document" >/dev/null 2>&1; then
  echo "validate-document-quality accepted empty plain field"
  exit 1
fi

format_document="${document_quality_root}/format.md"
cat > "$format_document" <<'EOF'
# 포맷 문서

## 요약

- 추천 방향: 자동 포맷 명령은 Markdown 문법 포맷만 정리한다.
- 줄 길이 위반은 lint가 보고하고 사람이 직접 문장을 나눈다.
EOF

.agents/sdlc/core/scripts/format-document-quality.sh "$format_document" >/dev/null
.agents/sdlc/core/scripts/validate-document-quality.sh "$format_document" >/dev/null

jira_validation_root=".agents/runs/sdlc-plan-validation/jira"
rm -rf "$jira_validation_root"

.agents/skills/sdlc-plan/scripts/collect-jira.sh QPD-1 \
  --run-id collect-ok \
  --run-root "$jira_validation_root" \
  --jira-bin .agents/skills/sdlc-plan/scripts/fixtures/mock-jira-success.sh \
  --comments 3 >/dev/null

test -s "$jira_validation_root/collect-ok/sources/jira/QPD-1.raw.json"
test -s "$jira_validation_root/collect-ok/sources/jira/QPD-1.plain.txt"
test -s "$jira_validation_root/collect-ok/sources/jira/QPD-1.meta.md"

if .agents/skills/sdlc-plan/scripts/collect-jira.sh BAD/KEY \
  --run-id collect-bad \
  --run-root "$jira_validation_root" \
  --jira-bin .agents/skills/sdlc-plan/scripts/fixtures/mock-jira-success.sh >/dev/null 2>&1; then
  echo "collect-jira accepted invalid issue key"
  exit 1
fi

completion_validation_root=".agents/runs/sdlc-plan-validation/completion/cases"
completion_run_root=".agents/runs/sdlc-plan-validation/completion/runs"
completion_case="2026-06-04-completion-check"
completion_case_dir="${completion_validation_root}/${completion_case}"
rm -rf "$completion_validation_root" "$completion_run_root"

.agents/sdlc/core/scripts/scaffold-case.sh "$completion_case" \
  --title "Completion Check" \
  --ticket TEST-1 \
  --root "$completion_validation_root" \
  --stage-template-root .agents/skills/sdlc-plan/assets/templates >/dev/null

python3 .agents/sdlc/core/scripts/validate-metadata-schema.py \
  "$completion_case_dir/metadata.yaml" \
  .agents/sdlc/core/schemas/case-metadata.schema.json \
  --case-id "$completion_case" \
  --stage plan >/dev/null

invalid_root_metadata="${completion_validation_root}/invalid-root-metadata.yaml"
printf -- '- invalid-root\n' > "$invalid_root_metadata"

invalid_root_output="$(
  python3 .agents/sdlc/core/scripts/validate-metadata-schema.py \
    "$invalid_root_metadata" \
    .agents/sdlc/core/schemas/case-metadata.schema.json \
    --case-id "$completion_case" \
    --stage plan 2>&1 || true
)"

if printf '%s\n' "$invalid_root_output" | rg -q "Traceback|AttributeError"; then
  echo "metadata validator crashed on non-object metadata root"
  exit 1
fi

if ! printf '%s\n' "$invalid_root_output" | rg -q "expected object"; then
  echo "metadata validator did not reject non-object metadata root"
  exit 1
fi

.agents/sdlc/core/scripts/validate-case.sh "$completion_case" plan \
  --root "$completion_validation_root" >/dev/null

metadata_drift_case="2026-06-04-metadata-drift"
metadata_drift_dir="${completion_validation_root}/${metadata_drift_case}"
.agents/sdlc/core/scripts/scaffold-case.sh "$metadata_drift_case" \
  --title "Metadata Drift" \
  --ticket TEST-2 \
  --root "$completion_validation_root" \
  --stage-template-root .agents/skills/sdlc-plan/assets/templates >/dev/null

perl -0pi -e '
  s/current_stage: "plan"/current_stage: "design"/;
  s/current_status: "draft"/current_status: "plan-completed"/;
' "$metadata_drift_dir/metadata.yaml"

if .agents/sdlc/core/scripts/validate-case.sh "$metadata_drift_case" plan \
  --root "$completion_validation_root" >/dev/null 2>&1; then
  echo "validate-case accepted metadata drift"
  exit 1
fi

placeholder_case="2026-06-04-placeholder-check"
placeholder_dir="${completion_validation_root}/${placeholder_case}"
.agents/sdlc/core/scripts/scaffold-case.sh "$placeholder_case" \
  --title "Placeholder Check" \
  --ticket TEST-3 \
  --root "$completion_validation_root" \
  --stage-template-root .agents/skills/sdlc-plan/assets/templates >/dev/null

printf '\n-\n' >> "$placeholder_dir/README.md"

if .agents/sdlc/core/scripts/validate-case.sh "$placeholder_case" plan \
  --root "$completion_validation_root" >/dev/null 2>&1; then
  echo "validate-case accepted empty placeholder"
  exit 1
fi

status_copy_case="2026-06-04-status-copy-check"
status_copy_dir="${completion_validation_root}/${status_copy_case}"
.agents/sdlc/core/scripts/scaffold-case.sh "$status_copy_case" \
  --title "Status Copy Check" \
  --ticket TEST-4 \
  --root "$completion_validation_root" \
  --stage-template-root .agents/skills/sdlc-plan/assets/templates >/dev/null

printf '\n- 상태: `draft`\n' >> "$status_copy_dir/README.md"

if .agents/sdlc/core/scripts/validate-case.sh "$status_copy_case" plan \
  --root "$completion_validation_root" >/dev/null 2>&1; then
  echo "validate-case accepted duplicated lifecycle status"
  exit 1
fi

if .agents/sdlc/core/scripts/complete-stage.sh "$completion_case" plan \
  --root "$completion_validation_root" \
  --run-root "$completion_run_root" >/dev/null 2>&1; then
  echo "complete-stage accepted unfinished stage"
  exit 1
fi

unfinished_finish_output="$(
  .agents/sdlc/core/scripts/finish-stage.sh "$completion_case" plan \
    --root "$completion_validation_root" \
    --run-root "$completion_run_root" 2>&1 || true
)"

if ! printf '%s\n' "$unfinished_finish_output" | rg -q "마무리 점검|보완"; then
  echo "finish-stage did not present user-facing unfinished output"
  exit 1
fi

if printf '%s\n' "$unfinished_finish_output" | \
  rg -qi "hard gate|semantic gate|semantic[- ]review|finalize|needs-semantic-review|completion_decision"; then
  echo "finish-stage exposed internal gate terms"
  exit 1
fi

perl -0pi -e '
  s/^- $/- 없음/gm;
  s/- 아직 시작하지 않음\./- 완료 검증 스크립트의 동작을 확인한다./g;
  s/- 문제: 아직 정리하지 않음\./- 문제: 완료 검증 스크립트의 동작을 확인한다./g;
  s/- 목표: 아직 정리하지 않음\./- 목표: 완료 전 검증 흐름을 확인한다./g;
  s/- 포함 범위: 아직 정리하지 않음\./- 포함 범위: 문서 완료 검증 흐름으로 한정한다./g;
  s/- PR 경계 판단: 아직 정리하지 않음\./- PR 경계 판단: 하나의 trunk-based PR로 review 가능한 범위다./g;
  s/- 추천 방향: 아직 정리하지 않음\./- 추천 방향: 단계 완료 전 검증을 통과해야 한다./g;
  s/- 기대효과: 아직 정리하지 않음\./- 기대효과: 미완료 산출물의 조기 완료를 막는다./g;
  s/- 제외 범위: 아직 정리하지 않음\./- 제외 범위: 제품 소스 수정은 포함하지 않는다./g;
  s/- 현재 단계 산출물을 작성한다\./- 다음 단계로 넘어갈 준비를 마친다./g;
' \
  "$completion_case_dir/README.md" \
  "$completion_case_dir/plan/result.md" \
  "$completion_case_dir/plan/handoff.md"

perl -0pi -e '
  s/^- 작성일: 없음$/- 작성일: `2026-06-04`/gm;
' \
  "$completion_case_dir/README.md" \
  "$completion_case_dir/plan/result.md"

.agents/sdlc/core/scripts/complete-stage.sh "$completion_case" plan \
  --root "$completion_validation_root" \
  --run-root "$completion_run_root" >/dev/null

ready_finish_output="$(
  .agents/sdlc/core/scripts/finish-stage.sh "$completion_case" plan \
    --root "$completion_validation_root" \
    --run-root "$completion_run_root"
)"

if ! printf '%s\n' "$ready_finish_output" | rg -q "내용 검토|점검 기록"; then
  echo "finish-stage did not trigger user-facing content review"
  exit 1
fi

if printf '%s\n' "$ready_finish_output" | \
  rg -qi "hard gate|semantic gate|semantic[- ]review|finalize|needs-semantic-review|completion_decision"; then
  echo "finish-stage exposed internal gate terms for ready stage"
  exit 1
fi

semantic_review_file="${completion_run_root}/${completion_case}/plan-semantic-review.md"
test -s "$semantic_review_file"

if rg -n 'current_status: "completed"' \
  "$completion_case_dir/metadata.yaml" >/dev/null; then
  echo "complete-stage finalized before semantic review"
  exit 1
fi

if .agents/sdlc/core/scripts/finalize-stage.sh "$completion_case" plan \
  --root "$completion_validation_root" \
  --run-root "$completion_run_root" \
  --review "$semantic_review_file" >/dev/null 2>&1; then
  echo "finalize-stage accepted pending semantic review"
  exit 1
fi

perl -0pi -e 's/completion_decision: pending/completion_decision: pass/' \
  "$semantic_review_file"

perl -0pi -e '
  s/^- Case ID:$/- Case ID: `2026-06-04-completion-check`/gm;
  s/^- Stage:$/- Stage: `plan`/gm;
  s/^- 작성 시각:$/- 작성 시각: `2026-06-04T00:00:00Z`/gm;
  s/^- $/- 없음/gm;
' "$semantic_review_file"

finalize_output="$(
  .agents/sdlc/core/scripts/finalize-stage.sh "$completion_case" plan \
    --root "$completion_validation_root" \
    --run-root "$completion_run_root" \
    --review "$semantic_review_file"
)"

if ! printf '%s\n' "$finalize_output" | rg -q 'Next stage: `design`'; then
  echo "finalize-stage did not report the immediate next stage"
  exit 1
fi

rg -n 'current_stage: "design"|current_status: "draft"|next_stage: "build"' \
  "$completion_case_dir/metadata.yaml" >/dev/null
rg -n '^[[:space:]]{2}plan: "completed"$' \
  "$completion_case_dir/metadata.yaml" >/dev/null
rg -n '^[[:space:]]{2}design: "draft"$' \
  "$completion_case_dir/metadata.yaml" >/dev/null

.agents/sdlc/core/scripts/validate-case.sh "$completion_case" design \
  --root "$completion_validation_root" >/dev/null

legacy_pattern="\\.ai-native|planning-index|task-decomposition"
legacy_pattern="${legacy_pattern}|planning-orchestrator|sdlc-planning-orchestrator"
legacy_roots=(.agents .codex .claude docs/plans)
if rg -n --glob '!**/validate-sdlc-plan.sh' "$legacy_pattern" "${legacy_roots[@]}" >/dev/null; then
  echo "legacy term found"
  rg -n --glob '!**/validate-sdlc-plan.sh' "$legacy_pattern" "${legacy_roots[@]}"
  exit 1
fi

echo "sdlc-plan scaffold is valid"
