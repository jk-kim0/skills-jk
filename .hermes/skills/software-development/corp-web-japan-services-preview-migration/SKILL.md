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

Typical examples and current taxonomy:
- AIP and ACP are platform products, not service-offering pages:
  - final target: `/platforms/aip`, `/platforms/acp`
  - preview target: `/t/platforms/aip`, `/t/platforms/acp`
  - older `/t/services/aip` and `/t/services/acp` routes should be treated as pre-rename legacy preview paths when working on Issue 454 follow-up.
- FDE remains a service-offering page because it is a project-style consulting/collaboration service rather than a platform product:
  - preview route stays `/t/services/fde`
  - final public route: `/services/fde`
- same preview pattern can apply to other redirect-backed areas under header/footer navigation, but classify the route family before choosing `services`, `platforms`, or another noun.

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

## Multi-page request rule

If the user asks for several service pages in one request, split them into separate fresh worktrees and separate PRs unless they explicitly ask for one combined PR.

Practical reason learned from `/t/services/aip`, `/t/services/acp`, and `/t/services/fde` follow-up work:
- each service page can differ materially in complexity and migration shape
- one page may be a straightforward parity port while another may require a custom interactive browser or a heavier asset import set
- separate PRs keep review focused and make it easier to verify the exact preview deployment per page

Recommended pattern:
- one branch / PR for the AIP rename or parity work (`/t/services/aip` -> `/t/platforms/aip` when following the Issue 454 taxonomy)
- one branch / PR for the ACP rename or parity work (`/t/services/acp` -> `/t/platforms/acp` when following the Issue 454 taxonomy)
- one branch / PR for `/t/services/fde` service-page work; do not move FDE into `platforms` unless the user explicitly reverses the taxonomy decision
- repeat the same latest-main worktree safety checks for each page independently

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
- lightweight HTML text extraction to collect headings, paragraphs, links, and image URLs

Effective approach used here:
- navigate upstream URLs with the browser tool to verify titles and visible sections
- use a simple requests + BeautifulSoup extraction script to list `h1/h2/h4/p/li` text and image URLs from `<main>`
- use those extracted image URLs to download only the preview assets that matter
- for service landing pages like `/ja/solutions/aip`, also inspect the authored `../corp-web-contents/pages/solutions/<slug>/ja/content.mdx` so you recover embedded-video presence, the exact 3-card value section, alternating feature-band order, and CTA wording rather than paraphrasing from memory

This is faster and more reliable than trying to fully reverse-engineer the upstream source implementation.

## Service-page parity rules learned from `/t/services/aip`

When the target is a QueryPie Japan service landing page that summarizes several deeper AIP/ACP/FDE subpages:

- Do not leave placeholder preview-only copy such as `Preview Service`, `Value 1`, or explanatory text like `preview でローカル確認できるように移しています`.
- Restore the real hero structure from upstream, including embedded video if the source page has one.
- Restore the 3-card value section as real image + title + body + `詳細を見る` links, not as generic bordered marketing cards.
- Restore the alternating feature-band layout (muted/white rhythm plus left/right media alternation) instead of collapsing everything into a uniform 2-column card grid.
- Restore the upstream CTA wording exactly when the source page already has a final CTA.

### Link-target rule for service landing pages

For service landing pages, card/detail links may need a mixed strategy:
- if the corresponding deep page already exists locally as a preview route, link to that local preview route from the preview landing page
  - example: `/t/services/aip` value cards should use local preview detail routes such as `/t/solutions/aip/usage-based-llm`, `/t/solutions/aip/mcp-gateway`, and `/t/solutions/aip/fde-services`
- if the corresponding deep page does not yet exist locally, keep the upstream destination for now rather than inventing a broken local path
  - example: the AIP integrations text link can stay on `https://www.querypie.com/ja/solutions/aip/integrations` until a local preview or canonical replacement exists

This produces a usable preview migration without pretending the entire deeper page family is already locally rebuilt.

## Audit workflow: identify the exact migration target for an existing `/t/services/*` preview page

Use this when the user asks whether a preview migration is complete and first wants to know which upstream page the preview route was intended to replace.

Preferred evidence order:
1. inspect the matching public short-route redirect handler, for example `src/app/services/aip/route.ts`
2. inspect redirect coverage tests such as `tests/redirect-endpoints.test.mjs` and `tests/services-preview-routes.test.mjs`
3. inspect the authored source in `../corp-web-contents/pages/solutions/.../ja/content.mdx` and `meta.json`
4. verify the live upstream page in the browser (`title`, `h1`, canonical URL)
5. if needed, inspect the introducing commit or PR that added the preview route

For `/t/services/aip`, this audit pattern confirms:
- preview route: `src/app/t/services/aip/page.tsx`
- short route redirect target: `https://www.querypie.com/ja/solutions/aip`
- authored source: `../corp-web-contents/pages/solutions/aip/ja/content.mdx`
- live page title/H1: `QueryPie AIプラットフォーム (AIP)`

Why this matters:
- the preview page content can look obviously AIP-related, but the redirect route and tests give the strongest repo-local contract for the intended upstream target
- `corp-web-contents` confirms the authored Japanese source of truth
- the live browser check confirms what actually shipped to users
- the adding commit/PR is useful when you need to explain intent or scope, not just current behavior

## Page-family-specific migration heuristics

### Route taxonomy decision for AIP / ACP / FDE

Issue 454 established a route-family distinction that should be applied before implementing follow-up route moves:

- AIP and ACP are platform products.
  - Use plural `platforms` because they are parallel platform offerings (`AI Platform`, `Access Control Platform`).
  - Preview targets: `/t/platforms/aip`, `/t/platforms/acp`.
  - Final public targets: `/platforms/aip`, `/platforms/acp`.
  - Treat older `/t/services/aip` and `/t/services/acp` as preview paths to rename, not as the final taxonomy.
- FDE is not a platform product in this taxonomy.
  - It is a project-style service/collaboration offering.
  - Keep preview route `/t/services/fde`.
  - Prefer `/services/fde` as the public service-family candidate unless the user changes the policy.
- Do not mechanically convert all `/t/services/*` pages to `/t/platforms/*`; classify each family by product/service semantics first.
- When updating a tracking issue after taxonomy decisions, verify the current `origin/main` path inventory before carrying forward old duplicate/canonical TODOs. In issue 454 follow-up, `src/app/t/solutions/aip/fde-services` was already absent while `src/app/t/services/fde/page.tsx` remained, so the duplicate-route cleanup belonged in an "already resolved" note, not in remaining work.

### `/t/services/fde`

A reliable parity shortcut:
- compare the live page against any existing local preview under `src/app/t/solutions/aip/fde-services/page.tsx`
- if that solution preview already matches the same live source well, reuse its route-local copy and section-primitive structure rather than maintaining a second placeholder layout
- keep the service preview route's own canonical path and route-aligned asset root (`public/services/fde/*`), but do not hesitate to mirror the proven hero / alternating feature-band / CTA structure

When the user asks to merge `/t/solutions/aip/fde-services` and `/t/services/fde` into one page:
- treat `/t/services/fde` as the final preview endpoint unless the user explicitly says otherwise
- prefer the implementation whose route, canonical metadata, component path, and asset root already match the final endpoint (`src/app/t/services/fde/page.tsx`, `src/components/sections/fde/service-page.tsx`, `public/services/fde/*`)
- verify duplicate assets by checksum before deleting the old route-aligned copies; identical hashes make the old `public/solutions/aip/fde-services/*` assets safe to remove
- remove the duplicate preview route, duplicate section module, and duplicate route-specific tests rather than leaving a redirect or compatibility `/t/*` endpoint
- update sibling preview links such as the FDE value card in `/t/services/aip` so they point to `/t/services/fde`, not the removed `/t/solutions/aip/fde-services`
- keep existing public redirect route handlers unchanged unless the user explicitly asks for rollout; for this class of cleanup, the upstream redirect to `https://www.querypie.com/ja/solutions/aip/fde-services` can remain while only local preview endpoints are consolidated
- update non-indexability and page-structure tests so the deleted preview route is no longer listed and the surviving `/t/services/fde` test asserts the old route/component/assets are absent

### `/t/services/acp`

Do not assume ACP is a simple four-card static page.

Important real finding:
- the live ACP page includes a category-driven feature browser, not just a flat set of feature cards
- the main categories are:
  - `データベースアクセス制御`
  - `システムアクセス制御`
  - `Kubernetesアクセス制御`
  - `Webアクセス制御`
  - `ワークフロー & 統合`
- each category rotates through multiple tutorial items with its own animated asset and external docs link
- the page also includes:
  - hero YouTube embed
  - easy-use full-width illustration section
  - integrations split section with `利用可能なACP統合機能をすべて見る >`
  - final CTA using the standard trial wording

Implementation guidance for ACP parity:
- import the remaining tutorial GIFs into route-aligned `public/services/acp/*`
- prefer a dedicated client section component for the interactive category browser
- keep route-local authored copy and data in `page.tsx`, but let the section component own the tab / previous / next interaction and image rendering details
- keep the external `Learn More` links as direct docs links when there is no local migrated equivalent
- add a structure test that checks the route keeps the category labels and that the section module owns the interactive browser implementation (`useState`, prev/next controls, `Learn More` links)

These heuristics are specific enough to save significant rediscovery time on future service-page parity work.

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
