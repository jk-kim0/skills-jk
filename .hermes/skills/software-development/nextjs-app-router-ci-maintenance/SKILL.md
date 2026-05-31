---
name: nextjs-app-router-ci-maintenance
description: Use when maintaining a Next.js App Router repository's route layout architecture or Vitest/GitHub Actions CI scope splitting, especially when route moves, source ownership, tests, and CI filters must remain aligned.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, app-router, route-groups, layouts, vitest, github-actions, ci]
    related_skills: [nextjs-typescript-config-contracts, github-pr-workflow, systematic-debugging]
---

# Next.js App Router and CI Maintenance

## Overview

Use this umbrella for recurring Next.js repository maintenance where App Router source structure, route ownership, tests, and GitHub Actions validation must stay consistent. It consolidates two narrow but related workflows:

- **Route group / multiple-root-layout work** — split an App Router tree into groups such as `(legacy)` and `(tailwind)`, introduce multiple root layouts, isolate route families, and avoid accidental public URL changes.
- **Vitest CI scope splitting** — detect changed file scopes, run only relevant grouped tests/builds, and keep a stable aggregate required check.

These workflows often touch the same source tree and fail in similar ways: invisible route-group segment collisions, stale test import paths, unassigned Vitest files, and path filters that no longer match the route/component ownership model.

## When to Use

- User asks to split or review Next.js App Router route groups or multiple root layouts.
- User wants to isolate an endpoint/route family from legacy chrome without changing public URLs.
- User asks to split monolithic Next.js/Vitest CI by changed file scope.
- User asks whether a hosted PostgreSQL/Neon database schema matches the Prisma datamodel used by a Next.js app, or wants a DB schema drift check CLI/workflow.
- A new or moved test makes `assert-test-groups.mjs`, `test:smoke`, `test:ci`, or a CI "Detect changed scope" stage fail.
- A route move requires updating App Router tests, source-level imports, middleware behavior, or GitHub Actions path filters.

Do not use this for generic React component bugs unless App Router structure, route ownership, or CI grouping is central.

## Shared Pre-flight

1. Confirm repository, branch, and baseline.
   ```sh
   pwd
   git rev-parse --show-toplevel
   git status --short --branch
   git remote -v
   git fetch origin --prune
   ```
2. Inspect Next/Vitest/tooling versions and source layout.
   ```sh
   node -p "require('./package.json').dependencies?.next || require('./package.json').devDependencies?.next"
   find src/app -name layout.tsx -o -name page.tsx | sort | sed -n '1,160p'
   find src -path '*__tests__*' -o -name '*.test.*' | sort | sed -n '1,200p'
   ```
3. Work in a fresh non-main branch/worktree when doing broad route, CI, or shared shell/sidebar changes.
4. Prefer lightweight local verification first (`next typegen`, grouping assertions, YAML parse, targeted Vitest group, `git diff --check`) before full builds.
5. If follow-up work starts after the original PR was merged and its remote branch deleted, do not resurrect that merged branch. Fast-forward latest `main`, create a new latest-main worktree/branch, and open a separate follow-up PR.

## Build Metadata and Compact App Status UI

Use this section when a Next.js app needs to expose the built artifact's git identity in the UI, especially for Preview/Production deployment debugging.

Recommended shape:

1. Read git metadata at build/config time in `next.config.ts`, not at request runtime.
   - short hash: `git rev-parse --short=7 HEAD`
   - commit date: `git show -s --format=%cI HEAD`
   - Vercel hash fallback/override: `VERCEL_GIT_COMMIT_SHA` when available
2. Inject the values via `nextConfig.env` with the repo/project prefix in the public env names, then import them from a small formatting utility.
3. Add tests around the formatting utility so the visible status contract is stable.
4. For a left-sidebar build/debug ticker, prefer one compact bottom-aligned line:
   - visible format: `<hash> (MM-DDThh:mm)`
   - example: `abcdef1 (05-30T11:53)`
   - preserve the full ISO timestamp in a `title`/accessible label if useful.
5. CSS pattern for sidebar placement:
   - sidebar as vertical flex with `min-height: 100vh`;
   - status line uses `margin-top: auto`;
   - one-line flex layout, small font, `white-space: nowrap`, and ellipsis on the code/hash span;
   - reset full-height behavior on mobile when the sidebar becomes a normal top section.

Do not introduce a customer-facing product versioning scheme merely to identify preview builds. Commit-based build metadata is usually enough until release notes or customer-visible release versions exist.

Reference: keep long-running local build/test status observable with short periodic progress markers, but keep repo-specific ticker scripts in that repository.

## Route Group and Multiple Root Layouts

Core principle: a nested layout can add UI, but it cannot remove a parent root layout. If `src/app/layout.tsx` exists, it remains the common parent for route groups below it.

For true multiple root layouts, remove or move the top-level layout and put root layouts in top-level route groups:

```text
src/app/
  globals.css
  (legacy)/
    layout.tsx
    ...existing routes...
  (tailwind)/
    layout.tsx
    ...isolated routes...
```

Route group names do not appear in URLs. `src/app/(tailwind)/internal/tailwind/page.tsx` serves `/internal/tailwind`; the same visible URL in another group is a conflict.

Implementation rules:

1. Move the existing root layout into the group that should keep current chrome.
2. Move existing page route trees intentionally; keep layout-independent route handlers and metadata endpoints top-level unless the task requires moving them.
3. Fix imports after layout relocation. Moved root layouts often need `../globals.css`; source imports should prefer stable absolute aliases.
4. New root layouts must return `<html>` and `<body>` and intentionally include/exclude providers, analytics, cookie preference, dimmed layers, header/GNB/footer, and global CSS.
5. If an isolated route group later changes to legacy-chrome parity, update the group layout first and update tests that previously asserted header/footer absence.
6. For Tailwind-owned route groups, treat legacy global CSS as a visual reference, not as an implementation source. Move layout/color/spacing contracts into Tailwind classes, component-local CSS, or shared components intentionally.
7. Preserve route-specific metadata ownership. A locale-specific page's default `generateMetadata()` fallback should point to the route it directly serves, not a broader parent.

## Vitest / GitHub Actions CI Scope Splitting

Use this when the repository has monolithic validation and the user wants changed-scope CI narrowing.

Recommended structure:

- `changes` job using `dorny/paths-filter@v3`, marking all scopes dirty for non-PR events or manual dispatch.
- If the workflow has restrictive top-level permissions such as `contents: read`, also grant `pull-requests: read`; otherwise `dorny/paths-filter` can fail on PRs with `Resource not accessible by integration` while listing changed files.
- A lint/smoke job that runs grouping assertions when relevant files changed.
- One job per test group, e.g. publications, forms, routing, marketing widgets, shell, utilities.
- A build job gated by build-impacting scopes and scoped test success/skips.
- An always-running aggregate job (`ci-result`, `Validate Test`, etc.) so required checks appear even for docs-only PRs.

Test grouping rules:

1. Every in-scope Vitest file maps to exactly one group; assertions must fail on unassigned and overlapping files.
2. Prefer class-level path regexes over PR-by-PR filename enumerations.
3. Route/middleware/locale redirect/preview navigation tests usually belong in a routing/SEO group, regardless of which content family they mention.
4. Keep Playwright/E2E specs out of Vitest grouping unless they are actually run by Vitest.
5. Include workflow YAML, CI helper scripts, package files, lockfiles, and test config in a CI/build-impacting scope.
6. Keep path filters aligned with route-group source moves. After moving `src/app/[locale]` under `src/app/(legacy)/[locale]`, update tests and filters together.

## Prisma / Hosted PostgreSQL Schema Drift Checks

When a Next.js app uses Prisma with a hosted PostgreSQL/Neon database, implement schema drift checks as read-only diagnostics, not automatic database repair:

1. For Prisma 7+ projects with `prisma.config.ts`, compare the live DB URL to the Prisma schema through the configured datasource, e.g. inject the selected URL into both `DATABASE_URL` and `DATABASE_DIRECT_URL`, then run `prisma migrate diff --from-config-datasource --to-schema prisma/schema.prisma --script --exit-code`. Older Prisma projects may still use `--from-url` / `--to-schema-datamodel`; verify the installed CLI before writing docs or workflows.
2. Treat exit code `0` as no drift and exit code `2` as drift detected; reserve other non-zero codes for command/configuration failures.
3. If `prisma/migrations/` exists, run `prisma migrate status --schema prisma/schema.prisma` first. Note that status can say “Database schema is up to date” while `migrate diff` still detects drift if `schema.prisma` changed without a matching migration artifact.
4. Add a local CLI wrapper and tests for missing env, drift output, and migration-status failure paths before wiring CI.
5. In GitHub Actions for Vercel-hosted apps, prefer pulling Vercel env (`vercel pull`) for read-only runtime drift checks. For mutating migrate/backfill workflows, use a direct/non-pooling DB URL secret and verify it without printing it.
6. Never print database connection strings; report only the env var name, run URLs, and artifact paths.
7. Keep mutating workflows manual or explicitly scoped unless the user wants PR/blocking automation against shared databases.

See `references/prisma-db-schema-drift-check-vercel-neon.md` for the concrete read-only CLI/workflow pattern. For mutating shared Vercel/Neon DB workflows, secret derivation, one-time baseline resolve, backfill execution, and recovery when drift remains after a successful apply, see `references/prisma-shared-db-migration-vercel-neon.md`.

## Build Metadata / Deployment Identity UI

When a Next.js App Router app needs to show which build is currently deployed, prefer injecting git metadata at build/config evaluation time rather than reading git at request runtime:

1. In `next.config.ts`, read the commit hash/date with `node:child_process` and expose stable `env` values such as `NEXT_PUBLIC_<PROJECT>_GIT_COMMIT_HASH` and `NEXT_PUBLIC_<PROJECT>_GIT_COMMIT_DATE`.
2. Use platform-provided commit SHA first when available (for example `VERCEL_GIT_COMMIT_SHA`) and fall back to `git rev-parse --short=7 HEAD` for local builds.
3. Use `git show -s --format=%cI HEAD` for the commit timestamp and format it in app code, not CSS/JSX inline.
4. Add a tiny formatter module and unit tests for display/fallback behavior; keep the UI component only responsible for rendering the already-formatted value.
5. For narrow sidebars/status tickers, use a short debugging-oriented label such as `<hash> (MM.DDThh:mm)`. Treat longer strings like `yyyy.mm.dd-<hash>` as build IDs or release labels, not necessarily as the visible sidebar text.
6. If the user asks whether to introduce a product version, distinguish product versioning from build identity: early MVP/Preview deployments usually need commit-based build identity first; CalVer/SemVer can be introduced later when release notes/customer-facing releases exist.

Pitfalls:
- Do not read git metadata dynamically inside request handlers or server components when the requirement is “which artifact was built”; that can diverge from the deployed bundle.
- Do not use a long product-version-looking string in cramped navigation UI unless the user explicitly wants a release label there.
- If local test execution is blocked only because a fresh worktree lacks installed dependencies, report that as local setup state and rely on lightweight static checks plus CI when the user prefers fast PR creation over local installs.

## Lightweight Verification

For route tree changes:

```sh
git diff --check
npx next typegen
npm test -- --run <targeted-route-or-metadata-test>
```

For CI grouping changes:

```sh
node scripts/ci/assert-test-groups.mjs
node -e "JSON.parse(require('fs').readFileSync('package.json','utf8')); console.log('package.json ok')"
python3 - <<'PY'
import yaml
from pathlib import Path
yaml.safe_load(Path('.github/workflows/ci.yml').read_text())
print('workflow yaml ok')
PY
git diff --check
```

If grouped npm scripts exist, run the affected group script and then the aggregate script CI uses:

```sh
npm run test:<affected-group>
npm run test:ci
```

Do not treat `npm run test:run` passing as proof that grouped CI is healthy; `test:ci` may fail earlier during grouping smoke checks.

## References

Session-specific examples migrated from the absorbed skills live under `references/` with `nextjs-app-router-route-group-layouts-*` and `nextjs-vitest-ci-scope-splitting-*` prefixes. Prisma hosted DB schema drift check details live in `references/prisma-db-schema-drift-check-vercel-neon.md`; shared Vercel/Neon migration/backfill and drift recovery details live in `references/prisma-shared-db-migration-vercel-neon.md`.

## Common Pitfalls

- Claiming layout isolation while a top-level `src/app/layout.tsx` still wraps every route.
- Leaving the same public URL in two route groups; group segment names are invisible.
- Moving every `src/app/**` directory blindly; route handlers and metadata endpoints may be layout-independent.
- Rewriting README/docs just because a broad move touched paths; keep docs in scope only when requested.
- Missing middleware/default-locale redirect behavior for unprefixed internal smoke endpoints.
- Copying a sibling repo's CI scopes without listing current tests and source directories.
- Fixing `Unassigned test files` by over-broad regexes that create overlap later.
- Feeding Playwright/E2E files to Vitest.
- Letting required checks skip completely because of PR `paths-ignore`; use an aggregate result job.
- Forgetting to rerun grouping assertions after rebasing over newly merged tests.
- Assuming a manual migration workflow fully failed because its final drift-check step failed. Inspect prior steps first; migrate/backfill may have succeeded and only the schema diff remains.
- Relying on pooled Vercel runtime `DATABASE_URL` for Prisma Migrate/backfill. Use and verify a direct/non-pooling URL secret, while keeping secret values out of logs and chat.

8. When using `dorny/paths-filter@v3` in a workflow with explicit `permissions: contents: read`, forgetting `pull-requests: read` can make the scope-detection job fail with `Resource not accessible by integration` on PRs.
9. For nested apps, avoid workflow-global `defaults.run.working-directory` when adding repo-root scope detection or aggregate jobs. Put the nested working directory on the app-specific jobs instead.
10. When deploy/preview workflows are expensive, add `paths-ignore` for documentation-only surfaces there too; narrowing only the CI workflow can still leave deploy jobs running for docs-only PRs.

## Verification Checklist

- [ ] Route group changes preserve public URLs intentionally and avoid duplicate visible routes.
- [ ] Root layout placement matches the intended chrome/providing boundary.
- [ ] Moved route imports, metadata fallbacks, and source-level tests were updated.
- [ ] CI test groups assign every in-scope test exactly once.
- [ ] Path filters include route/source/test/config changes that affect each group.
- [ ] Lightweight checks ran before committing or the reason for deferring to CI is stated.
