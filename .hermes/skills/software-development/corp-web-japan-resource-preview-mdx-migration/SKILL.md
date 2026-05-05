---
name: corp-web-japan-resource-preview-mdx-migration
description: Rebuild corp-web-japan resource preview families like glossary, introduction-deck, and manuals as local MDX-backed preview/detail routes with category-specific loaders, route-aligned thumbnails, and test files mirrored to source paths.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, resources, mdx, preview, abstract-class, tests, thumbnails]
---

# corp-web-japan resource preview MDX migration

Use this when a redirect-backed resource family in `corp-web-japan` should be migrated from hardcoded preview items into local MDX-backed preview/detail routes.

Typical targets:
- `/t/introduction-deck`
- `/t/glossary`
- `/t/manuals`
- shared hub `/t/resources`

## When to use

Use this when:
- the current preview is only a hardcoded card array
- the user wants category types treated independently, like blog/whitepaper/event
- the family should use local MDX sources plus local detail routes
- the user wants reusable structure but not one giant grouped `documentation` loader module

## Core outcome

Do **not** keep one grouped loader like:
- `src/lib/documentation-publications.ts`
- `src/lib/get-documentation-publication-post.ts`

Instead split into:
- shared `resource` base layer
- category-specific concrete publication loaders
- category-specific concrete post loaders

Recommended structure:
- `src/lib/resources/types.ts`
- `src/lib/resources/base-resource-publication.ts`
- `src/lib/resources/base-resource-publication-post-loader.ts`
- `src/lib/resources/introduction-deck-publications.ts`
- `src/lib/resources/introduction-deck-post-loader.ts`
- `src/lib/resources/glossary-publications.ts`
- `src/lib/resources/glossary-post-loader.ts`
- `src/lib/resources/manual-publications.ts`
- `src/lib/resources/manual-post-loader.ts`
- `src/lib/resources/resource-preview-items.ts`

## TypeScript class guidance

TypeScript supports:
- `abstract class`
- normal concrete `class`

There is no special `concrete` keyword.

Use the base layer to hold:
- frontmatter parsing
- disk loading
- cache setup
- shared list-item mapping
- shared post rendering pipeline

Use the concrete classes to hold:
- category string
- badge label
- content root path
- any category-specific policy

## Content layout

Keep local MDX under route-family-aligned directories:
- `src/content/documentation/introduction-deck/*.mdx`
- `src/content/documentation/glossary/*.mdx`
- `src/content/documentation/manuals/*.mdx`

Use frontmatter shaped similarly to publication content:
- `id`
- `slug`
- `title`
- `description`
- `heroImageSrc`
- optional `date`
- optional `gated`
- optional `relatedItems`

For gated intro-deck style content, reuse the existing whitepaper-style contract:
- `gated: true`
- `<GatingCut />`
- gated content rendered by the shared MDX publication renderer

## Detail route pattern

For each category, create both:
- `src/app/t/<category>/[id]/page.tsx`
- `src/app/t/<category>/[id]/[slug]/page.tsx`

Rules:
- `[id]/page.tsx` redirects to canonical `[id]/[slug]`
- lookup key is the `id`
- slug mismatch redirects to canonical slug route
- preview detail metadata should use canonical `/t/...` and `noindex`
- render through `PublicationPostPage`

For gated categories, set the unlock cookie state in the detail page before rendering, same as the whitepaper flow.

## Shared hub pattern

`/t/resources` can stay a mixed preview hub, but it should not own the per-category loading logic.

Recommended:
- category-specific publication loaders return their own list items
- `resource-preview-items.ts` assembles the hub list from:
  - intro deck local list
  - glossary local list
  - manuals local list
  - any intended external manual cards
  - existing local whitepaper/blog items

## Thumbnail and asset rule

Do not leave these families on generic `public/documentation/docu-thumb-*.png` paths once the local MDX content exists.

Follow repo thumbnail convention with route-aligned public paths, for example:
- `/introduction-deck/1/thumbnail.png`
- `/introduction-deck/2/thumbnail.png`
- `/glossary/1/thumbnail.png`
- `/manuals/1/thumbnail.png`
- external/manual helper cards under route-aligned subpaths like:
  - `/manuals/aip-guide/thumbnail.png`
  - `/manuals/acp-guide/thumbnail.png`
  - `/manuals/api-docs/thumbnail.png`

If a detail page has related cards with their own thumbnails, colocate them similarly under the family path, e.g.:
- `/glossary/1/related-release-notes-thumbnail.png`

## Testing rule

Do not keep one umbrella test file for this whole family.

Mirror source paths in tests as much as practical:
- `tests/src/lib/resources/architecture.test.mjs`
- `tests/src/app/t/resources/page.test.mjs`
- `tests/src/app/t/introduction-deck/page.test.mjs`
- `tests/src/app/t/glossary/page.test.mjs`
- `tests/src/app/t/manuals/page.test.mjs`

Test split guidance:
- architecture test
  - abstract base exists
  - concrete loaders extend the base
  - grouped legacy loader modules are gone
- page tests
  - preview page exists
  - canonical `/t/...`
  - noindex metadata
  - route uses the intended category-specific loader
  - `[id]` and `[id]/[slug]` detail routes exist and use the matching category-specific post loader

## Safe PR rewrite pattern when the PR picked up unrelated commits

If the open PR branch includes unrelated commits:
1. create a fresh detached worktree from latest `origin/main`
2. create a temporary local branch there
3. copy only the intended scoped files from `origin/<pr-branch>`
4. verify the diff is only the intended resource-preview scope
5. run typecheck/tests/build
6. commit cleanly
7. force-push back to the same PR branch

This is safer than trying to clean a stale mixed branch in place.

## Verification

Minimum:
```bash
npm run typecheck
node --test tests/src/lib/resources/architecture.test.mjs \
  tests/src/app/t/resources/page.test.mjs \
  tests/src/app/t/introduction-deck/page.test.mjs \
  tests/src/app/t/glossary/page.test.mjs \
  tests/src/app/t/manuals/page.test.mjs
npm run test
npm run build
```

## Pitfalls

- keeping one grouped `documentation` type/loader after the user asked for independent category types
- leaving hardcoded preview item arrays as the real source of truth
- forgetting `[id]` redirect routes for the new categories
- keeping generic `docu-thumb-*` hero paths instead of route-aligned thumbnails
- using one umbrella test file instead of test paths that mirror the source layout
- rewriting the PR branch without first confirming unrelated commits really exist

## Done criteria

- introduction-deck, glossary, and manuals are independent resource types
- shared logic lives in abstract base classes under `src/lib/resources/`
- category-specific concrete loaders exist
- preview/detail routes use category-specific loaders
- thumbnails use route-aligned public paths
- tests are split by module/path and pass
- the existing PR branch is updated cleanly
