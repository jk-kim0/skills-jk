---
name: corp-web-japan-documentation-preview-mdx-migration
description: Rebuild corp-web-japan documentation preview routes so /t/resources, /t/introduction-deck, /t/glossary, and /t/manuals use local MDX content, loaders, and detail routes instead of hardcoded preview cards.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, documentation, mdx, preview-routes, gating, worktree]
---

# corp-web-japan documentation preview MDX migration

Use this when the user wants the documentation/resource preview area to behave like the local blog/whitepaper systems rather than a temporary hardcoded preview list.

Typical targets:
- `/t/resources`
- `/t/introduction-deck`
- `/t/glossary`
- `/t/manuals`

## When to use

Use this skill when:
- a redirect-backed documentation endpoint in corp-web-japan needs a real local preview implementation
- the user rejects hardcoded preview cards and wants MDX-backed content instead
- glossary, introduction-deck, or manuals should follow the same local-content pattern as blog/whitepaper

Do not use this for:
- ordinary blog/whitepaper posting work
- legal preview routes
- demo/use-case/news/event migration work

## Required source of truth

Inspect these sibling-repo sources first:
- `../corp-web-contents/pages/features/documentation/ja/content.mdx`
- `../corp-web-contents/layout/ja/article-category.json`
- `../corp-web-contents/pages/features/documentation/aip-introduction-download/ja/content.mdx`
- `../corp-web-contents/pages/features/documentation/acp-introduction-download/ja/content.mdx`
- `../corp-web-contents/pages/features/documentation/glossary-items/ja/content.mdx`
- `../corp-web-contents/pages/features/documentation/querypie-install-guide/ja/content.mdx`
- `../corp-web-app/src/components/mdx-layout/article-list/**`

Important interpretation:
- `resources` is a mixed hub, not one homogeneous local content family
- `introduction-deck` entries are gated download-style content
- `glossary` is an article detail route family
- `manuals` is a mixed category: at least one local article plus external manual/API links

## Key lesson: do NOT stop at hardcoded preview arrays

If the user wants parity with blog/whitepaper behavior, a preview-only item array is not enough.

The correct direction is:
1. create local MDX source files under `src/content/documentation/**`
2. add a loader that reads frontmatter from those local MDX files
3. add detail routes with id-only redirect + canonical slug route
4. render detail pages through the shared MDX/publication pipeline
5. keep only genuinely external manual links as external list items

## Recommended file layout

Use route-aligned content families:
- `src/content/documentation/introduction-deck/*.mdx`
- `src/content/documentation/glossary/*.mdx`
- `src/content/documentation/manuals/*.mdx`

Recommended loader files:
- `src/lib/documentation-publications.ts`
- `src/lib/get-documentation-publication-post.ts`

Recommended preview routes:
- `src/app/t/resources/page.tsx`
- `src/app/t/introduction-deck/page.tsx`
- `src/app/t/introduction-deck/[id]/page.tsx`
- `src/app/t/introduction-deck/[id]/[slug]/page.tsx`
- `src/app/t/glossary/page.tsx`
- `src/app/t/glossary/[id]/page.tsx`
- `src/app/t/glossary/[id]/[slug]/page.tsx`
- `src/app/t/manuals/page.tsx`
- `src/app/t/manuals/[id]/page.tsx`
- `src/app/t/manuals/[id]/[slug]/page.tsx`

## Loader design

Mirror the blog/whitepaper pattern:
- read all MDX files in the family directory
- parse frontmatter with YAML
- cache records in memory
- expose:
  - `list...Items()` for list pages
  - `list...Params()` / `list...Ids()` for routes
  - `get...Record()` for canonical redirect lookup
  - `get...Post()` for rendered detail page data

Useful frontmatter shape for documentation families:
- `id`
- `slug`
- `title`
- `description`
- `heroImageSrc`
- optional `date`
- optional `gated: true`
- optional `relatedItems`

## Gated introduction-deck rule

For `introduction-deck`, do not fake the download behavior with a plain list card.

Use the existing whitepaper-style gating contract:
- keep the preview body in MDX
- insert `<GatingCut />`
- render through the shared MDX renderer
- use `buildGatingContentKey(...)`
- use `splitMdxSourceAtGatingCut(...)`
- use the existing `PublicationPostPage` + `ResourcePostGated` flow

Practical pattern:
- preview body describes the document
- gated section contains a `ButtonLink` to the final PDF URL

## Build-safety rule: do not read sibling repos at runtime/build on Vercel

A failed approach was reading `../corp-web-contents/...` directly during app build/runtime.
That works locally but fails in Vercel/CI because the sibling repo is not present in deployment.

Correct approach:
- copy or recreate the needed MDX source inside this repo under `src/content/documentation/**`
- copy required assets into this repo under `public/documentation/**`
- loaders should read only repo-local files under `process.cwd()`

This is critical for preview deploy success.

## Asset handling

Copy required static assets into local `public/documentation/**`.
Typical files include:
- intro deck thumbnails
- glossary thumbnail
- glossary related-item thumbnails
- install guide screenshots
- manual/API thumbnails

Do not leave the preview depending on sibling-repo filesystem paths at build time.

## MDX component compatibility

Documentation MDX can require components beyond the minimal blog/whitepaper set.

At minimum, ensure the shared MDX component registry supports local documentation content such as:
- `Link`
- `ButtonLink`
- `Table`
- `Box`
- `ArticleFileImage`
- `GatingCut`

Practical lesson:
- if imported documentation MDX uses `<Link ...>` and the shared renderer does not expose `Link`, the build will fail during prerender
- add a shared `Link` MDX component that handles both internal and external links

## Publication page compatibility adjustments

When reusing `PublicationPostPage` for documentation content:
- allow empty/missing `date` values without ugly blank text
- hide the related section when `relatedItems.length === 0`
- keep TOC/related/sidebar behavior generic enough for documentation posts

## `/t/resources` composition rule

`/t/resources` is a mixed preview hub.
A good composition is:
- local MDX-backed `introduction-deck`, `glossary`, and local `manuals` items
- external manual/API links that remain external
- existing local whitepaper items
- existing local blog items

Do not pretend every resources entry has a local detail page if some are intentionally external.

## Navigation rule

If preview navigation is enabled in non-production, resource links in header/footer should point to preview routes via `t(path, previewModeEnabled)`:
- `/resources`
- `/introduction-deck`
- `/glossary`
- `/manuals`

## Verification

Run at least:
```bash
npm run typecheck
node --test tests/documentation-preview-routes.test.mjs
npm run test
npm run build
npm run test:ci
```

Useful assertions to add/update:
- preview list pages exist and are `noindex`
- loaders read local MDX, not hardcoded arrays
- detail route families exist for intro/glossary/manuals
- id-only pages redirect to canonical slug pages
- shared navigation tests expect preview-aware resource links

## Pitfalls

- using hardcoded preview cards when the user asked for MDX-backed parity
- reading sibling repo files directly during Vercel build/runtime
- forgetting to add a shared MDX `Link` component
- treating all manuals entries as local when some should remain external
- forgetting id-only redirect pages for canonical detail routes
- leaving shared publication components unable to handle empty `date` or empty `relatedItems`

## Done criteria

- `/t/resources` uses a real local documentation loader
- `introduction-deck`, `glossary`, and local `manuals` content live under `src/content/documentation/**`
- detail routes exist and render via the shared MDX/publication flow
- intro deck uses the gating contract instead of hardcoded mock behavior
- builds succeed on local/Vercel because no sibling-repo runtime dependency remains
