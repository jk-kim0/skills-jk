---
name: sdlc-plan
description: Run the shared AI Native SDLC planning workflow and write planning artifacts in Korean.
---

# SDLC Plan Command Adapter

Use the `sdlc-plan` skill.

Read `.agents/skills/sdlc-plan/SKILL.md` first.

Treat `.agents/skills/sdlc-plan` as the canonical source for the plan stage.

Treat `.agents/sdlc/core` as the shared source for SDLC stage rules, scripts, schemas, and common
templates.

Do not create approved case files before the user approves the `계획 준비 요약`.

If 자료가 부족하면 공식 case 생성 전에 한 가지 질문으로 보충합니다.

Read `.agents/sdlc/core/references/case-structure.md`,
`.agents/sdlc/core/references/stage-workflow.md`, and
`.agents/sdlc/core/references/stage-contracts.md`.

Read `references/source-adapters.md` before external source collection.

Read `.agents/sdlc/core/references/document-quality.md` before writing SDLC artifacts.

Use `.agents/sdlc/core/scripts/scaffold-case.sh` for approved case creation with
`--stage-template-root .agents/skills/sdlc-plan/assets/templates`.

Use `.agents/sdlc/core/scripts/prepare-stage.sh <case-id> plan` before writing plan outputs.

Read `.agents/sdlc/core/references/stage-finish.md` when the user wants to finish the plan stage.

Use `.agents/sdlc/core/scripts/finish-stage.sh <case-id> plan` as the user-facing finish entry point.

If content review is needed, read `assets/prompts/stage-content-review.md`.

Write the review according to `.agents/sdlc/core/references/completion-review.md`.

Run the internal finalize script only when content review allows completion.

Use `.agents/sdlc/core/scripts/validate-case.sh <case-id> plan` before finishing.

Use `.agents/sdlc/core/scripts/validate-document-quality.sh` on generated SDLC documents before
finalizing.

Use `.agents/sdlc/core/scripts/format-document-quality.sh` only when the user asks to auto-format
artifacts.

Read `references/agent-invocation.md` before worker role collection.

Ask for 별도 역할 Agent 검토 inside the preparation summary. If it is not approved or unavailable,
continue with 기본 검토 in the same session.

Use `.claude/agents/sdlc-*.md` for selected worker roles only after brief files exist and the user
has approved worker-agent collection.

If native subagents are unavailable, use same-session role review and record that method.

Keep temporary run artifacts under `.agents/runs/sdlc-plan/<run-id>/`.

Write approved case documents under `.sdlc/cases/<yyyy-mm-dd-name>/`.

사용자 응답과 planning 산출물은 기본적으로 한국어로 작성합니다.

코드, 경로, 명령어, ticket ID, API 이름, 제품명, role id는 원문을 유지합니다.

Do not edit product source code during planning.

Agents recommend. Humans decide.

사용자에게 내부 검사 이름을 먼저 노출하지 않습니다.
