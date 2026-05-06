---
name: corp-web-japan-news-posting-migration
description: Migrate corp-web-japan news postings into the local MDX-backed /t/news and /news/:id/:slug flow, including parity checks against corp-web-contents and blog-to-news shadow redirect conversion when older news items originally pointed at blog posts.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, news, mdx, migration, publications, redirects]
    related_skills: [corp-web-japan-origin-main-worktree-safety, existing-pr-followup-worktree, blog-posting]
---

# corp-web-japan news posting migration

Use this when working on the local news system in `corp-web-japan`, especially when the user wants `/t/news` or `/news/:id/:slug` to reflect the real QueryPie Japan news corpus rather than a placeholder summary-only archive.

## When to use

- The user asks whether all news postings from `https://www.querypie.com/ja/company/news` were migrated.
- The user asks to migrate missing news items from `../corp-web-contents/pages/company/news/ja/content.mdx`.
- The user asks to replace summary-only local news MDX with fuller article bodies.
- Some news list entries historically pointed at local blog posts because the old news system had no detail-body capability, and the user now wants those article bodies moved into canonical news posts.

## Key findings to remember

### 1. The authoritative source list is not a directory of individual news article files
For the current Japan news surface, the primary source of truth is:
- `../corp-web-contents/pages/company/news/ja/content.mdx`

That file contains a `NewsList items={[ ... ]}` array.

Do not assume there is a parallel tree of standalone `pages/company/news/<id>/.../content.mdx` files to import from.
For many older entries, the source is only a list item that points at an external article URL.

### 2. Cross-check three places, not just one
When auditing migration completeness, compare all three:
1. live page: `https://www.querypie.com/ja/company/news`
2. source data: `../corp-web-contents/pages/company/news/ja/content.mdx`
3. local corpus: `src/content/news/*.mdx`

The most reliable sequence is:
- inspect latest `origin/main`
- read the local `src/content/news/*.mdx` set
- parse the `items` array from `corp-web-contents`
- visit the live page and extract the visible title list from the DOM
- compare count + order + titles across all three

### 3. Some "news" items may actually be backed by blog article bodies
A critical historical quirk:
- older Japan news list items sometimes linked to `/features/documentation/blog/...` instead of an external article URL
- this happened because the old news surface had no local body-rendering feature

Representative example found in real work:
- news item for TerraSky collaboration linked to blog 25
- news item for mitoco Buddy launch linked to blog 26

When the user wants those to become true news postings:
- do NOT create brand-new duplicate news records if matching local news records already exist
- instead, migrate the blog article body into the existing canonical news MDX file
- then turn the old blog record into a hidden redirect-only shadow record

## Current local implementation pattern

- local news content: `src/content/news/<id>.mdx`
- route-aligned assets: `public/news/<id>/...`
- publication records: `src/content/publications/news-publication-records.ts`
- detail loader: `src/lib/publications/get-news-publication-post.ts`
- preview list route: `src/app/t/news/page.tsx`
- canonical detail routes:
  - `src/app/news/[id]/[slug]/page.tsx`
  - `src/app/news/[id]/page.tsx`

## Audit workflow

### Step 1. Confirm latest main first
Use the normal latest-main safety workflow before planning.

### Step 2. Parse the source list
A practical Node snippet that worked:

```bash
node <<'NODE'
const fs = require('fs');
const src = fs.readFileSync('../corp-web-contents/pages/company/news/ja/content.mdx', 'utf8');
const start = src.indexOf('items={[');
const end = src.indexOf(']}', start);
const arrayText = src.slice(start + 'items={'.length, end + 1);
const items = Function(`return (${arrayText});`)();
console.log(JSON.stringify(items, null, 2));
NODE
```

This lets you compare title / href / date values directly.

### Step 3. Check the live page literally
Do not substitute a redirected or alternate page.
Visit:
- `https://www.querypie.com/ja/company/news`

Then extract visible titles and links from the browser DOM.
Examples that worked well:
- `document.querySelectorAll('main li h4')`
- `document.querySelectorAll('main li a')`

### Step 4. Compare against local MDX
Extract local title / id / date from `src/content/news/*.mdx` and compare:
- count
- order
- titles

If counts and ordered titles match, there are no missing postings to add.

## Migrating a blog-backed news item into canonical news

Use this when the live/source news item points to a blog URL but the user wants the news posting body to live under the news route.

### Desired outcome
- keep the existing news route canonical, e.g. `/news/13/...`
- move the full article body into the existing `src/content/news/<id>.mdx`
- if the news item should remain a media/news-style card after removing external redirect behavior, preserve that list labeling explicitly with news frontmatter `sourceLabel: "メディア掲載"`
- hide the old blog post from `/blog`
- redirect `/blog/<id>` and `/blog/<id>/<slug>` to the canonical news URL using blog frontmatter `redirectUrl`

### Important implementation lesson: `redirectUrl` is no longer enough once the article body is localized
Historically the local news list inferred:
- `record.redirectUrl ? "メディア掲載" : "公式発表"`

That works only while external-link news items still redirect away.
If you migrate an external article into a local body-backed news post and remove `redirectUrl`, the list will incorrectly flip to `公式発表` unless you add an explicit frontmatter field.

Recommended pattern:
- extend `src/lib/publications/news-publication-records.ts`
- support optional frontmatter `sourceLabel?: string`
- set list item label as `record.sourceLabel ?? (record.redirectUrl ? "メディア掲載" : "公式発表")`
- for migrated former external articles, set `sourceLabel: "メディア掲載"`

This lets local-body news posts remain canonical/local while still truthfully presenting them as media coverage in the list UI.

### Practical approach

1. Read both files:
- source blog body, e.g. `src/content/blog/25.mdx`
- target news file, e.g. `src/content/news/13.mdx`

2. Preserve the news frontmatter.
- keep the news `id`, `slug`, `heroImageSrc`, and `relatedIds` unless the user asks otherwise
- if the article originated as external/media coverage but is now rendered locally, add `sourceLabel: "メディア掲載"`
- replace only the body content after the frontmatter block

3. Replace route-aligned asset paths.
- rewrite `public/blog/<id>/...` -> `public/news/<news-id>/...` inside the migrated body
- copy the referenced files into `public/news/<news-id>/...`

4. Rewrite internal article links.
- if migrated blog content links to the old blog route, replace it with the canonical news route

5. Convert the old blog file into a shadow redirect record.
- set `hidden: true`
- set `redirectUrl: "/news/<news-id>/<news-slug>"`
- keep enough frontmatter for lookup/redirect behavior
- keep the original title/slug/author metadata intact
- keep source-parity-sensitive metadata such as `description` unchanged unless you also update the parity fixtures/tests
- the file body may be reduced to a tiny redirect note because the route should redirect before rendering it

### Example asset rename lesson
When copying blog-only body assets into news, do not keep stale blog-specific prefixes if they make the route-aligned asset tree noisy.
Example cleanup that was requested later:
- `public/news/13/blog25-image-1.png` -> `public/news/13/image-1.png`
- update MDX references and tests in the same change

Rule of thumb:
- prefer short, route-local names under the final canonical asset root
- avoid carrying historical source-family prefixes like `blog25-` into `public/news/<id>/...` unless they meaningfully disambiguate files

## Localizing imported non-Japanese news posts for the Japan site

When a migrated local news post is sourced from an English or Korean article, the user expects the local `corp-web-japan` news detail page itself to become Japanese-first rather than remaining an untranslated archive.

Recommended pattern for imported non-Japanese news posts:

1. Translate the visible frontmatter fields used by the local list/detail UI.
- translate `title` into natural Japanese
- translate `description` into natural Japanese
- keep `slug`, `id`, `date`, `sourceLabel`, and route-aligned assets unchanged unless separately requested

2. Make the local MDX body Japanese-first while preserving provenance.
- keep the source provenance quote block near the top, for example:
  - `> Source article: ...`
  - `> Original source: ...`
  - `> Imported from syndicated copy: ...`
- add a `## 日本語訳` section immediately before the original-language body content
- preserve the original imported body below it under either:
  - `## 原文（英語）`
  - `## 原文（韓国語）`

3. Do not add redundant original-language sections to news posts that are already Japanese local-body content.
- existing Japanese-native posts should stay as-is
- only add `日本語訳` / `原文` sections for migrated non-Japanese article bodies

4. Keep the route-local content structure simple.
- the MDX file itself should remain the source of truth
- do not move the translation into helper files or code-side constants just to avoid touching the MDX

Practical regression coverage that proved useful:
- assert imported non-Japanese news ids now have Japanese `title` and `description`
- assert `## 日本語訳` appears before `## 原文（英語）` / `## 原文（韓国語）`
- assert already-Japanese local-body news posts do not gain redundant `原文` sections

## External-source fallback lessons

When the configured original news URL is dead or blocked, do not stop at the first failure. In real news migration work these fallback classes were reusable:

- direct original URL still loads -> import from that page
- original URL times out but the article is otherwise mirrorable -> use a text mirror such as `r.jina.ai/http://...` to recover the body
- original domain no longer resolves -> search for a syndicated copy on another outlet and import from that copy
- original URL returns 404 -> search for the same press release on PR Newswire / Business Wire / other syndication targets
- original consumer-news URL returns 403 -> prefer the company’s own source release PDF or official press page if available

Concrete examples encountered:
- TechSeoul source dead -> imported from KSValley / BoanNews syndicated copies
- Yahoo Finance 404 -> imported from PR Newswire syndicated copy
- Nico 403 -> imported from Payroll PDF source release

Record the fallback source in the MDX body with a short quote block such as:
- `> Source article: ...`
- `> Original source: ...`
- `> Imported from syndicated copy: ...`

This keeps provenance visible after removing the external redirect behavior.

### A. Source parity test
Create a test that:
- parses `../corp-web-contents/pages/company/news/ja/content.mdx`
- reads local `src/content/news/*.mdx`
- asserts equal count
- asserts same visible title order
- asserts local files have non-empty metadata

### B. Migration-specific test for blog-backed news
Add a focused test that asserts:
- migrated news file contains distinctive headings from the old blog body
- route-aligned asset references point at `public/news/<id>/...`
- old `public/blog/<id>/...` references are gone
- old summary-only placeholder markers like `参照元: [関連ブログを見る]` are gone when the page is now a true body-backed news post

### C. Blog shadow redirect test
Add or extend a test asserting:
- blog 25/26 (or the relevant ids) have `hidden: true`
- blog 25/26 have `redirectUrl` pointing at the news canonical URL
- blog detail routes redirect on `redirectUrl` before attempting local render

## Verification commands

Useful targeted verification set:

```bash
node --test \
  tests/news-source-parity.test.mjs \
  tests/news-mdx-routing-and-preview.test.mjs \
  tests/news-imported-corpus.test.mjs \
  tests/news-blog-25-26-content-migration.test.mjs \
  tests/blog-frontmatter-visibility-and-redirect.test.mjs
```

Use this before commit/push for news-related follow-up work.

## Pitfalls

- assuming missing per-article source files exist under `corp-web-contents/pages/company/news/**`
- auditing only local files without visiting the live page literally
- creating a brand-new duplicate news post when an existing canonical news record should just receive the migrated body
- leaving migrated body assets under `public/blog/...` instead of `public/news/<id>/...`
- forgetting to update internal links inside the migrated article body
- leaving old blog records visible in `/blog` after moving their canonical body to news
- keeping noisy historical prefixes like `blog25-` in the final `public/news/<id>/...` asset names when the user wants cleaner route-local names

## Done criteria

- live / source / local news counts and titles are cross-checked
- missing news postings are added if any exist
- blog-backed news bodies are migrated into the existing canonical news MDX records when requested
- former blog-backed records are hidden and redirect to the canonical news URLs
- route-aligned news assets are copied and references updated
- targeted news/blog redirect tests pass
