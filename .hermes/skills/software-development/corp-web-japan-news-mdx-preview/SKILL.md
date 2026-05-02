---
name: corp-web-japan-news-mdx-preview
description: Implement `/t/news` plus local MDX-backed news detail routes in corp-web-japan by normalizing the existing QueryPie news list into checked-in `src/content/news/*.mdx` records.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, news, mdx, migration, nextjs]
    related_skills: [corp-web-japan-origin-main-worktree-safety, blog-posting, github-pr-workflow]
---

# corp-web-japan news MDX preview workflow

Use this when the user wants corp-web-japan news to behave like the local MDX-backed blog/whitepaper/event flows, especially with a preview list at `/t/news` and local detail pages under `/news/:id/:slug`.

## Key finding

Unlike blog/whitepaper/event migrations, the current source news content may not exist as one body-MDX file per article.

In `../corp-web-contents/pages/company/news/ja/content.mdx`, the source is a single MDX page that renders a `NewsList` with an inline `items` array. That means you must first normalize the list items into local per-record MDX files before the standard publication pipeline can be used.

## Recommended output structure

Mirror the event publication pattern:

- `src/content/news/<id>.mdx`
- `src/content/publications/news-publication-records.ts`
- `src/lib/publications/get-news-publication-post.ts`
- `src/app/news/[id]/[slug]/page.tsx`
- `src/app/news/[id]/page.tsx`
- `src/app/t/news/page.tsx`
- `public/news/<id>/thumbnail.png`

## Route policy

Keep the existing `/news` redirect route unchanged unless the user explicitly asks to replace it.

Expected result:
- `/news` stays an upstream redirect if that is the current contract
- `/t/news` becomes the local non-indexed preview list page
- `/news/:id/:slug` renders local MDX detail pages
- `/news/:id` redirects canonically

This split avoids breaking existing navigation/tests that still expect `/news` to be a redirect endpoint.

## Production-readiness follow-up pattern

When the user wants `/t/news` made production-ready first, but explicitly wants `/t/news -> /news` rollout and SEO activation deferred:
- treat the current PR as a production-readiness preparation PR only
- keep `/t/news` non-indexed and keep `/news` as-is
- create separate GitHub issues for:
  - moving the local news list from `/t/news` to `/news`
  - enabling production SEO/indexing/sitemap behavior

Important practical distinction learned during follow-up:
- the user may still want all list-card links on `/t/news` to use local `/news/:id/:slug` URLs even for redirect-backed items
- in that setup, the list remains fully local while the detail route may still redirect externally via `redirectUrl`
- do not assume that `redirectUrl` means the list itself must link directly to the external origin; confirm the user's desired list-link behavior

### Production-readiness prep before `/news` rollout

A useful intermediate state is:
- make `/t/news` feel production-ready in UX/copy/layout
- keep `/news` itself unchanged as the upstream redirect until rollout time
- keep SEO/indexing activation out of the prep PR and track it separately

This is especially useful when the user wants a reviewable PR that prepares the surface first, then handles route cutover and SEO as follow-up issues.

Recommended split:
1. PR A: `/t/news` production-readiness prep only
2. Issue B: move `/t/news` to `/news`
3. Issue C: activate SEO / sitemap / indexing for the final `/news` surface

## Production-readiness prep before `/news` rollout

When the user wants `/t/news` made production-ready first, but explicitly wants the final `/t/news` -> `/news` move and SEO activation kept out of the PR, treat that as a separate pre-rollout phase.

Recommended scope for the preparation PR:
- make `/t/news` feel like a real company-news landing page, not an internal preview
- remove copy such as `プレビュー一覧` or `ローカル MDX` from the visible page text
- keep `/t/news` non-indexed for now
- keep `/news` as the existing upstream redirect for now
- create separate GitHub issues for:
  - moving the local surface from `/t/news` to `/news`
  - enabling production SEO / sitemap / indexing for the local news surface

Important: if the user asks for those follow-up steps to be tracked separately, create the issues during the same task and link them from the PR body.

## Canonical content split for local vs external news

If the user chooses the mixed model:
- official QueryPie news stays local and canonical
- external media coverage should go straight to the original article

Then implement the list behavior like this:
- items with `redirectUrl` should open the external article directly from the `/t/news` list cards
- only official local news items should link from the list to `/news/:id/:slug`
- related-news cards on local detail pages should also send redirect-backed items directly to the original external URL rather than bouncing through a local detail route

This keeps the local news surface aligned with the intended production information architecture while preserving the current `/news` redirect contract.

## Detail-page UX polish for local official news

Before calling `/t/news` production-ready, check the local canonical detail experience.

Two specific fixes proved useful:
- if the migrated MDX body still starts with an H1 that duplicates the page title rendered by `PublicationPostPage`, strip that leading H1 before rendering and before TOC extraction
- replace placeholder share buttons with working client-side share/copy behavior, rather than shipping inert icon-only controls

A practical implementation is:
- add a small client component for share/copy actions
- keep `PublicationPostPage` server-authored, but mount the client share component inside it
- generate TOC from the post-processed MDX source used for rendering, not from the raw source, so the TOC stays consistent after the duplicate-H1 removal

Expected production-ready replacement result when the user explicitly wants to replace `https://www.querypie.com/ja/company/news`:
- `/news` becomes the local public list page instead of an upstream redirect
- `/t/news` is either removed or kept only temporarily during rollout
- the public `/news` list copy must stop calling itself a preview or local-MDX check surface
- `/news` must be added to sitemap and no longer be `noindex`
- internal navigation that currently points to `/news` should then land on the local list page
- decide item policy explicitly before implementation:
  - canonical local detail for true QueryPie-owned announcements
  - direct external redirect for third-party coverage / media mentions

Practical lesson: the preview implementation can be functionally complete while still being far from production-ready if `/news` still redirects upstream, all news routes remain `noindex`, and most detail pages are only lightweight archive stubs.

## Source extraction workflow

1. Read the source file:
   - `../corp-web-contents/pages/company/news/ja/content.mdx`
2. Extract the inline `items={[ ... ]}` array.
3. Parse each item into a structured record with:
   - image filename
   - href
   - date
   - title
   - description
4. Decide local numeric IDs in descending-recency order if the source has no explicit IDs.

A quick script is often safest here because manually copying 10+ records is error-prone.

## MDX normalization contract

Each normalized file should use frontmatter like:

```mdx
---
id: "14"
slug: "mitoco-buddy-official-launch"
title: "..."
description: "..."
date: "2025年12月23日"
heroImageSrc: "/news/14/thumbnail.png"
author: "querypie"
relatedIds:
  - "13"
  - "12"
  - "11"
---
```

Body guidance when no full article body exists upstream:
- use the source list description as the canonical summary
- create a lightweight archive/detail page body rather than inventing a long article
- do NOT include the route-aligned thumbnail again in the MDX body when `heroImageSrc` already points at the same image
- include a small metadata section with date/category/source link
- clearly preserve the original article link when the real body lives elsewhere

Reason:
- `PublicationPostPage` already renders `post.heroImageSrc` as the top hero image
- if the MDX body also starts with `ArticleFileImage filepath="public/news/<id>/thumbnail.png"`, the same image appears twice
- this duplication was observed in practice and fixed in a follow-up PR by removing the leading `ArticleFileImage` block from all 14 local news MDX files

## Internal-link normalization

Some news items may point at old internal content paths such as:
- `/features/documentation/blog/26/mitoco-buddy-release`

If an equivalent local canonical route already exists in corp-web-japan, rewrite those references to the local route, for example:
- `/blog/26/mitoco-buddy-release`

For true external media coverage, keep the external URL.

### List-vs-detail behavior

The user may want a two-step behavior split:
- list cards on `/t/news` can all point to local `/news/:id/:slug` detail URLs for structural consistency
- but external-media items may still redirect from the local detail route to the original third-party article via `redirectUrl`

Do not assume that `redirectUrl` means the list card itself must link externally. Confirm the desired behavior from the user or recent review feedback.

## Asset rule

Use route-aligned assets only:

- source images often come from `../corp-web-contents/public/news/*.png`
- copy them to `public/news/<id>/thumbnail.png`
- do not keep new news-specific assets under `public/assets/...`

## Loader pattern

`news-publication-records.ts`
- scan `src/content/news/*.mdx`
- parse YAML frontmatter
- cache records and list items
- derive hrefs with `getPublicationHref("news", id, slug)`
- badge text should be `ニュース`

`get-news-publication-post.ts`
- load by `id`, not slug
- render with `renderPublicationMdx`
- build TOC with `extractHeadingsFromMdx`
- resolve author via `resolveArticleAuthors`
- build related items from `relatedIds`

## Required shared changes

Extend the publication framework to recognize news:

- `src/lib/publications/types.ts`
  - add `"news"` to `PublicationCategory`
- `src/lib/publications/get-publication-href.ts`
  - add `news: "/news"`

## Route behavior

### `/news/[id]/[slug]`
- load record by `id`
- redirect if `redirectUrl` exists
- redirect if `slug` mismatches canonical slug
- render `getNewsPublicationPost(id)`
- set canonical metadata to `/news/:id/:slug`
- set robots to `index: false, follow: false`

### `/news/[id]`
- load record by `id`
- redirect to `redirectUrl` if present
- otherwise redirect to `/news/:id/:slug`

### `/t/news`
- list page backed by `listNewsPublicationItems()`
- canonical should be `/t/news`
- robots should be `noindex, nofollow`

## Tests to add

1. routing/preview test
- `/t/news` exists and uses `listNewsPublicationItems()`
- `/news/[id]` redirects canonically
- `/news/[id]/[slug]` loads by `id` and redirects on slug mismatch
- loader uses `renderPublicationMdx` and `extractHeadingsFromMdx`
- publication type/href mapping includes `news`
- if you strip the leading in-body H1 from local news details to avoid duplicate page titles, assert that the loader derives TOC from the stripped source
- if list cards intentionally stay local even for redirect-backed records, assert the list-page source no longer emits external `target="_blank"` behavior

2. imported corpus test
- expected local news IDs exist under `src/content/news/*.mdx`
- each file uses `heroImageSrc: "/news/<id>/thumbnail.png"`
- each file references `filepath="public/news/<id>/thumbnail.png"`
- each thumbnail exists under `public/news/<id>/thumbnail.png`
- no new `public/assets/...` drift is introduced

3. safety regression
- run existing redirect endpoint tests to confirm `/news` still behaves as the repo expects

## Verification

Useful lightweight checks:

```bash
node --test tests/news-mdx-routing-and-preview.test.mjs tests/news-imported-corpus.test.mjs
node --test tests/redirect-endpoints.test.mjs tests/canonical-endpoints.test.mjs
npx tsc --noEmit --pretty false
```

## Pitfalls

- assuming news already has one upstream MDX file per article
- replacing the existing `/news` redirect route when the user only asked for `/t/news`
- forgetting to extend `PublicationCategory` and `getPublicationHref`
- leaving internal source links on legacy `/features/documentation/blog/...` paths when local `/blog/...` routes already exist
- scattering thumbnails under `public/assets/...` instead of `public/news/<id>/thumbnail.png`
- inventing long article bodies when only short news summaries exist upstream
- copying another page's intro copy literally when the user only wanted the layout/UX pattern; reuse the visual structure but rewrite the text for the news context
- forgetting the user's preference that Japanese text shown in chat should include immediate Korean translation in parentheses

## Production-ready preparation before `/news` rollout

When the user wants `/t/news` brought to production-ready quality before the final route move and SEO activation, keep that scope separate from the actual rollout.

Recommended behavior for the preparation PR:

- keep `/t/news` as the temporary entry point
- keep `/news` itself unchanged if it still redirects upstream
- keep robots/canonical noindex behavior unchanged for now
- create separate GitHub issues for:
  - moving `/t/news` to `/news`
  - enabling production SEO/indexing for the local news surface

### Preferred content/linking policy

For corp-web-japan news, prefer this split:

- official QueryPie-owned announcement/news posts stay local canonical detail pages
  - currently this means items like `13` and `14`
- third-party media coverage items should not force users through thin local archive pages
  - list cards for redirect-backed items should open the original external article directly
  - related-news cards should also link directly to the original external article when the related item has `redirectUrl`

Implementation detail:
- in `news-publication-records.ts`, list item `href` should prefer `record.redirectUrl ?? getPublicationHref(...)`
- expose list-item metadata such as `sourceLabel` and `opensExternal` so `/t/news` can explain official-vs-external behavior in the UI

### `/t/news` UX finishing guidance

The generic `ResourceListPage` is acceptable for initial preview work, but the production-ready preparation pass should usually replace it with a dedicated news list surface if needed.

Useful refinements:
- remove preview-only wording such as `プレビュー一覧` or `ローカル MDX`
- explain clearly that official QueryPie announcements open local details while media coverage opens the original article
- use a company-information sidebar/nav treatment rather than a generic resources taxonomy if that better matches the site IA
- label cards so users can distinguish `公式発表` vs `メディア掲載`
- for external items, use direct external anchors with `target="_blank" rel="noopener noreferrer"`

### News detail UX refinements

For local canonical news posts:

- add working share/copy actions instead of placeholder icon buttons
- if the MDX body starts with a first-level `# title` that duplicates the page chrome H1, strip that leading heading before rendering
- build TOC from the stripped source so the duplicated title does not appear in the TOC

A reusable pattern is:
- keep the page-shell H1 in `PublicationPostPage`
- strip only the first leading MDX H1 after frontmatter in the news loader before `renderPublicationMdx`
- use the stripped source for both `renderPublicationMdx` and `extractHeadingsFromMdx`

### Tests worth adding in the preparation PR

In addition to the original routing/corpus checks, add source-level assertions for:
- `/t/news` copy no longer containing preview-only wording
- dedicated news list page using direct external links for redirect-backed items
- share/copy client behavior being wired in the detail page
- related-news UI supporting external direct links
- news loader stripping the leading duplicate H1 before render/TOC

## Done criteria

Initial preview done criteria:
- `/t/news` exists and is non-indexed
- `/news/:id/:slug` renders local MDX
- `/news/:id` redirects canonically
- `/news` top-level contract is preserved unless explicitly changed
- source news list is normalized into local `src/content/news/*.mdx`
- route-aligned thumbnails exist under `public/news/<id>/thumbnail.png`
- targeted news tests pass
- redirect regression tests still pass

Production-ready preparation done criteria:
- `/t/news` copy and card UX no longer feel preview-only
- official local news and external media items are clearly distinguished in list/detail behavior
- redirect-backed list items open the original article directly
- local canonical detail pages have working share/copy actions
- duplicate leading MDX H1 rendering is removed from local news detail pages
- separate follow-up issues exist for the `/t/news` -> `/news` move and SEO activation
