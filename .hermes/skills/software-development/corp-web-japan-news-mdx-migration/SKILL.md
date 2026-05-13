---
name: corp-web-japan-news-mdx-migration
description: Maintain the corp-web-japan local MDX-backed news corpus, verify parity against querypie.com/ja/company/news and corp-web-contents source data, and migrate blog-backed news bodies into canonical /news posts when needed.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, news, mdx, migration, parity, redirects]
    related_skills: [corp-web-japan-origin-main-worktree-safety, existing-pr-followup-worktree, github-pr-workflow]
---

# corp-web-japan news MDX migration and parity maintenance

Use this when working on the local news corpus in `corp-web-japan`, especially when the user asks whether all news postings have been migrated, wants missing news items imported, or wants blog-backed news announcements moved into canonical `/news` detail pages.

## Current structure

Local news implementation uses:
- `src/content/news/*.mdx`
- `src/content/publications/news-publication-records.ts`
- `src/lib/publications/get-news-publication-post.ts`
- `src/app/t/news/page.tsx`
- `src/app/news/page.tsx`
- `src/app/news/[id]/page.tsx`
- `src/app/news/[id]/[slug]/page.tsx`
- route-aligned assets under `public/news/<id>/...`

## News index labeling rule

Before renaming the `/news` list page title or hero heading, inspect the actual `src/content/news/*.mdx` corpus rather than assuming every item is external media coverage.

Important observed pattern:
- the corpus can mix true external-media coverage items and first-party official announcements/press-release style posts
- when that mix exists, a broader list-page label is more accurate than a media-only label

Current preferred outcome for this repo when `/news` contains both kinds:
- page H1 in `src/app/news/page.tsx`: `ニュース`
- metadata title in `src/app/news/page.tsx`: `ニュース | QueryPie AI`

Do not narrow the page label to something like media coverage only unless official announcements have first been split out of the `/news` corpus.

When changing the `/news` list page heading or title, update source-reading tests in the same PR. In particular, `tests/news/mdx-routing-and-preview.test.mjs` asserts the visible `NewsPageTitle` text; if the H1 changes, adjust that expectation and run `node --test tests/news/mdx-routing-and-preview.test.mjs` plus `npm run test:publications` before pushing.

Blog shadow/redirect behavior may also matter:
- `src/content/blog/*.mdx`
- `src/app/blog/[id]/page.tsx`
- `src/app/blog/[id]/[slug]/page.tsx`
- `src/lib/publications/blog-publication-records.ts`

## Source of truth for news inventory

For inventory/parity, the main source is:
- `../corp-web-contents/pages/company/news/ja/content.mdx`

Important finding:
- this source stores the news list as an inline `items={[ ... ]}` array inside MDX
- many items are external-media links
- some items can be blog-backed internal links like `/features/documentation/blog/25/...`
- do not assume there are separate per-news MDX source files in `corp-web-contents`

## Required validation order

When the user asks whether migration is complete, check all three layers:

1. live page
- exact requested page: `https://www.querypie.com/ja/company/news`
- extract visible item count and ordered titles

2. source file
- parse the `items={[ ... ]}` array from `../corp-web-contents/pages/company/news/ja/content.mdx`
- collect ordered titles, dates, hrefs

3. local corpus
- inspect `src/content/news/*.mdx`
- compare count and ordered titles with the source list

Do not infer parity only from code or file counts. The live page must be checked directly when the user explicitly asks for live-vs-source verification.

## Reliable parity conclusion pattern

Migration is complete only if all of the following match:
- live visible item count
- source item count from `corp-web-contents`
- local `src/content/news/*.mdx` count
- ordered titles between source and local corpus

## Reusable parsing approach for the source list

The `corp-web-contents` news source can be parsed by:
- reading `pages/company/news/ja/content.mdx`
- locating the `items={[` start
- locating the matching `]}` end
- evaluating the extracted JS object array in a trusted local script context

This is more reliable than regex-only extraction for the nested object literals.

## Blog-backed news items

Important experiential finding:
- some source news items are not external media links
- they point to existing blog posts, for example blog ids 25 and 26
- if the user wants the news posting itself to contain the full article body, do not create a new news item
- instead, move the blog article body into the existing canonical news post that already represents that news item

### Canonical rule

When a blog-backed news item already has a local news post like:
- blog 25 <-> news 13
- blog 26 <-> news 14

then:
1. keep the existing news ids/slugs as canonical
2. replace the summary-style news body with the full migrated article body
3. convert the former blog post into a hidden redirect-only shadow record

## Shadow blog record pattern

For blog-backed news items that should now canonicalize to `/news/...`:

- keep the blog MDX file present so id-based lookup still resolves
- set `hidden: true`
- set `redirectUrl: "/news/<id>/<slug>"`
- leave the existing blog route implementation to redirect before rendering

Example pattern:

```yaml
hidden: true
redirectUrl: "/news/13/terrasky-mitoco-buddy-announcement"
```

This ensures:
- `/blog` list hides the record
- `/blog/:id` redirects to the canonical news post
- `/blog/:id/:slug` also redirects to the canonical news post

## Content migration pattern for blog-backed news

When moving the body from blog -> existing news:

1. preserve the target news frontmatter (`id`, `slug`, `heroImageSrc`, `relatedIds`)
2. replace only the body content
3. keep the page-level hero image driven by `heroImageSrc`
4. allow in-body images when they are part of the actual migrated article body
5. ensure the in-body content does NOT reintroduce the page hero thumbnail duplication if the first image is only the thumbnail

### Asset rule

All news-specific assets must live under:
- `public/news/<id>/...`

If the source article body references blog assets like:
- `public/blog/25/blog25-image-1.png`

copy them to:
- `public/news/13/blog25-image-1.png`

and rewrite MDX references accordingly.

Do not leave migrated news-body assets under `public/blog/...` once the canonical body has moved to `/news/...`.

## Content-shape rule for local news MDX

Keep local news MDX files free of a duplicated leading page-title H1.

## Exact-source replacement rule for original-language follow-ups

When the user provides corrected source text for a specific local news post (for example a replacement English original article body for one `src/content/news/<id>.mdx` file):
- edit the existing news MDX file directly
- preserve the current frontmatter (`id`, `slug`, `title`, `description`, `date`, `heroImageSrc`, `relatedIds`, `sourceLabel`, `author`) unless the user explicitly asks to change it
- preserve the existing Japanese translation section unless the user explicitly asks to revise it
- replace only the targeted original-language section body under the matching heading such as `## 原文（英語）`
- keep the `**Original title:** ...` line unless the user explicitly supplies a replacement for it
- after the edit, rerun the narrow news regression tests rather than broad repo verification

When the user provides a source-language article (for example Korean) and asks for a better Japanese translation for an existing local news post:
- rewrite only the `## 日本語訳` section
- keep the existing frontmatter, route identity, source attribution line, and original-language section unless the user explicitly asks to change them too
- prefer natural Japanese news/article prose over literal sentence-by-sentence translation
- preserve key factual details from the supplied source text, especially chronology, company/product names, funding figures, and quoted future-plan statements
- if a brand or product typo is discovered nearby while doing the translation update (for example `query-Fi` vs `QueryPie`), fix it in the same follow-up when it is clearly an error in the same article body
- after the edit, rerun the narrow news regression tests rather than broad repo verification

This avoids accidental rewrites of translated copy, metadata, or routing when the requested task is only to correct the embedded source article text.

Required shape:
- frontmatter `title` is the canonical page title
- the body starts directly with the article content, source blockquote, or real section headings
- do **not** keep a duplicated first line like `# <same title as frontmatter>` immediately after frontmatter

Why:
- the shared `PublicationPostPage` already renders `post.title` as the page H1
- duplicating the title in MDX forces loader-side cleanup and can pollute the TOC extraction path

Implementation preference:
- remove the redundant H1 from `src/content/news/*.mdx`
- keep the loader simple so it renders `bodySource` directly and extracts headings from `bodySource`
- do not preserve a special-case strip helper unless there is a truly exceptional news-body shape that cannot be normalized at the content layer

## Tests to keep or add

Keep/add these regression checks:

1. source parity test
- local news count matches `corp-web-contents` source count
- local news titles remain in the same visible order as the source list

2. routing/loader test
- `/t/news` exists and is driven by news publication records
- `/news/[id]` redirects canonically
- `/news/[id]/[slug]` loads by id and redirects only on slug mismatch
- the news loader renders the MDX directly from `bodySource` and does not rely on a title-stripping helper

3. imported corpus test
- each news file keeps `heroImageSrc: "/news/<id>/thumbnail.png"`
- no file reuses the thumbnail in-body via `filepath="public/news/<id>/thumbnail.png"`
- route-aligned assets exist
- no news MDX file keeps a duplicated leading `# ` heading immediately after frontmatter

4. blog shadow redirect test
- affected blog records are `hidden: true`
- affected blog records have `redirectUrl` to canonical news routes
- blog detail routes redirect before rendering

5. migrated-body test for blog-backed items
- `news/13` and `news/14` contain the expected migrated section headings/body markers
- migrated `news/13` asset references point to `public/news/13/...`
- migrated bodies no longer point back to `public/blog/25/...` or `関連ブログを見る`

6. localization test
- verify Japanese `title` and `description` in frontmatter for translated imported news posts
- do not require a body-leading H1 in localization tests, because the canonical title now lives only in frontmatter/page chrome

## Verification commands

Targeted verification that worked well:

```bash
node --test \
  tests/news-blog-25-26-content-migration.test.mjs \
  tests/news-imported-corpus.test.mjs \
  tests/news-mdx-routing-and-preview.test.mjs \
  tests/news-source-parity.test.mjs \
  tests/blog-frontmatter-visibility-and-redirect.test.mjs
```

## Pitfalls

- treating count parity alone as sufficient without checking title order
- assuming `corp-web-contents` has per-news article MDX files when the real source is only the list array
- creating duplicate new news posts instead of updating the existing canonical news ids
- leaving canonical article bodies in `/blog/...` while also trying to make `/news/...` canonical
- forgetting to copy route-aligned in-body assets from `public/blog/...` to `public/news/...`
- overfitting tests so they ban all `<ArticleFileImage>` in news bodies; migrated real article bodies may legitimately include in-body images
- forgetting that the page hero already renders from `heroImageSrc`, so the thumbnail must not be repeated as the first in-body image

## Done criteria

- live page, source list, and local news corpus all match in count and ordered titles
- blog-backed news items use canonical `/news/...` detail pages with full article bodies
- old blog records are hidden and redirect to the matching news URLs
- migrated in-body assets are route-aligned under `public/news/<id>/...`
- targeted parity/routing/redirect/content-migration tests pass
