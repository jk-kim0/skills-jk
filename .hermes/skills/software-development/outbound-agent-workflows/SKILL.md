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
4. When authoring or updating `docs/` or `openspec/` documents, write body sentences in Korean. English is acceptable for technical terms, UI terms, software engineering terms, and filenames; choose filenames in clear, correct English.
5. Avoid broad local full builds by default; prefer focused tests, `git diff --check`, targeted lint/typecheck when touched files demand it, and CI monitoring.
5. Do not leak secrets in chat, docs, PR bodies, logs, screenshots, or skills.
6. For PR bodies containing backticks or commands, write a temporary body file and use `gh pr create/edit --body-file`.

## Workflow Routes

### Development environment operations

For Dev Vercel/Incheon and Tencent Seoul/Tokyo deploy/migrate/reset/schema/smoke work, use the class-level flow in `development-environment-ops` plus Outbound-specific details in `references/outbound-agent-dev-environment-operations.md`.
For Vercel/Next.js runtime 500s involving `ERR_REQUIRE_ESM`, `___next_launcher.cjs`, package-wide `"type": "module"`, or “which PR broke the previously working deployment?” forensics, also use `references/vercel-nextjs-esm-runtime-incident-forensics.md`.

Important reminders:

- Establish the latest stable `origin/main` SHA before claiming latest deployment.
- Prefer migrate-only before reset unless reset was explicitly requested.
- Verify exact deployed version separately from public `/login` health.
- Pair workflow/job evidence with VM/Vercel metadata and runtime smoke.
- When naming a deployment incident culprit, identify the first PR/deployment where live HTTP behavior changed from healthy to failing; separately label older latent preconditions so the user does not receive the wrong “범인 PR”.
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
When a docs/OpenSpec PR already records the accepted contract and the user asks for the implied code follow-up, use `references/docs-contract-followup-implementation-pr.md` to implement the exact checklist items and create a stacked implementation PR when the docs PR is still open.
When the user asks whether a PR's “계약/명세” and implementation match, treat it as a contract-vs-implementation audit: inspect the PR body/diff, the landed `origin/main` implementation if the PR is merged, the canonical docs/OpenSpec requirements, and the focused tests that prove the contract. Report separately (1) the PR's direct changed contract, (2) broader feature contracts the PR references, (3) actual code/schema/route/test evidence, and (4) explicit partial/backlog boundaries so docs wording is not overstated as shipped behavior.

Important reminders:

- Keep feature plans docs-only unless implementation is explicitly requested.
- Record Product Owner decisions in the active plan/OpenSpec surfaces and sweep stale opposite assumptions.
- Separate app auth policy from external provider platform constraints.
- Keep credential-reference design clear: public fields in config, secrets in approved secret sources, dry-run/apply boundaries for CLI work.
- For docs-contract follow-up implementation, mark only the completed implementation tasks in `openspec/changes/**/tasks.md`; leave live smoke/deploy tasks open unless actually run.
- For auth/SSO contract audits, distinguish Google SSO minimum implementation from username/password email-verification backlog language; do not label a backlog/future-scope clause as a blocker unless the active contract says it is required now.

### Agent PR creation workflow

When the user asks to add or maintain an AI Agent-only PR creation workflow for this repository, use `references/agent-pr-creation-workflow.md`. Follow the `skills-jk` `.github/workflows/create-pr.yml` pattern, then adapt it with Outbound Agent safeguards: source/base validation, no-diff rejection, duplicate open PR detection, `gh pr create --body-file`, narrow `pull-requests: write` permissions, `actionlint`, and `git diff --check`.

### OpenSpec documentation PR rebase conflicts

When rebasing Outbound Agent docs/OpenSpec PRs and conflicts appear in bridge documents or broad model contracts, use `references/outbound-agent-openspec-doc-pr-rebase-conflicts.md`. Preserve latest `main` bridge architecture and add only the PR's still-valid active spec pointers/payload instead of resurrecting obsolete long-form duplicate requirements.
If the conflict is a modify/delete on an OpenSpec file that latest `main` intentionally removed or split, also use `references/open-pr-rebase-openspec-deleted-spec-conflicts.md`: keep the latest-main deletion unless the PR explicitly restores that canonical spec, and preserve only the PR's still-valid payload in surviving specs/change files.

### Existing UI feature to OpenSpec documentation

When the user asks to document an already-implemented Front App UI/debug behavior in `openspec/`, use `references/outbound-agent-existing-ui-feature-to-openspec.md`.

Important reminders:

- Inspect the current implementation and source-level tests before writing the spec.
- Inspect `openspec/README.md`, `openspec/specs/README.md`, `openspec/project.md`, and candidate existing specs before creating a new spec.
- Before choosing or creating an OpenSpec spec id, read `openspec/README.md` for the current prefix taxonomy.
- Do not create new `platform-*` specs; Outbound Agent treats `platform-*` as a deprecated legacy prefix. Existing `platform-*` specs may still be extended when they are the current canonical home, but new or reorganized foundation behavior should prefer more specific `contract-*`, `integration-*`, `policy-*`, `ops-*`, `ui-*`, or `entity-*` specs according to the README.
- Convert behavior into explicit Requirements and GIVEN/WHEN/THEN Scenarios; split controls/shortcuts, marker authoring, visibility/collection, interaction/copy behavior, and environment availability when needed.
- Keep the change docs-only unless the user explicitly asks for implementation, and verify with `git diff --check` plus lightweight Markdown/OpenSpec structure checks when no validator exists.

### Chrome browser E2E OpenSpec for SSO and email sending

When the user asks for an OpenSpec/specification for Chrome Browser E2E coverage that spans Google SSO, Email Sender OAuth/configuration, test send, and actual send, use `references/outbound-agent-chrome-e2e-openspec.md`.

Important reminders:

- Treat the request as docs-only unless implementation is explicitly requested.
- Use a repo-local `.worktrees/` worktree and create an OpenSpec change under `openspec/changes/<change-id>/` with `proposal.md`, `tasks.md`, and a `uc-*` spec for the browser journey.
- Stage the journey into reusable test steps, then add a full-suite composition requirement that runs those stages in order.
- Explicitly separate Google SSO login from Gmail sender OAuth; SSO session creation must not imply sender authorization.
- Do not record or echo Google account credentials, OAuth client secrets, tokens, authorization codes, cookies, or passwords; specify secret-source/runtime-reference inputs only.
- Distinguish test send evidence from actual send evidence, and gate real provider side effects in CI behind explicit enable/manual approval.

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
- For docs/OpenSpec edits, assuming a file is missing because the root checkout is behind `origin/main`; first fetch and inspect `origin/main` or create a fresh `.worktrees/` worktree from `origin/main` before deciding the spec does not exist.
- When consolidating OpenSpec guidance from `openspec/specs/README.md` into `openspec/README.md`, do not copy stale inventory-local rules verbatim. Treat `openspec/README.md` as the canonical taxonomy, reconcile deprecated prefixes such as `platform-*`, and leave `openspec/specs/README.md` as inventory plus a canonical-link pointer to avoid future drift.
- Leaving PR-body scratch files under repo-local `.hermes`/`.agents` symlinked runtime paths after `gh pr create/edit`; clean temporary residue before final status.
- Treating public `/login` 200 as exact deploy proof.
- Running provider side effects before schema/runtime readiness.
- Letting docs/OpenSpec drift after UI or auth decision changes.
- Using root checkout for edits when the repo expects worktrees.
- Preserving old UI copy/tests that contradict the user's latest design direction.
- Printing OAuth, DB, provider, GitHub, Vercel, or VM secrets while debugging.
- During cleanup or PR preservation of credential/OAuth/runtime-secret changes, scan added lines for secret-like values before committing; public IDs and secret reference metadata can be documented, but raw secret values must not enter git history, PR bodies, or final reports.

## Verification Checklist

- [ ] `AGENTS.md`/repo guidance and current source/docs were checked.
- [ ] Correct workflow route and supporting reference were used.
- [ ] Worktree, branch, PR, and CI/deploy evidence are reported when applicable.
- [ ] Focused verification matches touched surfaces.
- [ ] Secrets stayed redacted.
- [ ] Relevant generic skills were consulted for cross-cutting work such as dropdown UI, OpenSpec decisions, domain models, or environment ops.
