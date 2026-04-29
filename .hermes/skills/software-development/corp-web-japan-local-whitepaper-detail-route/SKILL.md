---
name: corp-web-japan-local-whitepaper-detail-route
description: Implement local corp-web-japan whitepaper detail routes at /whitepapers/:id/:slug using checked-in MDX source with frontmatter, while keeping the /whitepapers list page unchanged in behavior and canonicalizing id/slug URLs.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, nextjs, routing, whitepaper, canonical, mdx, frontmatter]
    related_skills: [corp-web-japan-origin-main-worktree-safety, nextjs-id-slug-canonical-route, github-pr-workflow]
---

# corp-web-japan local whitepaper detail route pattern

Use this when the user wants local whitepaper detail pages in `corp-web-japan`, with:
- `/whitepapers` list page behavior left unchanged
- detail pages served locally at `/whitepapers/:id/:slug`
- `/whitepapers/:id` and `/whitepapers/:id/` resolving correctly
- wrong slugs redirected to the canonical slug
- implementation style aligned with the local blog publication pattern
- whitepaper source managed as checked-in MDX with frontmatter, not HTML snapshots

## Important update

Earlier versions of this workflow used checked-in HTML snapshots when no local MDX existed.

Current preferred approach:
- use Japanese MDX source from `../corp-web-contents` or `../corp-web-v2`
- check the content into `corp-web-japan` as local MDX files
- store required metadata in frontmatter
- derive the `/whitepapers` list items from those MDX frontmatter records
- remove the need for a separate hardcoded `src/content/publications/whitepapers.ts`

This is more consistent with the local blog publication structure and keeps source content editable.

## When to use

Use this workflow when:
- local whitepaper detail pages must be added without changing `/whitepapers` page behavior
- the repo already has or can recover Japanese MDX source for those whitepapers
- the user explicitly wants MDX/frontmatter consistency with the blog implementation
- the current implementation or plan still depends on HTML snapshots or a duplicated hardcoded whitepaper list file

## Core approach

1. If updating an open PR, use a fresh worktree on the existing PR branch.
2. Inspect the existing local publication pattern first:
   - `src/content/blog/*.mdx`
   - `src/lib/publications/get-publication-post.ts`
   - `src/app/blog/[id]/[slug]/page.tsx`
   - `src/app/blog/[id]/page.tsx` if present in follow-up work
3. Locate Japanese MDX source in adjacent repos:
   - `../corp-web-contents/pages/features/documentation/white-paper/<id>/<slug>/ja/content.mdx`
   - or `../corp-web-v2/src/content/mdx/white-paper/<id>/ja.mdx`
4. Copy or normalize those whitepapers into local checked-in MDX files under `src/content/whitepaper/`.
5. Convert all required metadata into frontmatter fields that mirror the blog pattern.
6. Create a whitepaper publication registry module that reads MDX files from disk and derives list/detail records.
7. Update the thin helper + thin routes to render whitepapers via MDX.
8. Add or update a source-level regression test for the canonical routing contract and the MDX-based list source.
9. Commit, push, and update the PR.

## Preferred file shape

Important naming rule learned in follow-up work:
- use plural `whitepapers` consistently for local repository-managed content and asset paths
- do not mix `whitepaper`, `white-paper`, and `whitepapers` for local checked-in paths
- upstream public URLs on `querypie.com` may still legitimately use legacy `/features/documentation/white-paper/...` and should not be mass-renamed

Preferred local file shape:

- `src/content/whitepapers/<id>.mdx`
- `src/content/publications/whitepapers.ts`
- `src/lib/publications/get-whitepaper-publication-post.ts`
- `src/app/whitepapers/[id]/[slug]/page.tsx`
- `src/app/whitepapers/[id]/page.tsx`
- `public/whitepapers/<id>/*`

Important asset convention learned later:
- use `heroImageSrc: "/whitepapers/<id>/thumbnail.png"`
- keep the thumbnail file colocated with the rest of that whitepaper's body assets under `public/whitepapers/<id>/`
- do not keep a parallel legacy thumbnail copy under `public/assets/image/whitepapers/<id>/thumbnail.png`
- if both paths exist, treat the route-aligned `public/whitepapers/<id>/thumbnail.png` file as canonical and remove the duplicate after updating references

Do not keep these legacy files once migrated:
- `src/content/publications/whitepaper.ts`
- `src/content/publications/whitepaper-posts.ts`
- `src/content/whitepaper/*.html`
- `src/content/whitepaper/*.mdx`
- `public/white-paper/**`

## Frontmatter contract

For each local whitepaper MDX file, use a frontmatter shape close to the blog files:

```yaml
---
id: "28"
slug: "ai-agent-guardrails-governance-2026"
title: "..."
description: "..."
listDescription: "..."
date: "2026年2月27日"
heroImageSrc: "/whitepapers/28/thumbnail.png"
author: "querypie"
relatedIds:
  - "23"
  - "22"
  - "21"
---
```

Notes:
- `listDescription` is useful because list-card copy may intentionally differ from full article description.
- Keep `date` in the display format used by the local site if the renderer expects display-ready dates.
- Prefer local `author` ids that already exist in `src/content/authors/ja.yaml`.
- If an author id is missing, add it to the registry instead of hardcoding author metadata in a separate TypeScript table.

## Source recovery and normalization

### Preferred source lookup order

1. `corp-web-v2` migrated MDX if it already has normalized route-aligned public asset paths and cleaned frontmatter
2. `corp-web-contents` original Japanese MDX if needed for fidelity or missing pages

### Typical recovery paths

Examples:
- `../corp-web-v2/src/content/mdx/white-paper/28/ja.mdx`
- `../corp-web-contents/pages/features/documentation/white-paper/28/ai-agent-guardrails-governance-2026/ja/content.mdx`

### Normalize during import

Common transformations that mattered in practice:
- add local frontmatter fields: `id`, `slug`, `listDescription`, `heroImageSrc`, `author`, `relatedIds`
- convert or preserve the final local title exactly as desired for `corp-web-japan`
- rewrite supported internal whitepaper links to local `/whitepapers/<id>/<slug>` routes
- keep unsupported whitepaper links external to `querypie.com` instead of creating broken local routes
- convert other `/features/...` links that are not implemented locally into `https://www.querypie.com/ja/...` absolute URLs
- remove duplicated top thumbnail blocks if the page shell already renders the hero image from frontmatter

## Deriving the list page data from MDX

Instead of a hardcoded `src/content/publications/whitepapers.ts`, create a module like `src/content/publications/whitepaper.ts` that:
- reads `src/content/whitepaper/*.mdx`
- parses frontmatter
- exposes `whitepaperPublicationRecords`
- exports `whitepaperItems` derived from those records for `/whitepapers`
- exports `listWhitepaperPublicationParams()`
- exports `listWhitepaperPublicationIds()`
- exports `getWhitepaperPublicationRecord(id)`

This removes duplicate metadata tables and keeps list/detail data in sync.

## Detail helper pattern

In `src/lib/publications/get-whitepaper-publication-post.ts`:
- read the MDX source from `record.sourcePath`
- render via the existing publication MDX renderer (`renderPublicationMdx`)
- resolve author through `resolveArticleAuthors()`
- generate `relatedItems` from `relatedIds`
- generate TOC with `extractHeadingsFromMdx()`
- expose `getWhitepaperPublicationPost(id)` using id-only lookup
- expose `getWhitepaperPublicationHref(id, slug)` via `getPublicationHref("whitepaper", ...)`

Important: the content loader should remain id-only. Do not make the helper slug-sensitive.

## MDX component support

Whitepaper MDX often uses more custom components than the local blog posts.

Before finalizing the migration, inspect the selected MDX pages for component usage. The minimum additions that proved useful were:
- `Table`
- `Box`
- `ButtonLink`
- `ArticleFileImage`
- `ArticleGatingForm`
- `InfoNote`

Recommended behavior for these local render components:
- `ButtonLink`: internal links use `Link`, external links use `<a target="_blank" rel="noopener noreferrer">`
- `ArticleFileImage`: normalize `public/...` file paths to `/...` and render a simple figure/img/caption block
- `ArticleGatingForm`: if the local site does not support full gating behavior yet, keep the gated source wrapper in MDX but render children pass-through rather than breaking the page
- `Box`: minimal alignment wrapper is usually enough
- `InfoNote`: provide a simple local note/callout renderer, including support for upstream props like `hideIcon`

Important CI lesson:
- do not assume only the obvious components (`Table`, `Box`, `ButtonLink`, `ArticleFileImage`) are needed
- after migrating MDX, audit the imported files for additional custom components such as `InfoNote`
- if one is missing, `next build` can fail during prerender with errors like `Expected component \`InfoNote\` to be defined`
- when CI fails this way, patch the publication MDX component registry first before assuming the content itself is broken

This lets the local MDX render without needing the full upstream component system.

## Gated-source preservation rule

Important follow-up lesson:
- some imported whitepapers are intentionally authored with `ArticleGatingForm` sections in upstream MDX
- if the local site does not yet implement the actual gating UX, do NOT strip those wrappers from the source just to make the page render
- instead:
  1. preserve the gated source structure in the checked-in MDX
  2. keep `ArticleGatingForm` as a temporary no-op renderer so the current page remains fully readable
  3. add a source-level regression test confirming the wrapper still exists in the MDX while current rendering remains ungated
  4. open a GitHub issue documenting the later work needed to implement the real gating form and apply it to the affected whitepapers

This preserves fidelity to the source content while making the current implementation safe and reviewable.

## Asset migration

Whitepaper MDX usually references many checked-in images. Copy the necessary assets into local public paths, ideally preserving route-aligned organization.

Use this convention consistently:
- all whitepaper-owned assets, including the hero thumbnail, live under `public/whitepapers/<id>/`
- the frontmatter `heroImageSrc` should point at `/whitepapers/<id>/thumbnail.png`
- supporting surfaces such as home-page cards and internal gating demos should reference the same route-aligned thumbnail path

Useful examples:
- `public/whitepapers/21/**`
- `public/whitepapers/22/**`
- `public/whitepapers/23/**`
- `public/whitepapers/24/**`
- `public/whitepapers/26/**`
- `public/whitepapers/28/**`

Important duplicate-file cleanup lesson:
- older repo state may still have thumbnail copies under `public/assets/image/whitepapers/<id>/thumbnail.png`
- verify whether the duplicate files are byte-identical before deleting them
- if they differ, inspect which one is the intended localized/canonical thumbnail and copy that version into `public/whitepapers/<id>/thumbnail.png` before removing the legacy duplicate

Also verify any author image paths referenced through the author registry. If an author profile image path is invalid locally, either:
- copy the missing asset, or
- normalize the author registry to a known local asset such as `querypie-logo.svg`

## Canonical routing

Keep the same id/slug canonicalization contract:

### Canonical route
`src/app/whitepapers/[id]/[slug]/page.tsx`
- load record by `id`
- `notFound()` if missing
- redirect when `record.slug !== slug`
- render the post loaded by `id` only
- `generateMetadata()` sets canonical URL using stored slug

### ID-only redirect route
`src/app/whitepapers/[id]/page.tsx`
- load record by `id`
- `notFound()` if missing
- redirect to `/<section>/<id>/<canonical-slug>`

## Testing

Add or update a source-level test such as `tests/whitepaper-canonical-slug-routing.test.mjs`.

Recommended assertions:
- `[id]/[slug]/page.tsx` reads record by `id`
- slug mismatch redirects to canonical href
- full post load calls `getWhitepaperPublicationPost(id)` rather than `(id, slug)`
- `[id]/page.tsx` exists and redirects canonically
- checked-in MDX source files exist
- `src/content/publications/whitepapers.ts` no longer exists
- `/whitepapers` page imports `whitepaperItems` from `@/content/publications/whitepaper`
- the publication registry reads `.mdx` files from `src/content/whitepaper`
- whitepaper MDX frontmatter no longer references the legacy `/assets/image/whitepapers/` thumbnail path
- supporting surfaces such as top-page cards or internal whitepaper demos also avoid the legacy thumbnail path

This is a good fit for the repo because it locks in the route/data-source contract without requiring a local dev server.

## Verification

Preferred lightweight verification:

```bash
git diff --check
node --test tests/*.test.mjs
```

If worktree-local TypeScript dependencies are missing, note that explicitly and rely on CI unless the user explicitly requests a local install.

## Pitfalls

- keeping a duplicated hardcoded `whitepapers.ts` alongside MDX frontmatter
- leaving the helper slug-sensitive after adding redirect logic
- migrating only the body but forgetting required whitepaper assets
- not supporting upstream MDX custom components, causing render failures
- rewriting links to unsupported local whitepapers and creating new 404s
- leaving invalid author image paths from upstream metadata
- changing `/whitepapers` page behavior when the user only asked to change the source implementation

## Done criteria

- `/whitepapers/:id/:slug` renders from local MDX
- `/whitepapers/:id` redirects to canonical slug URL
- wrong slugs redirect correctly
- `/whitepapers` behavior remains intact
- whitepaper list items are derived from MDX frontmatter
- separate hardcoded `whitepapers.ts` is removed
- local whitepaper assets needed by the MDX are checked in
- unsupported related/download links still resolve externally rather than breaking locally
- regression tests cover the MDX-based canonical routing contract
