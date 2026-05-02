---
name: corp-web-japan-news-mdx-redirect-rollout
description: Maintain corp-web-japan local MDX-backed news so the list stays local, selected posts render local bodies, and redirect-backed items defer to source URLs via frontmatter redirectUrl.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, news, mdx, redirects, content-migration]
---

# corp-web-japan news MDX + redirect rollout

Use this when working on `corp-web-japan` local news under `src/content/news/*.mdx`.

## Current model

The local news system is not uniform:

- `/t/news` lists local news records from `src/content/news/*.mdx`
- list items should link to local canonical news URLs: `/news/:id/:slug`
- news detail routes read frontmatter from `src/content/news/*.mdx`
- if a news record has `redirectUrl`, `/news/:id` and `/news/:id/:slug` should redirect there before rendering local MDX
- if a news record has no `redirectUrl`, it renders local MDX normally

## Important repo-specific findings

### Source of truth for news inventory
The upstream inventory for Japan news cards lives in:

- `../corp-web-contents/pages/company/news/ja/content.mdx`

That file contains a `NewsList items={[ ... ]}` array.

The array order matches the visible public order on:

- `https://www.querypie.com/ja/company/news`

In the current migrated corpus, source order maps newest -> oldest onto local ids:
- source item 1 -> local news `14`
- source item 2 -> local news `13`
- ...
- source item 14 -> local news `1`

### Which local news posts stay local vs redirect
Current stable policy learned from the migration:

- local news `13` and `14` are canonical local content posts with full local bodies
- local news `1` through `12` should usually keep a local list entry but redirect from the local detail route to the original source URL via frontmatter `redirectUrl`

This mirrors the original public news behavior while preserving local canonical list/detail structure.

### Blog-backed news migration case
Two news items originally pointed at internal blog posts rather than external news URLs:

- source `/features/documentation/blog/25/terrasky-mitoco-buddy` -> local news `13`
- source `/features/documentation/blog/26/mitoco-buddy-release` -> local news `14`

For those:
- move the full article body into the existing news posts `13` and `14`
- keep `13` and `14` as local-rendered news posts without `redirectUrl`
- convert blog `25` and `26` into hidden shadow records with `redirectUrl` to the corresponding news canonical URL

### Route-aligned asset policy for migrated news bodies
When body content is migrated into a news post:
- keep assets under `public/news/<id>/...`
- use short, route-local names
- avoid legacy prefixes like `blog25-` when the asset now belongs to a news post

Example:
- prefer `public/news/13/image-1.png`
- not `public/news/13/blog25-image-1.png`

Update MDX `ArticleFileImage filepath="public/news/<id>/..."` references accordingly.

## Frontmatter contract
Current usable news frontmatter:

```yaml
---
id: "12"
slug: "payroll-querypie-ai-security-partnership"
title: "..."
description: "..."
date: "2025年8月5日"
redirectUrl: "https://news.nicovideo.jp/..."
heroImageSrc: "/news/12/thumbnail.png"
author: "querypie"
relatedIds:
  - "14"
  - "13"
  - "11"
---
```

Notes:
- `redirectUrl` is optional
- if `redirectUrl` is set, both `/news/:id` and `/news/:id/:slug` should redirect there
- keep `heroImageSrc` route-aligned even for redirect-backed items

## Tests: what to do and what NOT to do

### Good local tests
Keep repo-local tests focused on:
- local MDX file existence and metadata sanity
- route behavior (`redirectUrl` respected before render)
- route-aligned asset references and files
- moved test organization under `tests/news/` and `tests/blog/`

### Avoid this CI trap
Do NOT make repo CI depend on sibling checkout data like:
- `../../../corp-web-contents/...`

Reason:
- that sibling repo exists on the user's machine, but not on GitHub Actions runners
- a parity test against `../corp-web-contents` will fail in CI with `ENOENT`

If you need cross-repo parity during investigation, do it interactively during development, not as a required repo CI test.

## Useful verification
For news-only follow-up work:

```bash
node --test tests/news/*.test.mjs tests/blog/*.test.mjs
```

## Practical workflow
1. Inspect `../corp-web-contents/pages/company/news/ja/content.mdx`
2. Map source item order to local ids `14 -> 1`
3. Decide which items stay local-rendered and which should use `redirectUrl`
4. Update `src/content/news/*.mdx` frontmatter
5. If migrating a former blog-backed item, copy body/assets into the existing news post and keep route-aligned asset names
6. If a former blog post is superseded by news, hide the blog post and set its `redirectUrl` to the canonical news URL
7. Update only repo-local tests; avoid sibling-repo CI dependencies

## Done criteria
- `/t/news` still links to local `/news/:id/:slug`
- redirect-backed news items redirect from local detail routes to the original source URL
- canonical local-body news items render locally
- migrated assets live under `public/news/<id>/...` with route-local names
- no repo CI test requires `../corp-web-contents` to exist
