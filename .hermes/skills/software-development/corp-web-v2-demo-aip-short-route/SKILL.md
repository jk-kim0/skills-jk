---
name: corp-web-v2-demo-aip-short-route
description: Shorten corp-web-v2 AIP demo URLs to /demo/aip/:id/:slug while keeping the existing managed demo rendering, adding legacy redirects, canonical metadata, tests, and PR follow-up updates.
---

# When to use

Use this when the user wants an AIP demo in `corp-web-v2` to move from legacy managed-demo paths such as:

- `/features/demo/aip-features/1/google-oauth-demo`
- `/features/demo/google-oauth-demo`

into a short canonical route such as:

- `/demo/aip/1/google-oauth-demo`

without converting the content to MDX.

This is especially appropriate when:

1. the demo already exists in managed content state
2. the rendering should stay aligned with existing `features/demo/[slug]` behavior
3. the request is a follow-up change on an already-open PR branch

# Key decision from prior work

Do not assume every short demo route should become an MDX migration.

For the AIP Google OAuth demo, the better implementation was:

- keep the existing managed demo entry and rendering pipeline
- add a thin short-route helper map for public canonical URLs
- redirect old paths to the short route
- update internal href generation so lists, related links, metadata, and sitemap all converge on the short route

This is different from ACP, where a separate MDX-backed route was the correct approach.

# Preconditions

1. If this is follow-up work on an open PR, use a fresh worktree on the existing PR branch, not a new PR branch.
2. Inspect the current managed demo route first:
   - `src/app/[locale]/features/demo/[slug]/page.tsx`
   - `src/features/content/data.ts`
   - `src/app/sitemap.ts`
3. Confirm the target content ID from `src/content/demo/**/meta.json` or content-state loading logic.

# Implementation pattern

## 1) Confirm the managed content entry

Find the actual managed demo content ID and category.

For the Google OAuth case, the successful mapping was:

- category: `aip-features`
- content ID: `google-oauth-demo`
- short public ID: `1`
- canonical slug: `google-oauth-demo`

Do not hardcode assumptions until you verify the source meta.

## 2) Add a dedicated AIP route helper

Create a helper like:

- `src/features/demo/aip.ts`

Include:

- explicit entry map `{ id, slug, contentId }`
- `getAipDemoEntry(id)`
- `getAipDemoEntryByContentId(contentId)`
- `getAipDemoHref(locale, id)` -> `/demo/aip/:id/:slug`
- `getAipDemoHrefByContentId(locale, contentId)`
- `resolveAipDemoRoute(locale, id, rest)` returning `{ entry, canonicalHref, shouldRedirect }`

Why explicit mapping matters:

- it cleanly separates public short IDs from managed content IDs
- it supports future expansion without coupling public routes to current storage conventions

## 3) Update public href generation centrally

Patch `src/features/content/data.ts` so demo href generation prefers the short AIP route when the managed content ID matches a mapped AIP entry.

Pattern:

- `getPublicDetailHref("demo", locale, slug)`
  - return `getAipDemoHrefByContentId(...)` when available
  - otherwise keep existing `/features/demo/:slug`

This step is critical because it automatically updates:

- listing links
- related post links
- any code paths already using `getPublicDetailHref`
- sitemap entries that derive URLs from the same helper

## 4) Add the canonical short route page

Create:

- `src/app/[locale]/demo/aip/[id]/[[...rest]]/page.tsx`

Recommended approach:

1. validate locale
2. resolve the short route with `resolveAipDemoRoute`
3. redirect if slug is missing, wrong, or extra path segments exist
4. load the managed demo item with `readContentItem("demo", contentId, ...)`
5. reuse the same gating / related-item / fallback rendering pattern as `features/demo/[slug]/page.tsx`
6. set metadata canonical to the short route

Important lesson:

- reuse managed rendering rather than introducing MDX just because the public path changed
- keep thumbnail handling consistent with the managed demo route by using `getContentThumbnailSrc(...)` for related items

## 5) Add legacy redirects

Create:

- `src/app/[locale]/features/demo/aip-features/[id]/[[...rest]]/page.tsx`

This route should:

- redirect `/features/demo/aip-features/:id/...` to `getAipDemoHref(locale, id)`
- `notFound()` when the mapped ID is unknown

Also patch the existing managed route:

- `src/app/[locale]/features/demo/[slug]/page.tsx`

Add an early redirect so when the managed content ID is a mapped AIP item, the page redirects to the short canonical route instead of rendering under `/features/demo/:slug`.

Also update `generateMetadata` there so canonical points to the short route for mapped AIP items.

## 6) Be careful with sitemap duplication

Check `src/app/sitemap.ts` after updating `getPublicDetailHref`.

Important finding:

- once `demoEntries` already uses `getPublicDetailHref("demo", ...)`, AIP short URLs are included automatically
- if you also add a separate explicit `aipDemoEntriesShort` block, you create duplicate sitemap entries

So for this managed-route pattern:

- update `getPublicDetailHref`
- let `demoEntries` pick up the short URL automatically
- do not add a second explicit sitemap block unless there is a route family not covered by managed content state

This differs from ACP MDX routes, where explicit sitemap wiring was needed because those pages were not driven by the managed demo detail route.

## 7) Tests to add

Add:

- `src/features/demo/aip.test.ts`
  - mapping lookup
  - canonical href generation
  - contentId -> href mapping
  - redirect decision for missing/wrong slug
- `src/features/content/data.test.ts`
  - `getPublicDetailHref("demo", ...)` returns `/demo/aip/1/google-oauth-demo` for the mapped AIP entry
  - non-mapped demo entries still return `/features/demo/:slug`

A good targeted validation set is:

- `npm run test:run -- src/features/demo/aip.test.ts src/features/demo/acp.test.ts src/features/content/data.test.ts src/features/mdx/loader.test.ts`
- `npm run build`

# PR follow-up workflow note

If this request arrives after an existing demo migration PR is already open:

1. inspect the open PR with `gh pr view`
2. use the same PR branch in a fresh worktree
3. commit the AIP route change as a focused follow-up commit
4. push to the existing PR branch instead of opening a new PR

# Pitfalls

- Do not over-generalize the ACP MDX migration pattern onto AIP.
- Do not manually add separate sitemap AIP entries if `demoEntries` already derives them from `getPublicDetailHref`; that causes duplication.
- Do not skip updating canonical metadata on `features/demo/[slug]/page.tsx`; otherwise search engines may still see the old managed path as canonical.
- Do not forget that `en` routes omit the `/en` prefix when validating expected URLs.

# Verification checklist

- `/demo/aip/1/google-oauth-demo` resolves correctly
- `/demo/aip/1` redirects to `/demo/aip/1/google-oauth-demo`
- `/features/demo/aip-features/1/google-oauth-demo` redirects to `/demo/aip/1/google-oauth-demo`
- `/features/demo/google-oauth-demo` redirects to `/demo/aip/1/google-oauth-demo`
- `getPublicDetailHref("demo", "en", "google-oauth-demo")` returns `/demo/aip/1/google-oauth-demo`
- unrelated demo items still use `/features/demo/:slug`
- targeted tests pass
- `npm run build` passes
