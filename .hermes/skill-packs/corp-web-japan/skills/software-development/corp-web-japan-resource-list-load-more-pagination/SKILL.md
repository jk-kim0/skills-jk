---
name: corp-web-japan-resource-list-load-more-pagination
description: Add opt-in load-more pagination to corp-web-japan resource list pages like /blog and /whitepapers while preserving thin route files, ID-based loaded-range restoration, and compatibility with other list pages.
---

# corp-web-japan resource-list load-more pagination

Use this when a corp-web-japan list page should switch from rendering the full list at once to a bottom-of-list "Load more" pattern.

Scope guard:
- If the user asks only for a plan, audit, or migration document, do not create the helper/component files in this skill. Instead, document these exact requirements as implementation directives: chunk size 12, `?until=<oldest-visible-id>`, `router.replace(..., { scroll: false })`, URL-derived initial count, and remount-key restoration.
- If a plan has an "open decision" about URL state, resolve it in the document as a directive when the user says to match the reference implementation.

Latest practical repo note:
- older iterations used a shared `ResourceListPage` wrapper
- current main-line implementation can be more direct and route-local: public `/blog` and `/whitepapers` now wire `ResourceListLoadMore` directly inside each route's `ResourceListContentSection`
- do not assume `ResourceListPage` is still the active integration point; inspect latest main first

Primary proven targets:
- `src/app/blog/page.tsx`
- `src/app/whitepapers/page.tsx`

## Goals

- Show an even default number of cards for balanced desktop/mobile composition.
- Append the next chunk when the user presses a button at the bottom.
- Preserve/restore the loaded range via URL state without numbered pagination.
- Keep the route file thin.
- Do not accidentally change unrelated list pages that still use the shared `ResourceListPage`.

## Proven implementation pattern

### 1. Use a shared chunk-size constant in the helper

Current practical repo lesson:
- the chunk size should be controlled from one shared helper constant, not repeated in routes/components/tests
- after follow-up tuning work, the current preferred value in this repo became `12`
- if the user later wants another value, change the helper constant first and verify the URL-restoration math still works

Create or keep a shared helper such as:
- `src/lib/resource-list-load-more.ts`

Keep in it:
- `DEFAULT_RESOURCE_LIST_CHUNK_SIZE = 12`
- `resolveResourceListVisibleCount(items, untilId, chunkSize)`
- `getResourceListNextVisibleCount(currentVisibleCount, totalCount, chunkSize)`
- `getResourceListLoadedRange(items, visibleCount)`

Focused follow-up rule learned from PR maintenance:
- if the task is only "change the default/incremental number of items" then a one-line constant change in `src/lib/resource-list-load-more.ts` is usually the right implementation
- add a narrow helper test that locks the constant to the intended value instead of rewriting unrelated route/component tests
- good path for that targeted regression test:
  - `tests/src/lib/resource-list-load-more.test.mjs`

### 2. Preserve range with `?until=<id>`, not `?page=N`

Do not use page numbers for this pattern.
Use the visible range's last-loaded document ID instead.

Recommended query contract:
- `?until=<oldest-visible-id>`

Recommended range display:
- `ID {newestVisibleId} ～ {oldestVisibleId}`

Behavior:
- no `until` query => show the default first chunk
- known `until` query => resolve the matching item index, then round up to the next full chunk size
- unknown `until` query => safely fall back to the default first chunk

Example:
- chunk size `8`
- `until=22` and item `22` is the 13th item in sorted order
- visible count becomes `16`, not `13`

This keeps button-based chunk UX while still restoring state from URL.

### 3. Put the interactive state in a dedicated client component

Do not convert the whole route page into a client component.
Keep the route page server-side and thin.

Recommended split:
- server page computes items + initial visible count from `searchParams`
- a small shared client component owns the interactive visible-count state

Current good file split in this repo:
- `src/components/sections/resource-list-load-more.tsx` (`"use client"`)
- `src/components/ui/progressive-load-more.tsx` (presentational button/progress UI)

Current practical route-local integration pattern:
- route imports `ResourceListLoadMore`
- route imports `resolveResourceListVisibleCount`
- route accepts `searchParams?: Promise<{ until?: string | string[] }>`
- route loads `[items, resolvedSearchParams]` with `Promise.all`
- route computes `initialVisibleCount = resolveResourceListVisibleCount(items, resolvedSearchParams?.until)`
- route renders `ResourceListLoadMore` directly inside `ResourceListContentSection`
- use a stable remount key like `key={`blog:${initialVisibleCount}`}` or `key={`whitepaper:${initialVisibleCount}`}` on the route-side caller when needed

Special current route lessons:
- `/events` has a featured/upcoming event plus a `pastEvents` list; apply load-more only to `pastEvents`, preserving `asof` handling in the same `searchParams` object and passing `resolvedSearchParams?.until` only to the load-more helper
- `/resources` aggregates multiple resource families whose raw numeric IDs can collide; before using the shared load-more helper, prefix aggregate-only item IDs such as `blog:28`, `whitepapers:28`, `manuals:7` while preserving original `href` values
- `/news` uses a distinct card/list component rather than `ResourceListItems`; preserve that UI by creating a small news-specific client wrapper (for example `NewsArticleLoadMore`) that reuses `ProgressiveLoadMore` and the shared helper functions while rendering `NewsArticleList` for visible items

### 4. Keep load-more opt-in and route-scoped

Important finding:
resource list routes in this repo do not all want the same behavior.

Current safe rule:
- wire load-more only in the target routes the user asked for
- current proven targets include public `/blog`, public `/whitepapers`, public `/demo/use-cases`, public `/demo/acp`, public `/events`, public `/resources`, public `/news`, and the internal `/internal/load-more` demo route
- keep other list pages such as `/manuals`, `/introduction-deck`, `/glossary`, and demo routes like `/demo/aip` on their existing rendering path unless the user explicitly expands scope
- if the task is an audit rather than implementation, classify routes by actual `ResourceListLoadMore`/route-specific wrapper + `resolveResourceListVisibleCount` usage on latest `origin/main`, not by memory or old preview-route names

This avoids accidental UX changes outside the intended surfaces and keeps coverage reports grounded in the current route taxonomy.

### 5. Ensure `ResourceItem`-like list items carry `id`

If range restoration is ID-based, the rendered item model needs the content ID.

In this repo, update the shared `ResourceItem` shape to include:
- `id: string`

Then ensure every publication-record builder that aliases to `ResourceItem` also populates `id`, not just blog/whitepaper.

At minimum, check these files if they type their list items as `ResourceItem`:
- `src/lib/publications/blog-publication-records.ts`
- `src/lib/publications/whitepaper-publication-records.ts`
- `src/lib/publications/event-publication-records.ts`
- `src/lib/publications/use-case-publication-records.ts`
- `src/lib/publications/aip-demo-publication-records.ts`
- `src/lib/publications/acp-demo-publication-records.ts`

Also switch list rendering keys from unstable title-based keys to `item.id` when possible.

### 6. Read `searchParams` in each target route and compute the initial count server-side

Pattern for the route:
- accept `searchParams?: Promise<{ until?: string | string[] }>`
- load items and resolved search params in parallel
- compute `initialVisibleCount = resolveResourceListVisibleCount(items, resolvedSearchParams?.until)`
- render `ResourceListLoadMore` with `items` and `initialVisibleCount`

Current proven targets:
- `src/app/blog/page.tsx`
- `src/app/whitepapers/page.tsx`
- `src/app/internal/load-more/page.tsx`

This keeps the initial render/restoration deterministic while staying route-local.

### 7. Update the URL from the client with `router.replace(..., { scroll: false })`

When the button is pressed:
- compute the next visible count
- append the next chunk locally
- update the query string to `until=<oldestVisibleId>` for the new visible range
- use `router.replace` with `scroll: false`

For the first/default chunk, delete the `until` param rather than storing redundant query state.

### 8. Handle back/forward query restoration without effect-based state syncing

Important experiential finding:
A naïve `useEffect(() => setVisibleCount(...), [initialVisibleCount])` can trigger React lint errors (`react-hooks/set-state-in-effect`).

Safer pattern:
- initialize the client component state from `initialVisibleCount`
- in the parent shared component, render the client component with a key that changes when the restored visible count changes

Example idea:
- `key={`${activeCategory}:${initialVisibleCount}`}`

This lets the component remount cleanly when URL-derived state changes, including browser back/forward restoration, without an effect that synchronously sets state.

## UI recommendations

For this repo's current resource cards:
- place the button below the rendered card grid
- also show the currently loaded ID range and count, e.g. `(8/29件)`
- keep the button simple and explicit rather than infinite scroll

Recommended copy used in this repo:
- button: `もっと見る`
- pending state: `読み込み中...`
- range label: `表示中の範囲: ID {newest} ～ {oldest} ({visible}/{total}件)`

## Coverage audit workflow

Use this when the user asks which features/pages have or do not have load-more, or asks to refresh a living GitHub issue such as `corp-web-japan` #451.

1. Re-audit the latest baseline, preferably a detached worktree at `origin/main`, or use `git show origin/main:<path>` / `git ls-tree origin/main` if no file edits are needed. Do not trust a local `main` checkout that is behind `origin/main`.
2. Fetch `origin/main`, record the full SHA and short SHA, and inspect first-parent commits merged since the issue's last recorded baseline. If the new commits are unrelated to load-more, say that explicitly in the refreshed issue instead of silently no-oping.
3. Search for `ResourceListLoadMore`, `NewsArticleLoadMore`, `ProgressiveLoadMore`, `resolveResourceListVisibleCount`, and `ResourceListItems`.
4. Classify list/index routes by current route path and source file:
   - applied: route imports/uses `ResourceListLoadMore` and computes `initialVisibleCount` with `resolveResourceListVisibleCount`
   - news applied: route uses the route-specific `NewsArticleLoadMore` wrapper plus `resolveResourceListVisibleCount`, preserving `NewsArticleList`
   - not applied: route renders `ResourceListItems` directly or uses a separate list component without the load-more helper
   - internal/demo: classify separately from public routes
5. Include current content counts when they are cheap to derive from `src/content/**`; use them only as prioritization signals, not as proof that load-more is or is not needed.
6. For GitHub issue output, include the baseline commit SHA, the exact evidence pattern, applied routes, non-applied candidate routes, implementation notes for special layouts such as `/events` past-events-only pagination or `/resources` aggregate-list ordering, and the current GitHub Actions status for the audited SHA. If local build/test is intentionally skipped, state that the refresh is based on static inventory plus CI/staging status.
7. For repeated issue-refresh requests, update the issue even if the route classification did not change: refresh the timestamp/SHA, mention any newly merged unrelated PRs checked, and preserve the explicit “no high-priority follow-up” or remaining-scope status when still true.

Useful quick probes from a clean baseline:

```bash
rg "ResourceListLoadMore|ProgressiveLoadMore|resolveResourceListVisibleCount|ResourceListItems" src/app src/components src/lib
find src/content -path '*.mdx' | sed 's#^src/content/##' | cut -d/ -f1-2 | sort | uniq -c
```

## Verification checklist

Run at least:
- focused node tests for the touched route/helper files
- `npm run typecheck`

Current useful targeted tests:
```bash
node --test tests/src/lib/resource-list-load-more.test.mjs
node --test tests/src/app/blog/page.test.mjs tests/src/app/whitepapers/page.test.mjs
node --test tests/src/app/demo/use-cases/page.test.mjs tests/src/app/demo/acp/page.test.mjs
node --test tests/src/app/events/page.test.mjs tests/src/app/resources/page.test.mjs tests/src/app/news/page.test.mjs
node --test tests/src/components/ui/progressive-load-more.test.mjs
```

When adding a route-specific wrapper or new tests, also run:
```bash
node scripts/ci/assert-test-groups.mjs
npm run typecheck
```

Existing source-reading contract tests can fail even when the new route-specific load-more tests pass. After changing an existing list route from direct full-list rendering to `ResourceListLoadMore` or a route-specific wrapper, search and update older tests that still assert direct render patterns such as `<ResourceListItems items={...} />`, `<NewsArticleList ... />`, or absence of load-more imports. Known places that have caught stale contracts:
```bash
rg "ResourceListItems|NewsArticleList|ResourceListLoadMore|NewsArticleLoadMore|resolveResourceListVisibleCount" tests
```
For public route changes, include broader groups such as:
```bash
npm run test:publications
npm run test:routing-seo
```
If `origin/main` advances before push, rebase onto latest `origin/main` and rerun the failing groups after the rebase before force-pushing the PR branch.

If the fresh worktree has no local `node_modules` and the root checkout has dependencies installed, a temporary PATH-only typecheck can avoid a slow install:
```bash
PATH=/path/to/root/node_modules/.bin:$PATH npm run typecheck
```

Then:
```bash
npm run typecheck
```

## Pitfalls

- making load-more mandatory in `ResourceListPage` and unintentionally changing unrelated list pages
- adding `id` only to blog/whitepaper while forgetting other `ResourceItem`-typed publication builders
- applying raw numeric IDs to aggregate `/resources` lists where different families can share the same ID; prefix aggregate-only IDs before `?until=` restoration
- forcing `/news` into `ResourceListItems` and losing the existing news card design; use a news-specific wrapper around `NewsArticleList` instead
- applying load-more to the entire `/events` page and accidentally paginating the featured/upcoming event; paginate only `pastEvents`
- using title-based React keys instead of `id`
- storing `?page=N` when the requirement is ID-based loaded-range restoration
- restoring to the exact matching item index instead of rounding up to the current chunk size
- using an effect to force-sync client state from props and tripping React lint
- leaving the default first chunk with a redundant `until` query param

## Done criteria

- `/blog` and `/whitepapers` initially show 12 cards
- the bottom button appends 12 more cards at a time
- the URL uses `?until=<id>` to restore the opened range
- the internal `/internal/load-more` demo still uses the same shared helper logic
- back/forward restoration works through URL-derived initial state + route-side initial-count wiring
- unrelated list pages still render normally unless explicitly opted in
