---
name: corp-web-japan-publication-hidden-redirect-audit
description: Audit corp-web-japan publication/routing changes for missing hidden-posting and redirect/canonicalization configuration, prioritizing content and route gaps over generic PR staleness review.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, publications, redirect, hidden, canonical, audit, nextjs]
---

# corp-web-japan publication hidden/redirect audit

Use this when reviewing corp-web-japan PRs or content changes involving:
- `src/content/blog/*.mdx`
- `src/content/news/*.mdx`
- `src/content/whitepapers/*.mdx`
- `src/content/events/*.mdx`
- `src/content/use-cases/*.mdx`
- `src/content/demo/**.mdx`
- detail routes under `src/app/**/[id]/page.tsx` and `src/app/**/[id]/[slug]/page.tsx`
- publication record loaders under `src/lib/publications/*-publication-records.ts`

## Why this skill exists

In corp-web-japan, a PR can look stale or duplicate at the Git level, but the more important review question may be whether the author missed:
- a `hidden: true` frontmatter flag for shadow/duplicate postings
- a `redirectUrl` for hidden/shadow records that should keep old detail URLs alive
- route-level canonical redirect handling for a content family that already parses `redirectUrl`

When the user is reviewing publication/routing work, prioritize these product-level gaps before generic PR-validity commentary.

## Review priorities

Order matters:

1. Check whether the content family supports `hidden` and `redirectUrl` in its record loader.
2. Check whether list derivation excludes only hidden records while preserving full id lookup.
3. Check whether both detail routes (`[id]` and `[id]/[slug]`) honor `redirectUrl` before canonical local redirects or rendering.
4. Check actual MDX corpus for shadow/duplicate entries missing `hidden` and/or `redirectUrl`.
5. Only after that, comment on Git/PR staleness if still relevant.

## Audit workflow

### 1. Inspect record-loader support

Read the relevant `src/lib/publications/*-publication-records.ts` file and confirm:
- frontmatter type includes `hidden?: boolean` and `redirectUrl?: string`
- normalization includes:
  - `hidden: frontmatter.hidden === true`
  - `redirectUrl: typeof redirectUrlValue === "string" ? redirectUrlValue : undefined`
- cache/list logic includes:
  - `const recordsById = new Map(...records...)`
  - `const visibleRecords = records.filter((record) => !record.hidden)`

Important rule:
- Hidden records must remain in `records` and `recordsById`.
- Only list pages should filter them out.

### 2. Inspect route-level redirect handling

For the same family, read both:
- `src/app/<section>/[id]/page.tsx`
- `src/app/<section>/[id]/[slug]/page.tsx`

Expected pattern in BOTH routes:

```ts
if (record.redirectUrl) {
  redirect(record.redirectUrl);
}
```

Then canonical local redirect logic should follow:
- id-only route redirects to canonical `/<section>/<id>/<slug>`
- slug route redirects mismatched slug to canonical `/<section>/<id>/<slug>`

Common gap:
- record loader already supports `redirectUrl`
- but one content family's routes forgot to apply it
- this creates a latent bug even if the current corpus has no redirecting item yet

### 3. Inspect actual MDX corpus for missing hidden/redirect setup

Search MDX frontmatter for:
- `hidden: true`
- `redirectUrl:`

Then look for likely shadow/duplicate cases by comparing:
- same title or nearly same title across families
- same date across families
- same organization/event name across blog vs news
- same story represented once as local long-form content and once as a local/external news item

Practical heuristic:
- if a blog/news/whitepaper item exists mainly to preserve an old detail URL after content moved to another family, it usually should be:
  - `hidden: true`
  - plus `redirectUrl: "/target/id/slug"` or an external URL
- if a hidden item has no `redirectUrl`, flag it as a likely missing configuration candidate

### 4. Distinguish current bug vs latent bug

Report two categories separately:

#### Actual missing content configuration
Example shape:
- `src/content/blog/23.mdx` has `hidden: true`
- but lacks `redirectUrl`
- while sibling shadow records in the same pattern (`blog/25`, `blog/26`) already use hidden+redirect
- and there is an obvious destination candidate in another family (for example `news/12`)

#### Route implementation gap
Example shape:
- `src/lib/publications/event-publication-records.ts` supports `redirectUrl`
- but `src/app/events/[id]/page.tsx` and `src/app/events/[id]/[slug]/page.tsx` do not redirect on `record.redirectUrl`
- current event corpus may not use it yet, but the implementation is incomplete

## Good reporting format

Use concise buckets:

- Confirmed already-correct cases
- Missing content configuration candidates
- Missing route/canonicalization implementation
- Confidence / notes

Example:

```text
Confirmed correct:
- blog/25 and blog/26 are hidden shadow records with redirectUrl set
- whitepapers/25 is hidden and redirects to whitepapers/24

Missing content configuration candidate:
- blog/23 is hidden but lacks redirectUrl
- it appears to correspond to news/12 by date/topic, so this is a likely missing redirect case

Missing route implementation:
- event record loader supports redirectUrl
- events [id] and [id]/[slug] routes do not apply redirectUrl before canonical redirect/render
```

## Pitfalls

- Spending the whole review on whether the PR is stale while missing the actual publication-routing defect
- Treating `hidden: true` alone as sufficient for a shadow record when the old detail URL should still resolve somewhere meaningful
- Checking only the slug route and forgetting the `[id]` route
- Assuming a family is fine because another family already implements the pattern
- Confusing external-news archive items with local canonical content; decide whether the intent is local rendering, redirect, or shadow preservation

## When this matters most

Use this especially when the user reacts along the lines of:
- "you should be finding missing hidden posting / redirect settings"
- "review whether routing/content setup is missing anything"
- "check canonical redirects and shadow posting behavior"

That is a signal to prioritize content/routing contract audit over generic Git review.