---
name: corp-web-japan-events-mdx-webinar-migration
description: Implement `/t/events` plus MDX-backed local event routes in corp-web-japan by importing the Japanese webinar corpus from corp-web-contents.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, events, webinars, mdx, migration, nextjs]
    related_skills: [corp-web-japan-origin-main-worktree-safety, corp-web-japan-local-whitepaper-detail-route, blog-posting, whitepaper-posting]
---

# corp-web-japan event MDX webinar migration

Use this when the user wants corp-web-japan events to work like the local blog/whitepaper MDX flows, especially with a preview list at `/t/events` and source content imported from `../corp-web-contents/pages/features/demo/webinars/**/ja/content.mdx`.

## Goals

- keep `/events` list launch-gated unless the user explicitly asks to un-gate it
- add `/t/events` as a non-indexed preview list page
- back `/events/:id/:slug` from local checked-in MDX under `src/content/events/*.mdx`
- add `/events/:id` canonical redirect route
- derive event list items from an event publication-record loader instead of a handwritten array
- store event thumbnails under `public/events/<id>/thumbnail.png`

## Current implementation pattern

Mirror the local blog/whitepaper structure:

- `src/content/events/<id>.mdx`
- `src/content/publications/event-publication-records.ts`
- `src/lib/publications/get-event-publication-post.ts`
- `src/app/events/[id]/[slug]/page.tsx`
- `src/app/events/[id]/page.tsx`
- `src/app/t/events/page.tsx`
- `public/events/<id>/thumbnail.png`

Keep `src/app/events/page.tsx` as the launch-gated public list route, but switch its `items` source to the MDX-derived event list.

## Source lookup

Japanese webinar source files currently live at:

- `../corp-web-contents/pages/features/demo/webinars/<id>/<slug>/ja/content.mdx`

The representative hero image usually comes from frontmatter:

- `ogImage: "public/webinar/<file>.png"`

Copy that file to:

- `public/events/<id>/thumbnail.png`

## Frontmatter contract for local event MDX

Use a blog/whitepaper-like shape:

```yaml
---
id: "27"
slug: "air-company-ai-agent-security-webinar"
title: "..."
description: "..."
date: "2026年4月9日"
heroImageSrc: "/events/27/thumbnail.png"
eventLabel: "ウェビナー"
hideHeroImageOnDetail: true
author: "querypie"
relatedIds:
  - "26"
  - "25"
  - "24"
---
```

Notes:
- keep `id` as a string
- `eventLabel` is the single event-type badge shown on `/t/events`; use values like `イベント`, `ウェビナー`, `ワークショップ`, or `研修`
- `hideHeroImageOnDetail: true` hides the top hero image only on the detail page; omit it or set `false` to keep the current default rendering
- the current list-page fallback remains `イベント` when `eventLabel` is omitted
- convert source ISO dates to display-ready Japanese date strings used by the local site
- convert source `relatedPosts` legacy webinar paths into `relatedIds`
- use `author: "querypie"` unless a different local author is explicitly needed

## MDX normalization rules

When importing from `corp-web-contents` webinar MDX:

1. remove the old source frontmatter and replace it with the local frontmatter above
2. rewrite `filepath="public/webinar/..."` to `filepath="public/events/<id>/thumbnail.png"`
3. if the MDX starts with a top-of-body hero block like:
   - `<Box center><ArticleFileImage filepath="public/webinar/..." ... /></Box>`
   remove that duplicate block, because the page shell already renders `heroImageSrc`
4. strip leading `<br />` noise left by the source
5. ensure the local MDX no longer contains:
   - `public/webinar/`
   - `/features/demo/webinars/`

## Required MDX component support

The webinar corpus may use these components:

- `ArticleYoutubeGatingForm`
- `EmailLink`
- `ButtonLink`
- `Box`
- `ArticleFileImage`

Local support rules:
- `ArticleYoutubeGatingForm` can be a thin pass-through wrapper to the existing `Youtube` component
- `EmailLink` should render a simple `mailto:` link
- keep `ButtonLink`, `Box`, and `ArticleFileImage` registered in the publication MDX component map

## Loader pattern

`event-publication-records.ts`
- scan `src/content/events/*.mdx`
- parse frontmatter with YAML
- cache records and derived list items
- derive list item hrefs with `getPublicationHref("event", id, slug)`
- badge text should be `イベント`

`get-event-publication-post.ts`
- load the MDX body from `record.sourcePath`
- render with `renderPublicationMdx`
- build TOC with `extractHeadingsFromMdx`
- resolve author via `resolveArticleAuthors`
- build related items from `relatedIds`
- expose `getEventPublicationPost(id)` and `getEventPublicationHref(id, slug)`

Important:
- do not make the event post loader slug-sensitive
- canonicalization belongs in the route, not the loader

## Route behavior

### `/events/[id]/[slug]`
- load record by `id`
- redirect if `slug` mismatches the canonical slug
- render `getEventPublicationPost(id)`
- set canonical metadata to `/events/:id/:slug`
- set robots to `index: false, follow: false`

### `/events/[id]`
- load record by `id`
- redirect to `/events/:id/:slug`

### `/t/events`
- list page backed by `listEventPublicationItems()`
- canonical should be `/t/events`
- robots should be `noindex, nofollow`

## Files that typically change

- `src/content/resources/events.ts`
- `src/app/events/[id]/[slug]/page.tsx`
- `src/app/events/[id]/page.tsx`
- `src/app/t/events/page.tsx`
- `src/lib/publications/mdx/components.tsx`
- new files under `src/content/events/`
- new files under `public/events/`
- new tests under `tests/`

## Tests to add

At minimum:

1. routing/preview test
   - `/t/events` exists and uses `listEventPublicationItems()`
   - `/events/[id]` redirects canonically
   - `/events/[id]/[slug]` loads by id and redirects only on slug mismatch
   - event loader uses `renderPublicationMdx` and `extractHeadingsFromMdx`

2. imported corpus test
   - exact expected Japanese event IDs are present as local MDX files
   - each event MDX uses `heroImageSrc: "/events/<id>/thumbnail.png"`
   - no `public/webinar/` references remain
   - no `/features/demo/webinars/` references remain

3. component support test
   - `ArticleYoutubeGatingForm` and `EmailLink` are registered in the MDX components map

## Verification

Lightweight local verification that worked well:

```bash
node --test tests/events-mdx-routing-and-preview.test.mjs tests/events-imported-ja-corpus.test.mjs
npx tsc --noEmit --pretty false
```

Then complete the normal git workflow:
- commit
- rebase on `origin/main`
- push
- create PR
- monitor `gh pr checks` until all checks finish

## Pitfalls

- accidentally reversing `id` and `slug` while parsing source paths
- keeping the event loader dependent on old HTML parsing in `src/lib/resource-posts.ts`
- leaving duplicate in-body hero images after the page shell already renders `heroImageSrc`
- creating a circular import by making event publication records depend on the event post loader for href generation
- forgetting `ArticleYoutubeGatingForm` or `EmailLink`, which can break imported webinar MDX rendering
- un-gating `/events` list when the user only asked for `/t/events`

## Done criteria

- `/t/events` exists and is non-indexed
- `/events/:id/:slug` renders local MDX
- `/events/:id` redirects canonically
- event list items come from MDX-derived event publication records
- Japanese webinar corpus is checked in under `src/content/events/*.mdx`
- route-aligned thumbnails exist under `public/events/<id>/thumbnail.png`
- event-specific tests pass
- branch is pushed and CI is green
