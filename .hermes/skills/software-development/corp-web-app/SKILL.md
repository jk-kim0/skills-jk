---
name: corp-web-app
description: Use when working in corp-web-app, especially route-local authoring, contact-us, stage E2E, and sitemap checks; contains migrated repo-specific memory and user preferences.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [repo-context, migrated-memory]
    related_skills: []
---
# Corp Web App

## Overview

This skill is a compact trigger/index for repo-specific context migrated out of `.hermes/memories/MEMORY.md` and `.hermes/memories/USER.md` so global memory stays focused on durable user preferences rather than repository implementation details.

Load this skill before substantial work in the named repository or platform area. The detailed migrated notes are kept in `references/migrated-memory-and-user-context.md`.

## When to Use

- The current task is in or about `corp-web-app`.
- The user asks about prior conventions, repo-specific constraints, route/content policy, migration status, or operational quirks for this area.
- You are about to edit code, documentation, GitHub wiki pages, CI, deployment, or infrastructure connected to this area.

## Required Context

Read `references/migrated-memory-and-user-context.md` after loading this skill. Treat entries from `USER.md` as user preferences/constraints and entries from `MEMORY.md` as repo facts or workflow lessons. If a note is stale when checked against the live repo, update this skill or its reference rather than writing the stale fact back into global memory.

## Task References

- `references/migrated-memory-and-user-context.md` — migrated repo-specific facts and user constraints.
- `references/plans-route-local-compare-table-refactor.md` — notes for refactoring plans/pricing pages from `CompareTable rows/columns` data props to route-local JSX table authoring without visible content changes.
- `references/tailwind-legacy-shared-ui-compatibility.md` — diagnostic and fix pattern for shared components that render differently between `(legacy)` and `(tailwind)` route groups because Tailwind globals intentionally omit legacy tokens/resets.
- `references/blog-mdx-translation-recovery.md` — workflow for filling missing blog MDX locale files from `corp-web-contents` inventory/history without inventing unavailable translations.

## Common Pitfalls

1. Do not copy repo-specific facts back into global memory unless they are broadly reusable across repositories.
2. Do not treat migrated notes as a substitute for live repo verification when code, CI, routes, or deployment state may have changed.
3. Keep new findings in this skill or a more specific existing skill for the repo/workflow.
4. For route-local locale/product metadata follow-ups, do not over-generalize locale-specific `generateMetadata` helpers by accepting a caller-supplied path such as `urlPath?: string` unless the file is genuinely shared across routes. A file like `page.ja.tsx` under a concrete product route should own its fixed canonical path (for example `/ja/plans/acp`) and the wrapper should normally select the locale module, not pass a path override that can create locale/path mismatches.
5. When a user questions why a wrong implementation was chosen, treat it as a workflow correction: explain the original decision path candidly, then encode the corrected contract in source/tests instead of only changing the immediate line.
6. When a shared component looks correct under `(legacy)` but differs under `(tailwind)`, first check whether the component or its primitives depended on legacy globals. Prefer a scoped component-level compatibility contract with exact legacy token values over broadening Tailwind globals for a narrow UI parity PR.

## Verification Checklist

- [ ] Skill loaded because the task matches `corp-web-app`.
- [ ] Migrated context reference reviewed when repo-specific history matters.
- [ ] Live repo/source checked before acting on potentially stale implementation details.
