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

## Redirect-backed MDX detail rule

For local MDX-backed detail routes such as:
- `src/app/blog/[id]/[slug]/page.tsx`
- `src/app/whitepapers/[id]/[slug]/page.tsx`
- `src/app/news/[id]/[slug]/page.tsx`
- `src/app/events/[id]/[slug]/page.tsx`
- `src/app/use-cases/[id]/[slug]/page.tsx`
- `src/app/demo/aip/[id]/[slug]/page.tsx`
- `src/app/demo/acp/[id]/[slug]/page.tsx`

follow this contract when a record has `redirectUrl`:
- normal human visitors should still be redirected to `record.redirectUrl`
- search bots should **not** be redirected away from the local detail page
- instead, bots should receive the local detail content with a normal `200 OK` render
- keep `alternates.canonical` pointed at the local canonical detail path such as `absoluteUrl(getNewsPublicationHref(id, record.slug))`
- for these redirect-backed local detail pages, metadata should remain indexable (`robots.index = true`, `robots.follow = true`) so search crawlers can index the local content they are allowed to render

Recommended implementation pattern:
- centralize the user-agent check in a shared helper such as `src/lib/publications/redirectable-publication-request.ts`
- expose a small helper like `shouldRedirectHumanVisitorFromRedirectablePublication()` that reads `headers()` and returns `false` for search-bot user agents
- in the detail route, gate the redirect with that helper:
  - `if (record.redirectUrl && await shouldRedirectHumanVisitorFromRedirectablePublication()) redirect(record.redirectUrl)`
- apply the same human-only redirect rule to the `/[id]` canonicalization routes so bots are sent to the local canonical slug path rather than out to `redirectUrl`

For `src/app/sitemap.ts`:
- include `/news` list route in the static routes
- include `/news/:id/:slug` detail entries from `newsPublicationRecords`
- when the product decision is that redirect-backed local content should still be indexable for bots, do **not** filter out `redirectUrl` records from sitemap detail entries
- apply the same inclusion rule consistently to other redirect-backed MDX families such as blog, whitepaper, and event detail routes when they are intended to expose local crawlable content

## MDX-backed sitemap coverage rule

When auditing `corp-web-japan` sitemap coverage for implemented local MDX content, do not stop at the list pages. Check every currently implemented local canonical detail family against `src/app/sitemap.ts`.

Latest known public MDX-backed detail families to verify:
- blog -> `/blog/:id/:slug`
- whitepapers -> `/whitepapers/:id/:slug`
- news -> `/news/:id/:slug`
- events -> `/events/:id/:slug`
- use-cases -> `/use-cases/:id/:slug` canonical detail, even though the list page is `/demo/use-cases`
- AIP demo -> `/demo/aip/:id/:slug`
- ACP demo -> `/demo/acp/:id/:slug`
- introduction-deck -> `/introduction-deck/:id/:slug`
- glossary -> `/glossary/:id/:slug`
- manuals -> `/manuals/:id/:slug`

Practical audit pattern:
1. read `src/app/sitemap.ts`
2. read the implemented detail routes under `src/app/**/[id]/[slug]/page.tsx`
3. inspect the publication/content record sources under `src/lib/publications/**` and `src/lib/resources/**`
4. compare the sitemap families against the actual local MDX-backed families
5. add missing detail-route families to the sitemap
6. for any family that supports `hidden` and `redirectUrl`, apply this sitemap rule explicitly:
   - hidden-only records must be excluded from sitemap detail entries
   - hidden records that also have `redirectUrl` must still be included in sitemap detail entries
   - visible records remain included as usual

Important known finding:
- latest-main audit found that blog and whitepaper detail routes were implemented but missing from `src/app/sitemap.ts`
- later follow-up clarified the intended corp-web-japan rule: `hidden` alone should keep a record out of sitemap, but `hidden + redirectUrl` is a bot-indexable local-canonical shadow record and must remain in sitemap
- current hidden+redirectUrl examples exist in blog, whitepaper, and event corpora; use them as regression fixtures when available

Regression-test expectation:
- add or update a test that asserts `src/app/sitemap.ts` covers the implemented MDX-backed public detail families
- verify blog/whitepaper/news/event families by their helper imports or route builders
- verify the hidden-vs-redirect contract explicitly:
  - `hidden` without `redirectUrl` is excluded
  - `hidden` with `redirectUrl` is included

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
