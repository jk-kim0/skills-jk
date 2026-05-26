---
name: nextjs-app-router-route-group-layouts
description: Implement or review Next.js App Router route groups and multiple root layouts without changing public URLs or accidentally keeping a top-level root layout in the way.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, app-router, route-groups, layouts, routing, refactor]
    related_skills: [nextjs-typescript-config-contracts, github-pr-workflow]
---

# Next.js App Router Route Group Layouts

Use this when a task asks to:
- split an App Router tree into route groups such as `(legacy)` and `(tailwind)`
- introduce multiple root layouts
- isolate one endpoint or route family from an existing root layout chrome
- explain why a nested `layout.tsx` cannot replace an already-applied parent layout
- add a smoke page under a new root layout without changing public URLs

## Core principle

A nested route layout can add wrapping UI, but it cannot remove a parent root layout. If `src/app/layout.tsx` exists, it remains the common parent for route groups below it.

For true multiple root layouts, remove or move the top-level `src/app/layout.tsx` and put root layouts inside top-level route groups:

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

Route group segment names do not appear in URLs. For example, `src/app/(tailwind)/internal/tailwind/page.tsx` serves `/internal/tailwind`.

## Implementation workflow

1. Confirm the current route tree and Next version.
   ```bash
   pwd
   git rev-parse --show-toplevel
   git status --short --branch
   node -p "require('./package.json').dependencies.next || require('./package.json').devDependencies.next"
   find src/app -name layout.tsx -o -name page.tsx | sort | sed -n '1,120p'
   ```

2. Start from a fresh non-main worktree and latest `origin/main` for repo work.
   - Follow the repo's worktree policy.
   - Do not perform large route moves in the main checkout.

3. Move the existing root layout into the legacy group.
   ```bash
   mkdir -p 'src/app/(legacy)' 'src/app/(tailwind)'
   git mv src/app/layout.tsx 'src/app/(legacy)/layout.tsx'
   ```

4. Move existing page route trees into `(legacy)`.
   - Move `src/app/page.tsx`, locale route trees, catch-all pages, and other existing page routes that should keep the current chrome.
   - Keep framework route handlers that should remain layout-independent (for example `api`, `sitemap.xml`, docs proxy routes) at the top level unless the task explicitly asks to move them.
   - Avoid moving public assets such as `favicon.ico`, `icon.png`, `apple-icon.png`, `globals.css`, and shared modules such as `fonts.ts` unless there is a clear reason.

5. Fix imports caused by layout relocation.
   - A moved root layout usually needs `import '../globals.css';` instead of `import './globals.css';`.
   - Prefer absolute `src/...` imports for shared components to avoid brittle `../components` shifts.

6. Add or update the new root layout under the new group.
   - Root layouts must return `<html>` and `<body>`.
   - Keep global providers, analytics, cookie preference, and shared dimmed layers intentionally copied or factored.
   - Do not include legacy chrome in the new layout if the point is layout isolation.
   - If the group contract changes from an isolated smoke page to legacy-chrome parity, update the group `layout.tsx` first: reuse the same Header/GNB/Footer/runtime wrapper primitives as legacy, pass the same preview/navigation state, and update any source-shape tests that previously asserted Header/Footer absence.
   - For a Tailwind-owned route group, treat the legacy `globals.css` as a visual reference only, not as an implementation source. Prefer a one-line Tailwind group global (`@import "tailwindcss";`) and move all required layout/color/spacing contracts into Tailwind classes, component-local CSS, or explicit shared-component values. Do not add `@theme`, base resets, dimmed-layer rules, or legacy CSS-variable fallbacks merely to keep old components working; those components should be tested/refactored intentionally as part of the migration.

7. Add only the requested smoke route or route family to the new group.
   - Ensure the same URL is not also implemented in another route group.
   - If the smoke route is intentionally unprefixed, check middleware locale redirects and default-locale rewrites.

8. Update source imports/tests that reference moved route modules.
   - `src/app/[locale]/...` imports become `src/app/(legacy)/[locale]/...` for tests/source-level inspections.
   - Relative imports from tests into `src/app/...` may need extra path segments or should be converted to stable absolute aliases.
   - Keep README/doc prose churn out of the PR unless the task asks to update docs; moving a README does not require rewriting every mentioned source path.

9. Preserve route-specific ownership when touching metadata helpers in moved or wrapped route modules.
   - A locale-specific product page such as `src/app/(legacy)/[locale]/plans/acp/page.ja.tsx` owns only `/{locale}/plans/acp`; its default `generateMetadata()` fallback must be the product route, not a broader parent such as `/{locale}/plans`.
   - If a wrapper passes `urlPath` into locale modules, still set each module's no-argument fallback to the route it directly serves.
   - Add direct tests that call the locale-specific `generateMetadata()` without arguments, so the route module's own canonical/default path cannot silently drift behind wrapper behavior.

## Verification

Use lightweight checks first:

```bash
git diff --check
npx next typegen
npm test -- --run <new-route-group-test> <middleware-test-if-touched>
node scripts/ci/assert-test-groups.mjs  # if the repo partitions tests
```

`npx next typegen` is a useful low-cost check that the App Router tree parses after route-group moves. It can catch invalid route conflicts without spending time on a full build.

Run full build/test only when the user asks or the repo workflow requires it. In fresh worktrees, broad Vitest groups can fail during collection if dependencies are not installed locally, even when targeted route tests pass.

## Pitfalls

## Pitfalls

- Do not claim endpoint-only layout isolation if a top-level `src/app/layout.tsx` still exists; it will still wrap the endpoint.
- Do not solve parent-layout removal with only a nested `layout.tsx`; that only adds another wrapper.
- Do not leave the same URL in two route groups; route group names are invisible in public URLs, so duplicates conflict.
- Route groups alone are not a good model for multiple independent micro-sites that each need their own `/` on distinct domains. Route group names do not appear in URLs, so public roots collide unless host/path rewriting or multiple apps are introduced.
- For micro-sites with independent URLs and operational ownership, prefer a monorepo with multiple independent Next.js apps (`apps/<site>`) plus shared packages over one app with hidden host-based middleware rewrites. It keeps source paths, asset paths, metadata, Vercel project roots, rollback, and local development more intuitive.
- If the user explicitly wants one app anyway, prefer explicit source routes such as `src/app/sites/<site-slug>/**` and declarative Vercel host rewrites over custom `middleware.ts` rewrites. Keep assets root-absolute under `public/microsites/<site-slug>/**`; avoid relative image paths from nested routes like `/sites/<site>/agenda`.
- Do not move every `src/app/**` directory blindly. Top-level route handlers and metadata endpoints may not need layout grouping.
- Do not rewrite moved README/docs just because a broad search-and-replace touched them. Restore docs unless they are intentionally in scope.
- If adding an unprefixed internal smoke endpoint, check middleware locale redirect behavior; otherwise `/internal/tailwind` can redirect to `/:locale/internal/tailwind` and miss the intended route.
- If `npx next typegen` warns about multiple lockfiles in worktrees, treat it as a worktree-root inference warning unless route generation actually fails.


## Reference

- See `references/corp-web-app-route-group-split.md` for a concrete session pattern from splitting corp-web-app into `(legacy)` and `(tailwind)` root layout groups with a `/internal/tailwind` smoke page.
- See `references/corp-web-app-tailwind-group-legacy-chrome-parity.md` for the follow-up pattern where `(tailwind)` changed from isolated smoke layout to legacy Header/GNB/Footer parity without copying the full legacy globals/reset stack.
