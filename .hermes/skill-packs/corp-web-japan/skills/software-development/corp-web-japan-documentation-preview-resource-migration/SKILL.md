---
name: corp-web-japan-documentation-preview-resource-migration
description: Rebuild corp-web-japan documentation/resource preview routes under /t/* as local MDX-backed resource publications, with category-specific loaders, route/file-path-aligned tests, and source-path-aligned public thumbnails.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, documentation, mdx, preview-routes, resources, tests, assets]
---

# corp-web-japan documentation preview resource migration

Use this when `/resources`, `/introduction-deck`, `/glossary`, or `/manuals` still redirect upstream, but the user wants local preview implementations under `/t/*` backed by local MDX and reviewable in an open PR.

## When to use
- Migrate documentation-like resources from `../corp-web-contents/pages/features/documentation/**`
- Replace hardcoded preview item arrays with real local MDX-backed list/detail routes
- Split grouped documentation loaders into category-specific implementations
- Align hero thumbnails and related preview images with MDX source paths under `src/content/documentation/**`

## Core user expectations
- Do not keep these categories grouped as one synthetic `documentation` type if the user wants them treated like distinct families.
- `glossary`, `introduction-deck`, and `manuals` should behave like separate publication types, analogous to blog / whitepaper / event.
- If shared logic is needed, prefer a `resource` abstract base plus per-category concrete implementations.
- Test files should mirror source paths they cover, e.g. `tests/src/app/t/...` and `tests/src/lib/resources/...`.
- For documentation-resource MDX, public hero/thumbnail asset paths should match the MDX source family path under `src/content/documentation/**`, not a flat `public/documentation/docu-thumb-*.png` naming scheme.

## Proven structure

### Content
Store local MDX under:
- `src/content/documentation/introduction-deck/*.mdx`
- `src/content/documentation/glossary/*.mdx`
- `src/content/documentation/manuals/*.mdx`

Use frontmatter like:
- `id`
- `slug`
- `title`
- `description`
- `heroImageSrc`
- optional `date`
- optional `gated: true`
- optional `relatedItems`

For introduction-deck items that represent gated downloads, use the existing whitepaper-style gating contract:
- local preview content in the visible body
- `<GatingCut />`
- gated tail section with `ButtonLink` to the download URL

### Shared loader base
Create a shared resource layer under:
- `src/lib/resources/types.ts`
- `src/lib/resources/base-resource-publication.ts`
- `src/lib/resources/base-resource-publication-post-loader.ts`

Recommended pattern:
- `BaseResourcePublicationRepository` (abstract class)
  - reads MDX files from one category root
  - parses frontmatter
  - caches records / params / list items
- `BaseResourcePublicationPostLoader` (abstract class)
  - reads cached MDX source
  - renders body via `renderPublicationMdx`
  - handles optional gating with `splitMdxSourceAtGatingCut`
  - maps `relatedItems`
  - exposes `getHref`, `getRecord`, `listParams`, `listIds`, `getPost`

### Per-category concrete implementations
Implement separate files such as:
- `src/lib/resources/introduction-deck-publications.ts`
- `src/lib/resources/introduction-deck-post-loader.ts`
- `src/lib/resources/glossary-publications.ts`
- `src/lib/resources/glossary-post-loader.ts`
- `src/lib/resources/manual-publications.ts`
- `src/lib/resources/manual-post-loader.ts`

Do not leave the final PR centered on one grouped file like:
- `src/lib/documentation-publications.ts`
- `src/lib/get-documentation-publication-post.ts`

If you needed such grouped files temporarily, remove them before finishing.

### Preview hub composition
A mixed preview hub can still exist under:
- `src/lib/resources/resource-preview-items.ts`

Use it only to compose the `/t/resources` page from:
- introduction-deck local items
- glossary local items
- manuals local items
- manual external-link cards
- existing local whitepaper/blog list items

Keep category ownership in the concrete loaders, not in the preview hub.

## Route pattern

### List pages
- `src/app/t/resources/page.tsx`
- `src/app/t/introduction-deck/page.tsx`
- `src/app/t/glossary/page.tsx`
- `src/app/t/manuals/page.tsx`

### Detail routes
For each category, implement both:
- `src/app/t/<category>/[id]/page.tsx`
- `src/app/t/<category>/[id]/[slug]/page.tsx`

Rules:
- id-only route redirects to canonical slug route
- slug route uses `id` as the lookup key
- mismatched slug redirects to canonical slug
- metadata should be `noindex`
- `introduction-deck` detail pages should wire gating cookies like the existing whitepaper pattern

## Asset-path rule learned here

This task surfaced an important distinction:
- For static preview pages migrated from external pages, route-aligned assets under `public/<route>/...` are often correct.
- But for documentation/resource MDX backed by `src/content/documentation/**`, the user wanted public asset paths to align with the MDX source family path, not with a shorter public route alias.

So for this family, prefer:
- `src/content/documentation/introduction-deck/1.mdx` -> `heroImageSrc: "/documentation/introduction-deck/1/thumbnail.png"`
- `src/content/documentation/glossary/1.mdx` -> `heroImageSrc: "/documentation/glossary/1/thumbnail.png"`
- `src/content/documentation/manuals/1.mdx` -> `heroImageSrc: "/documentation/manuals/1/thumbnail.png"`

Also align related/external preview images similarly, e.g.:
- `/documentation/glossary/1/related-release-notes-thumbnail.png`
- `/documentation/manuals/aip-guide/thumbnail.png`
- `/documentation/manuals/acp-guide/thumbnail.png`
- `/documentation/manuals/api-docs/thumbnail.png`

Do not leave the final PR using flat legacy-like direct references such as:
- `/documentation/docu-thumb-acp-introduction.png`
- `/documentation/docu-thumb-glossary.png`
- `/documentation/docu-thumb-aip-manual.png`

Those can remain as imported source artifacts temporarily, but the final referenced paths should follow the MDX-family-aligned structure.

## Test organization rule learned here

If a combined test file like `tests/documentation-preview-routes.test.mjs` appears during iteration, split it before finishing.

Preferred final test layout:
- `tests/src/lib/resources/architecture.test.mjs`
- `tests/src/app/t/resources/page.test.mjs`
- `tests/src/app/t/introduction-deck/page.test.mjs`
- `tests/src/app/t/glossary/page.test.mjs`
- `tests/src/app/t/manuals/page.test.mjs`

Use these to cover:
- base abstract class existence
- concrete loader/repository split
- page metadata / canonical / noindex
- detail route family existence
- category-specific loader usage

## PR cleanup lessons from this work

This task also involved cleaning an open PR that had unrelated commits.
When the user says the PR contains unrelated commits:
1. inspect `git rev-list --oneline origin/main..origin/<pr-branch>`
2. create a clean worktree from latest `origin/main`
3. use a temporary local branch name if the real PR branch is already checked out elsewhere
4. selectively copy only the intended scoped files from `origin/<pr-branch>`
5. validate
6. commit cleanly
7. `git push --force-with-lease origin HEAD:<pr-branch>`

This is often safer than trying to prune mixed history interactively.

## Verification
Run at minimum:
- `npm run typecheck`
- `node --test tests/src/lib/resources/architecture.test.mjs tests/src/app/t/resources/page.test.mjs tests/src/app/t/introduction-deck/page.test.mjs tests/src/app/t/glossary/page.test.mjs tests/src/app/t/manuals/page.test.mjs`
- `npm run test`
- `npm run build`

## Done criteria
- No grouped `documentation-*` loader files remain in the final PR
- `glossary`, `introduction-deck`, and `manuals` each have separate concrete resource loaders
- `/t/<category>` and `/t/<category>/:id/:slug` preview routes exist and build
- MDX hero/related image paths point at source-family-aligned `public/documentation/**` paths
- combined preview-route test file is split into source-path-aligned test modules
- PR diff is limited to documentation preview resource work only
