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

Important path-guard nuance learned later:
- when the helper needs to avoid double-prefixing already-preview paths, do **not** use a broad check like `path.startsWith("/t")`
- that incorrectly treats canonical paths such as `/terms-of-service` as already preview-scoped because they also start with `/t`
- instead, only treat the explicit preview namespace as already-previewed:

```ts
if (path === "/t" || path.startsWith("/t/")) {
  return path;
}
```

This exact bug caused Preview Toggle to leave `利用規約` on `/terms-of-service` while correctly prefixing `/privacy-policy`, `/eula`, and `/cookie-preference`.

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
  - can also add preview-only footer columns by conditionally appending them when `previewModeEnabled` is true
- `src/components/layout/site-footer.module.css`
  - if a preview-only footer column changes desktop column count, add a preview-only layout class (for example a six-column desktop grid) and apply it only when `previewModeEnabled` is true

#### Why this split matters
The header was already a client component for dropdown state, while footer/sidebar links need server-consistent href generation. The safest low-scope pattern is:
- server wrapper reads cookie
- client header renders existing dropdown behavior plus toggle
- server footer/sidebar read the same cookie directly

This avoids trying to make environment-based navigation decisions independently in multiple client components.

Important extension learned from follow-up debugging:
- any shared sidebar used by both preview and public resource-list pages must also read the same preview-navigation cookie by default
- do not rely only on page-level explicit `links={previewResourceCategorySidebarLinks}` overrides for `/t/...` routes
- otherwise, navigating from a preview-enabled state into a public page like `/whitepapers` can silently reset the sidebar back to public links even while header/footer still show preview navigation
- preferred fix: make the shared sidebar component itself resolve its default link set from `PREVIEW_NAVIGATION_COOKIE` + `getPreviewNavigationState(...)`, while still allowing an explicit `links` prop override where a page intentionally needs a fixed link set

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

## Preview-toggle-only resource link pattern

Use this when the user wants a preview-only link added under existing header/footer resource menus, but only while Preview Toggle is enabled.

Example requirement:
- add `イベント` under `ブログ` in the GNB resource menu
- add the same `イベント` link under `ブログ` in the footer resource menu
- link target should resolve to `/t/events` only when preview navigation is enabled
- production / preview-toggle-off should keep the existing canonical menu without the extra item

Recommended implementation in both:
- `src/components/layout/site-header-client.tsx`
- `src/components/layout/site-footer.tsx`

Pattern:

```ts
{ label: "ホワイトペーパー", href: "/whitepapers" },
{ label: "ブログ", href: "/blog" },
...(previewModeEnabled ? [{ label: "イベント", href: t("/events", previewModeEnabled) }] : []),
```

Why this exact pattern:
- preserves existing canonical links for non-preview mode
- keeps the extra item absent unless Preview Toggle is actually on
- still routes through the shared `t()` helper so the preview target becomes `/t/events`

Do not:
- replace the canonical blog/whitepaper links with `t(...)` unless the task explicitly asks for that
- add the events item unconditionally if the request is specifically tied to Preview Toggle behavior

## Test alignment for preview-only resource items

When adding a preview-only item to header/footer resource menus, update existing source-string tests in the same PR.

Current relevant tests:
- `tests/canonical-endpoints.test.mjs`
- `tests/link-and-metadata-integrity.test.mjs`

Expected string to add:

```ts
'label: "イベント", href: t("/events", previewModeEnabled)'
```

If the repo uses the shared resource sidebar component in `src/components/sections/resource-category-sidebar.tsx`, also update its preview link set in the same PR.

Current required preview sidebar entry:

```ts
{ label: "イベント", href: "/t/events" }
```

Why:
- header/footer preview menus can already show `イベント` correctly while the shared resource sidebar still omits it
- public resource pages like `/whitepapers` can therefore reproduce a partial preview-navigation mismatch even when GNB and footer are already fixed
- the sidebar uses explicit preview/public link arrays, so this is not automatically inherited from header/footer changes

Recommended test alignment:
- update `tests/resource-list-page-structure.test.mjs`
- assert the preview sidebar link set contains `イベント -> /t/events`

Keep the change minimal:
- no new route work if `src/app/t/events/page.tsx` already exists
- no footer/sidebar refactor if only one new preview-only resource item is needed

## Preferred scope

Keep the change minimal:
- no duplicated header/footer components
- no broad layout-mode refactor unless the user explicitly asks for it
- no speculative remapping for nonexistent preview pages

## Demo navigation links that follow Preview Toggle

Use this when the user wants the `デモ` section in the GNB or footer to switch between preview and public destinations with the same Preview Toggle behavior used elsewhere.

Recommended implementation:
- in `src/components/layout/site-header-client.tsx`
- in `src/components/layout/site-footer.tsx`
- use the existing helper form with the already-resolved `previewModeEnabled` value

Current proven pattern:

Header:
```ts
{ label: "活用事例", href: t("/use-cases", previewModeEnabled) }
{ label: "AIP機能", href: t("/demo/aip", previewModeEnabled) }
{ label: "ACP機能", href: t("/demo/acp", previewModeEnabled) }
```

Footer:
```ts
{ label: "活用事例", href: t("/use-cases", previewModeEnabled) }
{ label: "AIP 機能", href: t("/demo/aip", previewModeEnabled) }
{ label: "ACP 機能", href: t("/demo/acp", previewModeEnabled) }
```

Result:
- preview on -> `/t/use-cases`, `/t/demo/aip`, `/t/demo/acp`
- preview off -> `/use-cases`, `/demo/aip`, `/demo/acp`

Important repo-specific nuance learned here:
- for this repo's current GNB/footer behavior, the public use-case destination should be `/use-cases`, not `/demo/use-cases`, when using the Preview Toggle helper pattern
- the header label strings are `AIP機能` / `ACP機能`, but the footer currently uses `AIP 機能` / `ACP 機能` with a space; keep string-based tests aligned with the actual component text instead of normalizing them speculatively

Recommended verification:
- `tests/link-and-metadata-integrity.test.mjs`
- `tests/canonical-endpoints.test.mjs`
- `tests/footer-preview-navigation.test.mjs`
- `npm run typecheck`

## Footer preview-only internal menu pattern

Use this when the user wants footer-only preview navigation that should appear only while the Preview Toggle is enabled.

Recommended implementation:
- define a small `internalFooterColumn` object inside `src/components/layout/site-footer.tsx`
- append it with `...(previewModeEnabled ? [internalFooterColumn] : [])`
- keep the links canonical to the internal routes themselves, for example:
  - `/internal`
  - `/internal/whitepaper-gating-demo`
  - `/internal/mdx-list-demo`
  - `/internal/load-more`
- do not show this column when preview mode is off

Recommended regression test shape:
- add a source-based test file such as `tests/footer-preview-navigation.test.mjs`
- assert all of the following in `site-footer.tsx`:
  - the conditional append based on `previewModeEnabled`
  - the `Internal` section title
  - each expected internal footer label and href
- also rerun existing footer/navigation regression tests because this repo already has string-based source assertions for footer contents

Practical note from this task:
- adding a new preview-only footer column can require a separate preview-only desktop grid class in `site-footer.module.css`; otherwise the normal five-column desktop layout can become cramped when the sixth column appears

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

## Porting the Preview Toggle pattern to corp-web-app

Use this when the user asks to implement the same corp-web-japan Preview Toggle behavior in `corp-web-app`.

Key differences from corp-web-japan:
- `corp-web-app` already has `src/utils/env/is-production.ts`; reuse it instead of adding `src/lib/is-production.ts`.
- Layout data for header/footer is loaded in `src/app/layout.tsx` via `FileQuerySingleton`, not hardcoded in header/footer components.
- The shared `Link` component automatically locale-prefixes internal links in `src/utils/client/use-updated-href.hook.ts`, so preview URLs must be generated as `/t/<locale>/...` and then excluded from locale-prefix rewriting.
- Current implemented preview routes are locale-scoped: `src/app/t/[locale]/blog`, `whitepapers`, `events`, and `demo/use-cases`. Do not point navigation at preview paths that do not exist on current `origin/main`.

Recommended corp-web-app implementation shape:
1. Add `src/lib/preview-navigation.ts` with the same cookie/state API (`PREVIEW_NAVIGATION_COOKIE`, `getPreviewNavigationState`, POST payload semantics), but map public paths to `/t/${locale}...`.
2. Include only verified route mappings, for example:
   - `/blog` and `/resources/discover/blog` -> `/t/<locale>/blog`
   - `/whitepapers` and `/resources/discover/white-paper` -> `/t/<locale>/whitepapers`
   - `/events`, `/webinars`, and `/resources/discover/webinars` -> `/t/<locale>/events`
   - `/demo/use-cases` and `/features/demo/use-cases` -> `/t/<locale>/demo/use-cases`
3. In `src/app/layout.tsx`, read `cookies()`, compute `previewModeEnabled`, and transform the fetched `headerData` / `footerData` before passing them to `Header`, `Main`, and `Footer`.
4. Make the transformer recursive enough to cover `href`, nested `items`, header `button`, `relatedArticle`, and CTA `pageSpecific` entries; otherwise dropdown buttons or related links can remain canonical while ordinary links switch.
5. Add `src/app/api/preview-navigation/route.ts` to write the `querypie-preview-navigation` cookie, forcing `off` in production.
6. Add a client `PreviewModeToggle` component under the header UI folder and render it from `header.component.tsx` when `showPreviewModeToggle` is true.
7. In `src/utils/client/use-updated-href.hook.ts`, treat `path === '/t' || path.startsWith('/t/')` as already preview-scoped so `/t/ja/blog` is not rewritten to `/ja/t/ja/blog`.

Verification notes from the corp-web-app port:
- Targeted test worked: `npm run test:run -- src/lib/__tests__/preview-navigation.test.ts`.
- Changed-file formatting check worked with `npx prettier --check <changed files>`.
- Full `npx tsc --noEmit --pretty false` can fail on existing baseline test typing issues unrelated to this feature (for example duplicate `name` props in form tests, mocked `Headers` casts in get-base-url tests, and missing `vi` namespace in remote-file tests). If it fails, grep the tsc log for touched paths before treating it as a regression.

## Done criteria

- `t("/path")` is used at explicit selected call sites
- production keeps canonical non-`/t` paths
- non-production defaults selected links to `/t/...`
- nonexistent `/t/...` routes are not linked prematurely
- `npm run typecheck` passes
