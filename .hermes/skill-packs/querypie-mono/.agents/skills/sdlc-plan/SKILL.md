---
name: sdlc-plan
description: Use when planning AI Native SDLC work from ideas, tickets, issues, chats, or triage.
---

# SDLC Plan

Use this skill to run the AI Native SDLC planning step.

The planning step is not a code-writing step. It turns incomplete ideas, external signals, and
repository context into decision-ready planning artifacts.

## Quick Start

1. Identify the starting context from the user request.
2. Read `references/workflow.md`, `references/agent-invocation.md`,
   `.agents/sdlc/core/references/stage-workflow.md`, and
   `.agents/sdlc/core/references/stage-contracts.md`.
3. Read `references/source-adapters.md`, then collect obvious Jira, Slack, GitHub, spec, document,
   code, and previous-case evidence.
4. If 자료가 부족하면 공식 case 생성 전에 한 가지 질문으로 보충한다.
5. If enough context exists, present a `계획 준비 요약` before creating case files.
6. In the summary, show the case candidate, input status, 검토 방식, and 승인 요청.
7. Ask whether to use 별도 역할 Agent. If not approved or unavailable, use 기본 검토.
8. Create an approved case only after 사용자 승인 of the preparation summary.
9. Use `.agents/sdlc/core/scripts/scaffold-case.sh` with
   `--stage-template-root .agents/skills/sdlc-plan/assets/templates` when creating the approved
   case directory.
10. Use `.agents/sdlc/core/scripts/prepare-stage.sh <case-id> plan` before writing plan outputs.
11. Build an idea draft from human input, evidence, and role perspectives.
12. Run the planning conversation as a brainstorming loop.
13. Use `references/agent-routing.md` to select worker roles.
14. Use `references/agent-invocation.md` before native agents or same-session role review.
15. Use `references/case-splitting.md` when the idea is too large.
16. Use `.agents/sdlc/core/references/output-contracts.md`,
   `.agents/sdlc/core/references/document-quality.md`, and `assets/templates`.
17. Checkpoint important decisions into files. Do not rely on chat history.
18. When the user wants to finish the stage, read `.agents/sdlc/core/references/stage-finish.md`.
19. Run `.agents/sdlc/core/scripts/finish-stage.sh <case-id> plan` and follow its next action.
20. If content review is needed, read `assets/prompts/stage-content-review.md`.
21. Write the review file with `.agents/sdlc/core/references/completion-review.md`.
22. Run the internal finalize script only when content review allows completion.
23. Run `.agents/sdlc/core/scripts/validate-case.sh <case-id> plan` before finishing a case.

When explaining the workflow to users, read `references/user-guide.md`.

## Starting Contexts

Treat these as input shapes, not command subtypes:

- known seed such as an idea, Jira ticket, Slack thread, GitHub issue, or repo link
- broad discovery question about complaints or opportunities
- human idea that needs validation against evidence
- topic that needs decision context before planning
- group of candidate work items that needs triage
- candidate that should become a planning session

If the starting context is unclear, ask one short question before collecting broad evidence.

If the context is clear enough to inspect sources, collect evidence first and then show a planning
preparation summary. Do not create approved case files just because a ticket key exists.

## Language Rules

Write user-facing responses in Korean (`한국어`) by default.

Write all generated planning artifacts in Korean (`한국어`), including case documents, stage
results, handoffs, reports, case split proposals, decisions, and checkpoints.

Keep code, file paths, commands, ticket IDs, API names, product names, and role ids in their
original form.

If a source is written in another language, summarize it in Korean and keep only necessary original
terms or short excerpts.

## Runtime Adapters

Codex should use `.codex/agents/sdlc-*.toml` when native worker agents are needed.

Claude Code should enter through `.claude/skills/sdlc-plan/SKILL.md` or
`.claude/commands/sdlc-plan.md`, then use `.claude/agents/sdlc-*.md`.

These files are adapters. Canonical behavior lives in this skill directory.

## Storage Rules

Temporary run artifacts go under `.agents/runs/sdlc-plan/<run-id>/`.

Approved SDLC case documents go under `.sdlc/cases/<yyyy-mm-dd-name>/`.

Approved case files are created only after the user approves the `계획 준비 요약`.

Shared SDLC core lives in `.agents/sdlc/core`.

Approved cases must follow `.agents/sdlc/core/references/case-structure.md`.

Approved case `metadata.yaml` must follow `.agents/sdlc/core/schemas/case-metadata.schema.json`.

Each SDLC stage must follow `.agents/sdlc/core/references/stage-contracts.md`.

Each SDLC stage must follow `.agents/sdlc/core/references/stage-workflow.md`.

Each generated SDLC document must follow `.agents/sdlc/core/references/document-quality.md`.

Product knowledge documents go under `docs/` only after documentation promotion.

## Safety Rules

Planning agents do not edit product source code.

Agents recommend. Humans decide.

Official state is stored in `.sdlc/cases/<case-id>/` root and stage documents.

Lifecycle status is stored only in `metadata.yaml`. Do not duplicate current stage or status values
in `README.md` or stage Markdown files.

Chat history is not official state because sessions can compact or restart.

Use core `prepare-stage.sh` to restore stage context and core `checkpoint-stage.sh` to record
decisions.

Use core `finish-stage.sh` before declaring a stage complete.

Skill activation cannot force native subagents. Ask explicit user approval before requesting worker
agents, then fall back to same-session role review if native agents are unavailable.

Role perspective review is basic planning work. Native worker agents are only one execution method.

For user requests, say `마무리 점검`, `보완 필요`, or `마무리 완료`.

Do not expose internal check names unless the user asks how the checks work.

Use core `validate-document-quality.sh` when checking generated SDLC documents.

Use core `format-document-quality.sh` only when the user wants to auto-format Markdown artifacts.
