---
name: corp-web-japan-services-preview-migration
description: Migrate corp-web-japan redirect-backed upstream pages into local /t/... preview pages, while preserving production upstream redirects and routing non-production traffic to the preview implementation.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, preview, redirect, non-production, static-pages, vercel]
    related_skills:
      - corp-web-japan-origin-main-worktree-safety
      - github-pr-workflow
---

# corp-web-japan: /t preview migration for redirect-backed pages

Use this when a route currently redirects to `querypie.com/ja/...`, but the user wants a local preview implementation under `/t/...` for staged validation before public rollout.

## When to use

Typical examples:
- `/services/aip` -> local preview at `/t/services/aip`
- `/services/acp` -> local preview at `/t/services/acp`
- `/services/fde` -> local preview at `/t/services/fde`
- same pattern can apply to other redirect-backed areas under header/footer navigation

## Goal

Keep the public canonical route stable while adding a local preview implementation under `/t/...`.

There are two valid rollout modes. Choose based on the user's scope instruction.

### Mode A — route-level non-production redirect

Use this when the user explicitly wants the existing public route itself to resolve to `/t/...` outside production.

Desired behavior:
- production keeps redirecting to upstream `https://www.querypie.com/ja/...`
- non-production redirects the same public route to local `/t/...`
- the local `/t/...` page is `noindex` and uses canonical `/t/...`
- the preview page is implemented locally so design/content can be validated before final rollout

### Mode B — keep route handlers unchanged, switch only navigation links in preview mode

Use this when the user later clarifies that existing route handlers such as `src/app/services/aip/route.ts` must remain unchanged.

Desired behavior:
- public route handlers continue to redirect upstream exactly as before
- local `/t/...` preview pages still exist for direct access and staged validation
- non-production preview access is exposed through the existing preview-navigation toggle/link layer rather than by changing the route handler
- GNB/footer service links use the same preview-navigation helper pattern already used for other previewable links

## Proven workflow

1. Start from latest `origin/main` in a fresh worktree.
2. Inspect the current redirect route(s), header/footer links, and existing `/t/...` preview page patterns.
3. Inspect the upstream page content directly in the browser.
4. Extract the core section structure and representative copy from the upstream page.
5. Download the minimum route-aligned assets needed for the preview page.
6. Implement local static preview pages under `src/app/t/.../page.tsx`.
7. Choose rollout mode:
   - Mode A: update the redirect route to branch on production vs non-production
   - Mode B: keep route handlers unchanged and wire GNB/footer through the existing preview-navigation helper/toggle layer
8. Add or update regression tests for the selected mode.
9. Run targeted tests and `npm run build`.
10. Commit, push, open/update PR, and watch CI through completion.

## Implementation details

### 1. Keep the visible navigation route stable

Do not change public-facing route names.

Then choose one of two exposure strategies.

#### Mode A — route handler decides

Keep header/footer links pointing at the stable public route, for example:
- header/footer continues to link to `/services/aip`

Then make the route decide where to go:
- production -> upstream QueryPie page
- non-production -> `/t/...`

#### Mode B — preview-navigation link layer decides

Use this when the user does not want existing route handlers changed.

Keep the public route handlers untouched, but make preview-mode navigation point to `/t/...` by reusing the existing `t(path, previewModeEnabled)` helper pattern from the merged preview-navigation work.

Example:
- `site-header-client.tsx` service links become `t("/services/aip", previewModeEnabled)`
- `site-footer.tsx` service links become `t("/services/aip", previewModeEnabled)`

This lets:
- production and normal navigation keep the stable public path
- preview mode send GNB/footer traffic to `/t/services/...`
- direct `/services/...` requests still behave exactly like the old upstream redirect handler

### 2. Route branching pattern

Use this only for Mode A.

Use `@/lib/is-production`.

Pattern:

```ts
import { NextResponse } from "next/server";
import isProduction from "@/lib/is-production";

const previewDestination = "/t/services/aip";
const productionDestination = "https://www.querypie.com/ja/solutions/aip";

export function GET(request: Request) {
  const destination = isProduction()
    ? productionDestination
    : new URL(previewDestination, request.url).toString();

  return NextResponse.redirect(destination, 307);
}

export const HEAD = GET;
```

Important:
- keep status `307`
- build the non-production destination from `request.url`
- preserve the production upstream destination exactly unless the user asked to change it
- if the user later says the route handler must remain unchanged, revert to Mode B instead of trying to preserve both behaviors in one handler

### 3. Preview-navigation link-layer pattern

Use this for Mode B when preview traffic should come from GNB/footer without changing the route handlers.

Pattern already proven in `corp-web-japan` latest main:

```ts
import { t } from "@/lib/preview-navigation";

{ label: "AIプラットフォーム｜AIP", href: t("/services/aip", previewModeEnabled) }
```

Common file locations:
- `src/components/layout/site-header-client.tsx`
- `src/components/layout/site-footer.tsx`

Important:
- reuse the existing preview toggle/cookie helper layer already on latest main
- for this repo, current header link expectations often live in tests against `site-header-client.tsx`, not `site-header.tsx`, because `site-header.tsx` is now the server wrapper

### 3. Preview page metadata contract

For each `/t/...` page:
- `alternates.canonical` must be the `/t/...` path
- `robots.index = false`
- `robots.follow = false`

Pattern:

```ts
export const metadata: Metadata = {
  title: "... | QueryPie AI",
  description: "...",
  alternates: {
    canonical: "/t/services/aip",
  },
  robots: {
    index: false,
    follow: false,
  },
};
```

## Page-authoring guidance

Use route-local authoring in `page.tsx`.

Preferred shape:
- page JSX readable in one file
- keep the main Japanese copy and section order local to the route
- use shared primitives such as `SiteHeader`, `SiteFooter`, `RevealOnScroll`
- do not recreate an extra page-specific content registry unless truly necessary

## Asset handling

For repeated preview migration work, use route-aligned local public paths.

Example used successfully:
- `public/services/aip/*`
- `public/services/acp/*`
- `public/services/fde/*`

Guidelines:
- download only the assets actually used by the preview page
- prefer colocating them under a route-shaped directory
- if remote GIF/PNG/SVG assets are required for reliable preview/build behavior, localize them instead of hotlinking
- for animated GIFs rendered by Next `Image`, `unoptimized` may be appropriate

## Upstream inspection strategy

Use the browser and lightweight scraping together:
- browser navigation for structure/title/visible sections
- lightweight HTML text extraction to collect headings, paragraphs, and image URLs

Effective approach used here:
- navigate upstream URLs with the browser tool to verify titles and visible sections
- use a simple requests + BeautifulSoup extraction script to list `h1/h2/h4/p/li` text and image URLs from `<main>`
- use those extracted image URLs to download only the preview assets that matter

This is faster and more reliable than trying to fully reverse-engineer the upstream source implementation.

## Test strategy

Add focused regression coverage based on the selected mode rather than only broad repo tests.

Good shared coverage for both modes:
1. `/t/...` page file exists
2. page exports `metadata`
3. metadata includes canonical `/t/...`
4. metadata is `noindex`
5. page includes `SiteHeader` and `SiteFooter`

Mode A specific coverage:
6. redirect route imports `isProduction`
7. redirect route includes both preview and production destinations
8. redirect route builds the preview URL from `request.url`
9. redirect route keeps `HEAD = GET`

Mode B specific coverage:
6. header/footer service links use `t("/services/...", previewModeEnabled)`
7. tests read `src/components/layout/site-header-client.tsx` if that file is the active client-side nav source on latest main
8. route handlers remain unchanged upstream redirects

## Verification

Recommended minimum:

```bash
node --test tests/redirect-endpoints.test.mjs tests/<new-preview-test>.test.mjs
PATH='../../node_modules/.bin:'"$PATH" npm run build
```

Notes:
- in worktrees, root `node_modules` may still be reusable via PATH prefixing
- build warnings about multiple lockfiles in worktrees are acceptable if build succeeds

## CI follow-through

After PR creation:
- check `gh pr checks`
- if checks are still spinning up, also check `gh run list --branch <branch>`
- keep polling until Verify/Deploy settle
- report both PR number and final CI state

## Pitfalls

- forgetting to preserve production upstream redirects while adding preview behavior
- changing header/footer links prematurely when the user only asked for preview migration
- leaving preview pages indexable
- hotlinking remote assets instead of localizing route-aligned copies when preview stability matters
- skipping route-specific regression tests and relying only on general CI
- forgetting that worktree-local `node_modules` may be absent even when root dependencies are usable

## Done criteria

- `/t/...` preview page exists and builds
- production route still redirects upstream
- non-production route redirects to the matching `/t/...` preview page
- regression test covers both metadata and redirect branching
- PR is open and CI has been checked to completion
