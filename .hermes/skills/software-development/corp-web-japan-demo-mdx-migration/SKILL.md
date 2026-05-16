---
name: corp-web-japan-demo-mdx-migration
description: Migrate corp-web-contents demo MDX families (use-cases, AIP demos, ACP demos) into corp-web-japan local MDX publication routes with preview lists, canonical detail routes, route-aligned assets, and focused regression tests.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# corp-web-japan demo MDX migration

Use this when the user asks to migrate a `../corp-web-contents/pages/features/demo/<family>/**` MDX family into `corp-web-japan`.

Supported pattern families proven in practice:
- `use-cases`
- `aip-features`
- `acp-features`

## Core rules

1. Start from latest `origin/main` in a fresh git worktree.
2. Do not reuse an old branch/worktree for a new migration request.
3. Keep existing public root redirect routes like `/demo/aip` or `/demo/acp` unchanged unless the user explicitly asks to replace them.
4. Implement preview list routes under `/t/...` and canonical detail routes under the final public route family.
5. Keep assets route-aligned under `public/<route-family>/<id>/thumbnail.png`.
6. Add focused source-based tests first; they are fast and reliable in fresh worktrees.
7. If repo-root `node_modules` already exists, `../../node_modules/.bin/tsc --noEmit` is a useful fast check from a worktree.

## Family mappings used successfully

### use-cases
- source: `../corp-web-contents/pages/features/demo/use-cases/<id>/<slug>/ja/content.mdx`
- public list: `/demo/use-cases`
- canonical detail: `/demo/use-cases/:id/:slug`
- id redirect: `/demo/use-cases/:id`
- content root: `src/content/demo/use-cases/*.mdx`
- assets: `public/demo/use-cases/<id>/thumbnail.png`
- category key / MDX collection identifier: `demo/use-cases`
- href prefix: `/demo/use-cases`

Rationale / path-contract pitfall:
- Treat use-cases as part of the demo namespace consistently: list route, detail route, ID-only redirect route, content root, asset root, and publication category should all align to `demo/use-cases`.
- Do **not** preserve or reintroduce `/use-cases/:id/:slug` when normalizing use-case content roots. PR #547 follow-up corrected that split-brain state by moving detail routes to `/demo/use-cases/:id/:slug` and ID redirects to `/demo/use-cases/:id`.
- When auditing a PR that moves only `src/content/demo/use-cases` / `public/demo/use-cases` but leaves `get-publication-href.ts`, `src/app/use-cases/**`, docs, or tests on `/use-cases`, treat it as incomplete.
- Update page-authored links such as AI Crew use-case cards and all source-based route tests to the same canonical detail prefix.
- See `references/use-cases-demo-namespace-rollout.md` for the focused review/update checklist from the PR #547 follow-up.

Cross-repo parity caution:
- The complete use-case corpus source is `../corp-web-contents/pages/features/demo/use-cases`, not `page-archives/customers/customer-success-cases`.
- The customer-success archive overlaps only IDs 1-5 and is insufficient for a full use-case migration.
- For corp-web-app parity work, source coverage observed from this root was EN=29, JA=29, KO=6 (IDs 1-6), total 64 MDX records; tests should assert IDs 1-29 and locale-specific counts.

Important source-root pitfall:
- `../corp-web-contents/page-archives/customers/customer-success-cases/**` is only the 1-5 customer-success subset.
- Full use-case parity must use `../corp-web-contents/pages/features/demo/use-cases/**` as the source root.
- Current source coverage observed for that root: 29 EN records, 29 JA records, and 6 KO records (IDs 1-6 only for KO), 64 MDX records total.
- Tests for a full migration should assert IDs 1-29 and locale-specific coverage, not a fixed 5-record customer-success subset.
- See `references/use-cases-source-root-parity.md` for the detailed audit pattern and commands.

Important corpus boundary:
- The full use-cases corpus is `../corp-web-contents/pages/features/demo/use-cases/**`, not `../corp-web-contents/page-archives/customers/customer-success-cases/**`.
- As observed in May 2026, the full source has 29 JA records and 29 EN records; KO exists only for a subset (1-6).
- IDs 1-5 are customer-success-style records and also exist under the `page-archives/customers/customer-success-cases/**` archive, but that archive is only a 5-record subset and must not be used as the source root for full use-case parity.
- When validating a use-cases migration, assert expected IDs 1-29 or source-derived per-locale counts; do not write tests that merely assert 5 records unless the task is explicitly scoped to the customer-success subset.
- Session-specific investigation notes: `references/use-cases-corpus-boundary.md`.

### AIP demos
- source: `../corp-web-contents/pages/features/demo/aip-features/<id>/<slug>/ja/content.mdx`
- preview list: `/t/demo/aip`
- canonical detail: `/demo/aip/:id/:slug`
- id redirect: `/demo/aip/:id`
- content root: `src/content/demo/aip/*.mdx`
- assets: `public/demo/aip/<id>/thumbnail.png`
- category key: `aip-demo`
- href prefix: `/demo/aip`

### ACP demos
- source: `../corp-web-contents/pages/features/demo/acp-features/<id>/<slug>/ja/content.mdx`
- preview list: `/t/demo/acp`
- canonical detail: `/demo/acp/:id/:slug`
- id redirect: `/demo/acp/:id`
- content root: `src/content/demo/acp/*.mdx`
- assets: `public/demo/acp/<id>/thumbnail.png`
- category key: `acp-demo`
- href prefix: `/demo/acp`

## Implementation shape

For each new family, add:
- `src/content/publications/<family>-publication-records.ts`
- `src/lib/publications/get-<family>-publication-post.ts`
- preview list page under `src/app/t/.../page.tsx`
- canonical detail page under `src/app/.../[id]/[slug]/page.tsx`
- id redirect page under `src/app/.../[id]/page.tsx`
- `src/content/.../*.mdx`
- `public/.../<id>/thumbnail.png`
- tests for corpus completeness + route architecture
- sitemap entries
- `PublicationCategory` extension in `src/lib/publications/types.ts`
- href prefix in `src/lib/publications/get-publication-href.ts`

Follow the existing event/news/use-case publication pattern:
- records file scans MDX directory, parses YAML frontmatter, exposes list/params/id helpers
- loader reads MDX, renders with `renderPublicationMdx`, extracts TOC via `extractHeadingsFromMdx`, builds related items from `relatedIds`
- detail route loads by `id`, redirects mismatched slug, renders `PublicationPostPage`
- preview route uses `ResourceListPage`, `SiteHeader`, `SiteFooter`, and `robots: noindex`

## Frontmatter normalization

Typical source frontmatter fields:
- `layout`
- `category`
- `title`
- `description`
- `date` as `YYYY-MM-DD`
- `ogImage`
- `hideOgImage`
- `hideTableOfContents`
- `relatedPosts`

Normalize to:
- `id`
- `slug`
- `title`
- `description`
- `date` converted to Japanese format like `2025年9月23日`
- `heroImageSrc` pointing at route-aligned thumbnail
- `relatedIds`

Drop source-only fields like:
- `layout`
- `category`
- `ogImage`
- `hideOgImage`
- `hideTableOfContents`
- `keywords`

Important finding:
- Some source families have blank descriptions for every entry. In that case, fill a minimal useful local description instead of preserving empty strings.

## Asset migration

- Read `ogImage` from source frontmatter.
- Copy the referenced source file from `../corp-web-contents/public/...` into the route-aligned target thumbnail path.
- Do not keep migrated MDX pointing at old `public/demo/...`, `public/tutorial/...`, or other legacy asset roots.

## MDX component compatibility

Before finalizing, inspect the imported corpus for custom tags.
Practical findings:
- use-cases only needed `Youtube`
- AIP demos only needed `Youtube`
- ACP demos needed `Youtube`, `InfoNote`, and additionally `BlueState` + `User`

If imported MDX uses unsupported components, add the smallest presentational implementation to `src/lib/publications/mdx/components.tsx` rather than rewriting all content.

## Hero-image duplication rule for YouTube-first demo/publication entries

A reusable corpus-specific finding from the local demo/publication migrations:
- when a migrated MDX entry presents a `<Youtube ... />` embed directly in the article body, the detail-page hero image can become visually redundant with the embedded video
- this has been confirmed for:
  - `/demo/use-cases/:id/:slug`
  - `/demo/aip/:id/:slug`
  - `/demo/acp/:id/:slug`
- in those cases, add `hideHeroImageOnDetail: true` to the MDX frontmatter
- make sure the family-specific publication frontmatter parser and `get-*-publication-post.ts` loader pass this flag through to `PublicationPost`
- `PublicationPostPage` already respects `post.hideHeroImageOnDetail`, so the migration/follow-up work only needs the frontmatter + loader wiring and regression coverage

Practical verification rule:
- add/keep a regression that asserts `if source includes <Youtube, source also includes hideHeroImageOnDetail: true`
- also prefer the inverse assertion for these families: if `hideHeroImageOnDetail: true` is present, the MDX should include `<Youtube`

## Verification commands

Use these first:
- `node --test tests/<family>-imported-ja-corpus.test.mjs tests/<family>-mdx-routing-and-preview.test.mjs`
- `../../node_modules/.bin/tsc --noEmit`

Good tests should verify:
- expected IDs exist locally
- `heroImageSrc` uses the new route-aligned thumbnail path
- legacy asset paths are gone from migrated MDX
- legacy `/features/demo/<family>/...` references are gone from migrated MDX
- preview page is noindex and uses the correct list function
- canonical detail page loads by `id` and redirects mismatched slugs
- id-only route redirects correctly
- `PublicationCategory` and href prefix include the new family category
- any newly required MDX components are present

## Worktree safety note

Do not assume an ad hoc directory is a real git worktree just because its name looks right.
Use `git worktree list --porcelain` to confirm the actual registered worktree path before writing files.
Prefer repo-local `.worktrees/<branch>` paths when creating a new worktree in this repo.

## Rebase conflict expectations after another demo migration lands

If one demo-family migration PR sits open while another demo-family migration lands on `main`, rebasing the older PR will usually conflict in additive registry files rather than in the family-specific content files.

Observed high-probability conflict files:
- `src/lib/publications/types.ts`
- `src/lib/publications/get-publication-href.ts`
- `src/app/sitemap.ts`
- sometimes `.agents/skills/README.md` if the PR also added a repo-local migration skill

Resolution rule:
- keep both family categories in `PublicationCategory`
- keep both route prefixes in `get-publication-href.ts`
- keep both sitemap imports and both mapped route arrays in `src/app/sitemap.ts`
- in `.agents/skills/README.md`, preserve previously landed migration-skill entries and append the new one instead of taking either side wholesale

This is usually an additive merge, not a semantic choice between alternatives.
After resolving, rerun the focused source tests and the lightweight typecheck before force-pushing the rebased PR branch.

## Finish

Before push:
- `git fetch origin --prune`
- if `origin/main` advanced, rebase from a clean latest-main worktree context rather than stashing local edits in place
- if rebase conflicts happen after another demo migration landed, resolve the shared registry files additively as described above
- rerun focused tests
- commit and push
- open PR with a body file describing route family, asset alignment, and verification
