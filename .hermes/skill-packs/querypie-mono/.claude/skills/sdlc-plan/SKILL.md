---
name: sdlc-plan
description: Use for AI Native SDLC planning. Write responses and artifacts in Korean.
---

# SDLC Plan Adapter

Read `.agents/skills/sdlc-plan/SKILL.md` and follow it as the canonical workflow.

Use `.agents/skills/sdlc-plan` for plan-specific files.

Use `.agents/sdlc/core` for shared SDLC rules, scripts, schemas, and templates.

Do not create approved case files before the user approves the `계획 준비 요약`.

If 자료가 부족하면 공식 case 생성 전에 한 가지 질문으로 보충합니다.

Read `.agents/sdlc/core/references/case-structure.md`,
`.agents/sdlc/core/references/stage-workflow.md`, and
`.agents/sdlc/core/references/stage-contracts.md` before writing approved case documents.

Read `references/source-adapters.md` before collecting Jira, Slack, GitHub, or other external
source evidence.

Read `.agents/sdlc/core/references/document-quality.md` before writing SDLC artifacts.

Run `.agents/sdlc/core/scripts/prepare-stage.sh <case-id> <stage>` at the start of each SDLC stage.

Run `.agents/sdlc/core/scripts/validate-case.sh <case-id> <stage>` before finishing stage work.

Run `.agents/sdlc/core/scripts/validate-document-quality.sh` on generated SDLC documents before
finalizing.

Run `.agents/sdlc/core/scripts/format-document-quality.sh` only when the user asks to auto-format
artifacts.

If the user expresses stage completion intent, read `.agents/sdlc/core/references/stage-finish.md`,
then run `.agents/sdlc/core/scripts/finish-stage.sh <case-id> <stage>`.

If content review is needed, read `assets/prompts/stage-content-review.md`.

Write the review according to `.agents/sdlc/core/references/completion-review.md`.

Run the internal finalize script only when content review allows completion.

Read `references/agent-invocation.md` before worker role collection.

Ask for 별도 역할 Agent 검토 inside the preparation summary. If it is not approved or unavailable,
continue with 기본 검토 in the same session.

Use `.claude/agents/sdlc-*.md` only as Claude Code runtime adapters for worker roles after user
approval.

If native subagents are unavailable, use same-session role review and record that method.

사용자 응답과 planning 산출물은 기본적으로 한국어로 작성합니다.

코드, 경로, 명령어, ticket ID, API 이름, 제품명, role id는 원문을 유지합니다.

Do not edit product source code during planning.

Agents recommend. Humans decide.

Chat history is not official state. Record important decisions in case files.

사용자에게 내부 검사 이름을 먼저 노출하지 않습니다.
