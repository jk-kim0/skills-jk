---
name: corp-web-japan-publication-related-items-contract
description: Unify and maintain related-items behavior across corp-web-japan publication loaders, and evaluate when cross-type related links need a new frontmatter schema.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, publications, mdx, related-items, frontmatter, refactor]
---

# corp-web-japan publication related-items contract

Use this when changing how publication detail pages derive `relatedItems` for:
- blog
- news
- whitepaper
- use-case
- AIP demo
- ACP demo
- event

## Current desired contract

Apply one common behavior across all publication families:

1. If MDX frontmatter declares `relatedIds`, use those ids exactly as authored.
2. Do **not** filter out hidden records from explicit `relatedIds`.
3. Do **not** truncate explicit `relatedIds` to 3 items.
4. If `relatedIds` is empty or missing, fall back to the most recent 3 postings in the **same publication category**.
5. Exclude the current post id from both explicit and fallback related lists.
6. Preserve redirect-aware href generation for related cards.

This contract was implemented by extracting a single helper:
- `src/lib/publications/build-related-publication-items.ts`

## Important architectural finding

A previous implementation divergence existed:
- blog used a separate `build-related-publications.ts`
- standard publication loaders had a `fallbackToAllRecords` option
- some loaders truncated to 3 even when explicit ids were present
- blog also filtered through visible-only records

That divergence was not treated as a strong product requirement. The desired direction is one common helper and one common contract.

## Implementation pattern

### Shared helper

Prefer a shared helper with this shape:
- inputs: `records`, current `id`, `relatedIds`, `getHref`, optional `formatDate`
- explicit ids path: map ids directly to records, keep all valid matches, no `slice(0, 3)`
- fallback path: `records.filter(record => record.id !== id).slice(0, 3)`
- summary conversion should use redirect-aware hrefs

### Loader migration targets

All of these should use the same helper:
- `src/lib/publications/create-standard-publication-post-loader.ts`
- `src/lib/publications/get-publication-post.ts`
- `src/lib/publications/get-news-publication-post.ts`
- `src/lib/publications/get-whitepaper-publication-post.ts`

After migration:
- remove per-loader `buildRelatedItems(...)` helpers
- remove obsolete one-off helper files like `build-related-publications.ts`
- remove category-specific `fallbackToAllRecords` toggles if they only existed to control same-category fallback

## Verification pattern

Before implementation, add a source-level architecture test proving:
- a shared related-items helper exists
- all relevant loaders import it
- old one-off related helper implementations are gone
- old `fallbackToAllRecords` toggles are gone

Useful test file:
- `tests/src/lib/publications/related-publication-items-architecture.test.mjs`

Also run targeted routing/loader tests for all affected families:
- `tests/use-cases-mdx-routing-and-preview.test.mjs`
- `tests/aip-demo-mdx-routing-and-preview.test.mjs`
- `tests/acp-demo-mdx-routing-and-preview.test.mjs`
- `tests/events-mdx-routing-and-preview.test.mjs`
- `tests/news/mdx-routing-and-preview.test.mjs`
- `tests/blog/canonical-slug-routing.test.mjs`
- `tests/blog/frontmatter-visibility-and-redirect.test.mjs`
- `tests/whitepaper-frontmatter-visibility-and-redirect.test.mjs`
- `tests/src/lib/publications/standard-publication-post-loader-architecture.test.mjs`
- `tests/src/lib/publications/related-publication-items-architecture.test.mjs`

And run:
- `npx tsc --noEmit --pretty false`

## Cross-type related review rule

Do **not** enable cross-type related links by reusing the current `relatedIds: string[]` shape.

Reason:
- ids are category-local
- `"14"` does not indicate whether it means blog/news/whitepaper/event/etc.
- current resolvers/loaders assume one same-category record set

## Safe future direction for cross-type related

If cross-type related links are needed, introduce a new explicit schema instead of overloading `relatedIds`.

Recommended shape:

```yaml
relatedEntries:
  - category: news
    id: "14"
  - category: blog
    id: "29"
```

Benefits:
- category is explicit
- href resolution is deterministic
- migration can be incremental without breaking same-type `relatedIds`

## Guardrails

- Do not silently reinterpret existing `relatedIds` as cross-type ids.
- Do not reintroduce visible-only filtering for explicit ids unless the user explicitly wants that policy.
- Do not truncate explicit author-provided related lists.
- Keep fallback same-category unless the user explicitly changes the product rule.
- If event loaders use date formatting hooks, preserve them while migrating related-items logic.

## Recommended workflow

1. Start from fresh latest `main` worktree.
2. Add a failing architecture test first.
3. Extract/update the shared helper.
4. Migrate standard loader, then blog/news/whitepaper loaders.
5. Delete obsolete helper code.
6. Update source-based tests that reference old `fallbackToAllRecords` or inline helper patterns.
7. Run targeted tests and `tsc`.
8. In the PR body, state clearly whether cross-type related was only reviewed or actually implemented.
