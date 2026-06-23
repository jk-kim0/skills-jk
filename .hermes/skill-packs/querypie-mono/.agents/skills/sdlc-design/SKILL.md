---
name: sdlc-design
description: Use when turning an approved SDLC plan into technical design and build handoff.
---

# SDLC Design

Use this skill to run the AI Native SDLC design step.

The design step turns `plan` decisions and open questions into technical contracts, architecture
choices, area-specific design notes, and build-ready task units. It is not the default place to
edit production source code.

## Quick Start

1. Identify the approved case id and confirm the case is in or ready for `design`.
2. Read `references/workflow.md`, `references/task-model.md`, `references/agent-routing.md`,
   `.agents/sdlc/core/references/stage-workflow.md`,
   `.agents/sdlc/core/references/stage-contracts.md`,
   `.agents/sdlc/core/references/stage-backtrack.md`,
   `.agents/sdlc/core/references/output-contracts.md`, and
   `.agents/sdlc/core/references/document-quality.md`.
3. Run `.agents/sdlc/core/scripts/prepare-stage.sh <case-id> design`.
4. Read the documents listed under `반드시 읽을 문서`.
5. Read `evidence.md`, related docs, source files, design system docs, or UI references only when
   needed to answer design questions.
6. Use `references/agent-routing.md` to pick role perspectives such as backend, frontend, core,
   infrastructure, QA, security/risk, and release.
7. Ask for explicit user approval before requesting native worker agents. If unavailable, use
   same-session role review and record that method.
8. Separate `Delegate`, `Review`, and `Own` responsibilities:
   - Agents may draft prototypes, component maps, boilerplate sketches, alternatives, and edge
     cases.
   - The team reviews conventions, accessibility, integration, reliability, and quality.
   - Humans own design system rules, UX direction, architecture decisions, and final tradeoffs.
9. Explain the difference between `case` and `task` before creating build tasks.
10. Derive build tasks only from case goals, plan handoff, and confirmed design decisions.
11. Classify open decisions as blockers, build-handoff decisions, case-wide decisions, or concerns.
12. If this is a backtrack, close only the approved backtrack question unless the user expands
    scope.
13. Write `design/result.md`, `design/handoff.md`, and `build/tasks.md`.
14. Update root case documents when design decisions or open decisions change.
15. If the user asks to finish, read `.agents/sdlc/core/references/stage-finish.md`.
16. Run `.agents/sdlc/core/scripts/finish-stage.sh <case-id> design` and follow its next action.
17. If content review is needed, read `assets/prompts/stage-content-review.md`.
18. Write the review file using `.agents/sdlc/core/references/completion-review.md`.
19. Run the internal finalize script only when content review allows completion.
20. Run `.agents/sdlc/core/scripts/validate-case.sh <case-id> design` before finishing.

## Design Responsibilities

Design must answer enough questions for build to start without chat history.

- technical direction and rejected alternatives
- domain, API, UI, data, infrastructure, security, and release boundaries
- interface contracts, data flow, control flow, error handling, and observability
- prototype findings, if any, clearly separated from final decisions
- build task units, dependencies, and exclusions
- test and review expectations that build must preserve

## Case and Task Rules

Read `references/task-model.md` before writing `build/tasks.md`.

In short:

- A `case` is the approved SDLC container for the problem, goal, scope, evidence, decisions, and
  lifecycle.
- A `task` is a build-stage execution unit derived from design decisions inside one case.

One case may produce many tasks. A task must not redefine the case goal or reopen product scope.

## Language Rules

Write user-facing responses and generated design artifacts in Korean (`한국어`) by default.

Keep code, file paths, commands, ticket IDs, API names, product names, role ids, and technology
names in their original form.

## Storage Rules

Temporary design exploration artifacts go under `.agents/runs/sdlc-design/<case-id>/`.

Approved case documents go under `.sdlc/cases/<case-id>/`.

Do not require `.agents/runs/` files as mandatory input for the next stage. Promote useful
findings into approved case documents.

## Safety Rules

Agents recommend. Humans decide.

Production source edits are not part of the default design step. If a prototype or scaffold is
needed for validation, keep it in runtime artifacts or ask the user before touching product source.

Lifecycle status is stored only in `metadata.yaml`. Do not duplicate current stage or status values
in `README.md` or stage Markdown files.

Use core `finish-stage.sh` before declaring a stage complete.

For user requests, say `마무리 점검`, `보완 필요`, `진행 승인 필요`, or `마무리 완료`.

Do not expose internal check names unless the user asks how the checks work.
