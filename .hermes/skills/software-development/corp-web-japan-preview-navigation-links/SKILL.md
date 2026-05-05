---
name: corp-web-japan-preview-navigation-links
description: Apply selective `/t/...` preview navigation links in corp-web-japan using a small `t("/path")` helper that defaults to preview outside production.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, preview, navigation, header, footer, environment]
---

# corp-web-japan preview navigation links

Use this when the user wants some navigation links in `corp-web-japan` to point to `/t/...` preview pages in non-production, while keeping production links unchanged.

## When to use

Typical cases:
- Header/footer company-info links should point to preview pages on preview/stage environments.
- Only some routes have `/t/...` preview implementations.
- The user wants a very explicit link style like `href: t("/about-us")` rather than a large mode/config abstraction.

## Core preference learned from the user

Prefer a tiny helper with explicit call sites:

```ts
href: t("/about-us")
```

This is preferred over:
- a global `preview mode` prop passed through layout/header/footer
- duplicating header/footer/layout components
- broad hidden remapping tables when only a few links need preview behavior

Why:
- call sites stay easy to read
- only selected links opt into preview behavior
- future follow-up pages are one-line changes

## Environment rule

Do **not** use `process.env.NODE_ENV !== "production"` directly for this repo pattern.

Instead, add `src/lib/is-production.ts` and mirror the proven `corp-web-app` helper exactly:

```ts
const isProduction = () => {
  return process.env.VERCEL_TARGET_ENV === 'production';
};

export default isProduction;
```

Then implement the preview helper like:

```ts
import isProduction from "@/lib/is-production";

export function t(path: string) {
  return !isProduction() ? `/t${path}` : path;
}
```

Reason:
- the user explicitly wanted the same environment-detection approach used in sibling QueryPie repos
- `VERCEL_TARGET_ENV === 'production'` is the chosen production signal here

## Implementation patterns

There are now two valid patterns depending on the user's request.

### Pattern A: environment-default preview links
Use this when the user wants selected links to point to `/t/...` automatically outside production, with no user-facing toggle.

#### 1. Add the shared helpers
- `src/lib/is-production.ts`
- `src/lib/preview-path.ts`

#### 2. Update only the selected links
Import `t` where needed and apply it only to routes that should use preview by default outside production.

### Pattern B: non-production preview toggle with persistent override
Use this when the user wants a visible preview-mode control in stage/preview deployments that can turn `/t/...` navigation on and off interactively.

This pattern was used for PR 179 follow-up work.

#### Core behavior
- production: no toggle, always canonical non-`/t` links
- non-production: show a floating round toggle button in the header
- default state in non-production: preview navigation ON
- user override persists in a cookie
- header, footer, and any matching company-info sidebar must all read the same state

#### Recommended structure
- `src/lib/preview-navigation.ts`
  - exports cookie name constant
  - computes whether the toggle should be visible
  - computes whether preview navigation is enabled from environment + cookie
  - exports `t(path, previewModeEnabled)`
- `src/app/api/preview-navigation/route.ts`
  - POST route that writes the cookie (`on` / `off`)
- `src/components/layout/site-header.tsx`
  - server wrapper that reads cookies and passes state down
- `src/components/layout/site-header-client.tsx`
  - existing interactive header logic plus the toggle UI
- `src/components/layout/preview-mode-toggle.tsx`
  - client toggle button that POSTs to the API route and then `router.refresh()`
- `src/components/layout/site-footer.tsx`
  - server component that reads the same cookie and applies the same `t(..., previewModeEnabled)` logic

#### Why this split matters
The header was already a client component for dropdown state, while footer/sidebar links need server-consistent href generation. The safest low-scope pattern is:
- server wrapper reads cookie
- client header renders existing dropdown behavior plus toggle
- server footer/sidebar read the same cookie directly

This avoids trying to make environment-based navigation decisions independently in multiple client components.

Examples:
- `src/components/layout/site-header.tsx`
- `src/components/layout/site-footer.tsx`
- company-info sidebars such as `src/components/sections/news-list-page.tsx`

Example:

```ts
{ label: "私たちについて", href: t("/about-us") }
{ label: "ニュース", href: t("/news") }
{ label: "ホワイトペーパー", href: t("/whitepapers") }
```

Leave normal links alone:

```ts
{ label: "お問い合わせ", href: "/contact-us" }
```

## Important route-availability rule

Only wire `t("/path")` for preview pages that actually exist on the current `main` branch.

Before changing links, verify whether the target route exists, e.g.:
- `src/app/t/about-us/page.tsx`
- `src/app/t/news/page.tsx`
- `src/app/t/whitepapers/page.tsx`
- `src/app/t/events/page.tsx`

If a route is not on `main` yet, do **not** point navigation at it just because a preview idea exists.

Practical example from this task:
- `/t/about-us`, `/t/news`, `/t/whitepapers`, `/t/events` existed on `main`
- `/t/certifications` did not exist on `main`
- therefore `/certifications` was intentionally left unchanged until the preview page lands

## Preferred scope

Keep the change minimal:
- no duplicated header/footer components
- no broad layout-mode refactor unless the user explicitly asks for it
- no speculative remapping for nonexistent preview pages

## Existing helper preservation rule

Before adding or changing `src/lib/is-production.ts`, check whether the file already exists on the current `main` branch.

Practical lesson from this task:
- `src/lib/is-production.ts` was already present on `origin/main`
- a follow-up PR change accidentally rewrote that file instead of just reusing it
- the correct fix was to restore the file exactly from `origin/main`

Safe check pattern:

```bash
git show origin/main:src/lib/is-production.ts
```

If the file already exists on `main`:
- do not rewrite its wording/comments casually
- reuse it as the source of truth
- if a PR branch changed it unnecessarily, restore it from `origin/main`

## Test-alignment rule

If you convert navigation call sites from literal href strings to the helper form `t("/path")`, update repo string-based tests in the same change.

Important files from this task:
- `tests/canonical-endpoints.test.mjs`
- `tests/link-and-metadata-integrity.test.mjs`

Typical failure pattern:
- CI still expects literal strings such as `href: "/about-us"` or `href: "/whitepapers"`
- implementation now intentionally contains `href: t("/about-us")` or `href: t("/whitepapers")`

So when updating navigation to use the preview helper, also update test expectations to the helper-based string form where applicable.

## Verification

Additional repo-specific pitfall learned from PR follow-up work:
- `tests/news/mdx-routing-and-preview.test.mjs` does source-structure assertions against `src/components/sections/news-list-page.tsx`, not just runtime behavior.
- If your preview-navigation change touches `NewsListPage`, preserve or consciously update the expected source-visible defaults there.
- In particular, the test currently expects all of these to remain visible in the source unless intentionally updated together:
  - a literal `News` default heading in the component source
  - the bottom CTA copy `まずは小さく、失敗しないAXを始めよう`
  - the CTA support copy `簡単サインアップで、14日間の無料トライアルをお試しください`
  - the CTA URL `https://app.querypie.com/`
- A practical safe pattern when adding preview-navigation cookie logic to `NewsListPage` is: keep the new company-info link behavior, but preserve the existing preview page's source-visible heading/CTA structure unless the task explicitly includes a UX rewrite and matching test updates.

For this user's preference, start with the lightest meaningful verification:

```bash
npm run typecheck
```

If CI later fails, the most likely first follow-up is to check the string-based navigation tests above.

A reliable local confirmation command from this task was:

```bash
npm run test:ci
```

## CI follow-up nuance

If the PR does not show any `pull_request` checks even after pushing:
- do not assume the code is fine or broken from that absence alone
- inspect workflow status with `gh pr checks` and `gh run list`
- if needed, trigger the repo CI manually with:

```bash
gh workflow run CI --ref <pr-branch>
```

Then watch it and inspect failed logs with:

```bash
gh run watch <run-id> --exit-status
gh run view <run-id> --log-failed
```

## PR follow-up nuance

If the user later asks to replace environment detection after the initial PR is already open:
- use a fresh worktree on the existing PR branch
- copy the exact `is-production.ts` implementation from `corp-web-app`
- push back to the same PR branch rather than opening a new PR

## Done criteria

- `t("/path")` is used at explicit selected call sites
- production keeps canonical non-`/t` paths
- non-production defaults selected links to `/t/...`
- nonexistent `/t/...` routes are not linked prematurely
- `npm run typecheck` passes
