---
name: sdlc-build
description: Use when implementing an approved SDLC design and producing build artifacts.
---

# SDLC Build

Use this skill to run the AI Native SDLC build step.

The build step turns `design` decisions and `build/tasks.md` into scoped source changes,
verification evidence, and a test-stage handoff. Unlike `plan` and `design`, production source
edits are expected when they are required by the approved build tasks.

## Quick Start

1. Identify the approved case id and confirm the case is in or ready for `build`.
2. Read `references/workflow.md`, `references/agent-routing.md`,
   `.agents/sdlc/core/references/stage-workflow.md`,
   `.agents/sdlc/core/references/stage-contracts.md`,
   `.agents/sdlc/core/references/stage-backtrack.md`,
   `.agents/sdlc/core/references/output-contracts.md`, and
   `.agents/sdlc/core/references/document-quality.md`.
3. Run `.agents/sdlc/core/scripts/prepare-stage.sh <case-id> build`.
4. Read the documents listed under `반드시 읽을 문서`.
5. Read `references/user-guide.md` when the user asks how to start, scope, or finish build work.
6. Read source files, tests, local docs, generated contracts, and `evidence.md` only when needed
   to implement or verify the approved tasks.
7. Execute `build/tasks.md` in dependency order unless a safer local order is required.
8. Preserve the design contract. If implementation proves the design wrong, stop and ask whether
   to run a design backtrack instead of silently changing scope.
9. Use `references/agent-routing.md` to pick role perspectives such as backend, frontend, core,
   infrastructure, QA, security/risk, and release.
10. Use same-session role review by default. Request native worker agents only when matching
    adapters exist and the user explicitly approves.
11. Keep implementation changes scoped to the approved case PR boundary.
12. Record changed files, task completion, verification commands, skipped checks, and remaining
    risks in `build/result.md`.
13. Write `build/handoff.md` for the test stage.
14. Update root case documents when build decisions or open decisions change.
15. If the user asks to finish, read `.agents/sdlc/core/references/stage-finish.md`.
16. Run `.agents/sdlc/core/scripts/finish-stage.sh <case-id> build` and follow its next action.
17. If content review is needed, read `assets/prompts/stage-content-review.md`.
18. Write the review file using `.agents/sdlc/core/references/completion-review.md`.
19. Run the internal finalize script only when content review allows completion.
20. Run `.agents/sdlc/core/scripts/validate-case.sh <case-id> build` before finishing.

## Build Responsibilities

Build must leave enough evidence for test and review to proceed without chat history.

- implemented task units and task-to-change trace
- changed files and behavioral impact
- preserved design decisions and any deviations
- verification commands, results, and skipped checks
- regression areas for test stage
- known risks, rollback concerns, and release notes candidates
- diff-ready changeset and PR message candidates when requested
- exclusions and work intentionally left out

## Build Rules

- Treat `design/result.md`, `design/handoff.md`, and `build/tasks.md` as the build contract.
- Do not redefine the case goal, product scope, or PR boundary.
- Do not add unrelated refactors, dependency upgrades, formatting churn, or new features.
- Use `AGENTS.md`, tests, linters, and build errors as feedback loops during implementation.
- If a task is blocked by missing product or architecture input, record it as a build blocker and
  ask the user.
- If a task requires changing the approved design, record the proposed backtrack and ask before
  proceeding.
- If tests cannot run, record the exact reason and the residual risk.
- Keep runtime exploration artifacts under `.agents/runs/sdlc-build/<case-id>/`.
- Do not require `.agents/runs/` files as mandatory input for later stages.

## Language Rules

Write user-facing responses and generated build artifacts in Korean (`한국어`) by default.

Keep code, file paths, commands, ticket IDs, API names, product names, role ids, and technology
names in their original form.

## Storage Rules

Temporary build exploration artifacts go under `.agents/runs/sdlc-build/<case-id>/`.

Approved case documents go under `.sdlc/cases/<case-id>/`.

Lifecycle status is stored only in `metadata.yaml`. Do not duplicate current stage or status values
in `README.md` or stage Markdown files.

## Safety Rules

Agents implement within the approved contract. Humans decide scope changes.

Production source edits are allowed only when they trace to `build/tasks.md` or confirmed build
decisions.

Use core `finish-stage.sh` before declaring a stage complete.

For user requests, say `마무리 점검`, `보완 필요`, `진행 승인 필요`, or `마무리 완료`.

Do not expose internal check names unless the user asks how the checks work.
