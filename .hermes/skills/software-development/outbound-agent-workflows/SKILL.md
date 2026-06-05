---
name: outbound-agent-workflows
description: Use when working in querypie/outbound-agent across environment operations, frontend UI changes, provider smoke tests, auth/SSO/OAuth feature planning, and repo-specific PR workflows.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [outbound-agent, nextjs, dev-environments, frontend, oauth, provider-smoke, auth, openspec, pull-requests]
    related_skills: [development-environment-ops, dropdown-overlay-interaction-design, openspec-decision-management, domain-model-design-docs]
---

# Outbound Agent Workflows

## Overview

Use this umbrella skill whenever the task is in `querypie/outbound-agent`. It routes recurring Outbound Agent work across four major classes: development environment operations, front-end UI implementation/review, live provider/OAuth smoke, and auth/SSO/OAuth feature planning.

Keep this `SKILL.md` as a class-level entry point and move detailed session-specific runbooks, environment maps, UI conflict recipes, provider smoke notes, and feature-plan decision tables into `references/`.

## When to Use

- The repository, issue, PR, deployment, or feature is `querypie/outbound-agent`.
- The user asks about Dev Vercel/Incheon, Tencent Seoul/Tokyo, migrations, schema checks, resets, deploys, runtime smoke, or development environment readiness.
- The user asks for frontend/UI work in the Next.js App Router app, App Shell, Sidebar, top-bar, dropdown menus, Entity Cards, settings/profile UI, or UI PR evidence.
- The user asks to run or plan Gmail/provider OAuth connection, actual-send smoke, sender identity readiness, or provider evidence updates.
- The user asks to plan/document auth, Google SSO, account linking, System Settings access, OAuth boundary decisions, credential references, or Secret Manager/1Password runtime credential workflows.

## Repository Defaults

1. Use a repo-local `.worktrees/<topic>` worktree for file changes unless the user or repo guidance explicitly says otherwise.
2. Read `AGENTS.md` and the current source/docs before implementing from old issue or PR text.
3. Use Korean PR titles/bodies for this repo unless directed otherwise.
4. Avoid broad local full builds by default; prefer focused tests, `git diff --check`, targeted lint/typecheck when touched files demand it, and CI monitoring.
5. Do not leak secrets in chat, docs, PR bodies, logs, screenshots, or skills.
6. For PR bodies containing backticks or commands, write a temporary body file and use `gh pr create/edit --body-file`.

## Workflow Routes

### Development environment operations

For Dev Vercel/Incheon and Tencent Seoul/Tokyo deploy/migrate/reset/schema/smoke work, use the class-level flow in `development-environment-ops` plus Outbound-specific details in `references/outbound-agent-dev-environment-operations.md`.

Important reminders:

- Establish the latest stable `origin/main` SHA before claiming latest deployment.
- Prefer migrate-only before reset unless reset was explicitly requested.
- Verify exact deployed version separately from public `/login` health.
- Pair workflow/job evidence with VM/Vercel metadata and runtime smoke.
- Report progress visibly for mutating or long-running environment operations.

### Frontend UI workflow

For App Shell, top-bar, Sidebar, dropdown, Entity Card, settings/profile, docs/UI alignment, screenshots, or UI PRs, use `references/outbound-agent-front-ui-workflow.md` and related generic UI skills such as `dropdown-overlay-interaction-design`.

Important reminders:

- Ground UI work in canonical `docs/ui/**`, OpenSpec/design docs, and current landed implementation.
- Keep browser-only APIs in client components.
- Reuse shared class tokens and add source-level structure tests for order/placement/absence contracts.
- Include a required `UI 변경` section in UI PRs with checkable URI paths.

### Provider and OAuth smoke

For Gmail OAuth, provider credential storage, actual-send smoke, sender identity readiness, or provider evidence, use `references/outbound-agent-provider-smoke.md` and any OAuth environment details under `development-environment-ops`.

Important reminders:

- Confirm code deployment, migration/schema readiness, and target environment before provider side effects.
- Use the smallest real provider side effect first.
- Record safe evidence only: route, environment, row existence/status, redacted IDs, provider message/thread ID presence when safe.
- Distinguish OAuth start, callback token exchange, credential persistence, and actual provider send evidence.

### Auth / SSO / OAuth feature planning

For Google SSO, account linking, System Settings access, OAuth config boundary, credential-reference CLI, or Secret Manager plans, use `references/outbound-auth-feature-planning.md` plus `openspec-decision-management` and `domain-model-design-docs` where the decision affects durable specs or model contracts.

Important reminders:

- Keep feature plans docs-only unless implementation is explicitly requested.
- Record Product Owner decisions in the active plan/OpenSpec surfaces and sweep stale opposite assumptions.
- Separate app auth policy from external provider platform constraints.
- Keep credential-reference design clear: public fields in config, secrets in approved secret sources, dry-run/apply boundaries for CLI work.

### Existing UI feature to OpenSpec documentation

When the user asks to document an already-implemented Front App UI/debug behavior in `openspec/`, use `references/outbound-agent-existing-ui-feature-to-openspec.md`.

Important reminders:

- Inspect the current implementation and source-level tests before writing the spec.
- Inspect `openspec/README.md`, `openspec/specs/README.md`, `openspec/project.md`, and candidate existing specs before creating a new spec.
- Prefer extending the existing canonical `platform-*` or `contract-*` spec over creating a narrow one-off spec when the behavior is part of foundation behavior.
- Convert behavior into explicit Requirements and GIVEN/WHEN/THEN Scenarios; split controls/shortcuts, marker authoring, visibility/collection, interaction/copy behavior, and environment availability when needed.
- Keep the change docs-only unless the user explicitly asks for implementation, and verify with `git diff --check` plus lightweight Markdown/OpenSpec structure checks when no validator exists.

## Reporting Pattern

For Outbound Agent work, report:

1. Repository/worktree/branch and whether files were changed.
2. Which workflow route(s) applied.
3. Key evidence handles: PR URL, workflow run IDs, deployment IDs, target SHA, smoke result, or doc paths.
4. Verification performed and skipped, with reason.
5. Secret-safety statement when OAuth/provider/runtime credential work was involved.
6. Current CI/deploy state if a PR or environment operation was created.

## Common Pitfalls

- Implementing from stale PR/issue text instead of latest `main`.
- Treating public `/login` 200 as exact deploy proof.
- Running provider side effects before schema/runtime readiness.
- Letting docs/OpenSpec drift after UI or auth decision changes.
- Using root checkout for edits when the repo expects worktrees.
- Preserving old UI copy/tests that contradict the user's latest design direction.
- Printing OAuth, DB, provider, GitHub, Vercel, or VM secrets while debugging.

## Verification Checklist

- [ ] `AGENTS.md`/repo guidance and current source/docs were checked.
- [ ] Correct workflow route and supporting reference were used.
- [ ] Worktree, branch, PR, and CI/deploy evidence are reported when applicable.
- [ ] Focused verification matches touched surfaces.
- [ ] Secrets stayed redacted.
- [ ] Relevant generic skills were consulted for cross-cutting work such as dropdown UI, OpenSpec decisions, domain models, or environment ops.
