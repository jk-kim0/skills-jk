---
name: corp-web-japan-seo-metadata-routes
description: Implement or update robots, sitemap, and canonical metadata in corp-web-japan without regressing final page-title decisions or route conventions.
version: 1.0.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, seo, nextjs, metadata, sitemap, robots, canonical]
    related_skills: [corp-web-japan-origin-main-worktree-safety, test-driven-development, github-pr-workflow]
---

# corp-web-japan SEO metadata routes

Use when the task involves any of the following in `corp-web-japan`:
- adding or updating `src/app/robots.ts`
- adding or updating `src/app/sitemap.ts`
- adding or updating page `canonical` metadata
- aligning public page metadata with the current implemented route set

## Goal

Implement SEO baseline metadata in a way that matches the repository's actual public routes and preserves already-decided title/branding text.

## Required approach

1. Start from the latest `origin/main` in a fresh worktree.
   - Do not trust a dirty local `main` checkout for metadata text or route state.
   - Confirm open PRs before changing anything.

2. Read the current page files before patching.
   - In this repo, title text may already have been finalized in another PR.
   - Do not rewrite titles just because older local files show different strings.

3. Add a shared site URL helper if needed.
   - A small `src/lib/site-url.ts` helper is a clean source for:
     - `metadataBase`
     - canonical URLs
     - sitemap URLs
     - robots sitemap/host values

4. Update root metadata first.
   - Add `metadataBase` in `src/app/layout.tsx`.
   - Then add page-level `alternates.canonical` only where needed.

5. Build `sitemap.ts` from actual implemented public routes.
   - Include only routes that are currently real public pages.
   - Exclude routes that currently resolve to `notFound()`.
   - Keep the sitemap aligned with final URI conventions.

6. For resource routes, preserve current route reality.
   - If post routes still exist locally, sitemap/canonical may include them.
   - Do not remove them as part of SEO work unless the task explicitly includes route removal.

7. Add a regression test.
   - Verify:
     - `metadataBase` exists
     - `robots.ts` declares sitemap and host
     - expected canonical entries exist
     - `sitemap.ts` includes implemented public routes
     - `sitemap.ts` excludes known non-public routes

8. Run full verification.
   - `npm run test:ci`
   - `npm run build`

## Repo-specific pitfalls

### 1. Preserve title decisions
A prior PR may already have finalized page titles. Do not overwrite those strings while adding canonical metadata.

### 2. Use `/whitepapers`, not `/whitepaper`
For the resource index, the intended final route is `/whitepapers`.
Keep sitemap and canonical values aligned with that path.

### 3. Do not blindly include `/events`
If `src/app/events/page.tsx` currently calls `notFound()`, do not add `/events` to `sitemap.ts`.
Only include it once the page is actually implemented.

### 4. Keep page metadata and sitemap aligned
When adding, removing, or renaming a public page:
- update the page's canonical metadata
- update the matching `src/app/sitemap.ts` entry in the same change

### 5. Partial issue progress must not auto-close the issue
If the PR only addresses part of a broader issue, do not use `Closes #...` in the PR body.
Use neutral wording such as:
- `partial progress for #62`
- `related to #62`

## Suggested file targets

- `src/lib/site-url.ts`
- `src/app/layout.tsx`
- `src/app/robots.ts`
- `src/app/sitemap.ts`
- relevant public page files under `src/app/**/page.tsx`
- `tests/seo-metadata.test.mjs`

## Verification checklist

- [ ] no title strings were unintentionally changed
- [ ] `metadataBase` is set
- [ ] canonical metadata exists for affected public pages
- [ ] sitemap entries reflect actual implemented routes
- [ ] no known `notFound()` page is listed in the sitemap
- [ ] `npm run test:ci` passes
- [ ] `npm run build` passes
- [ ] PR body references broader issues without auto-closing them when work is partial
