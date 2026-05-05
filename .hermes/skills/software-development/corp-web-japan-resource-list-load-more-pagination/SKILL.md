---
name: corp-web-japan-resource-list-load-more-pagination
description: Add opt-in load-more pagination to corp-web-japan resource list pages like /blog and /whitepapers while preserving thin route files, ID-based loaded-range restoration, and compatibility with other list pages.
---

# corp-web-japan resource-list load-more pagination

Use this when a corp-web-japan list page built on `ResourceListPage` / `ResourceListItems` should switch from rendering the full list at once to a bottom-of-list "Load more" pattern.

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

### 1. Use 8 as the default chunk size

For corp-web-japan resource cards, `8` worked well because:
- it is even
- it fits desktop 2-column composition cleanly
- it still feels reasonable on mobile 1-column tall-card layouts
- common counts like 28 whitepapers fall into neat chunks (8/8/8/4)

Create a shared helper such as:
- `src/lib/resource-list-load-more.ts`

Keep in it:
- `DEFAULT_RESOURCE_LIST_CHUNK_SIZE = 8`
- `resolveResourceListVisibleCount(items, untilId, chunkSize)`
- `getResourceListNextVisibleCount(currentVisibleCount, totalCount, chunkSize)`
- `getResourceListLoadedRange(items, visibleCount)`

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
- shared list page delegates only the interactive behavior to a small client component

Good file split:
- `src/components/sections/resource-list-page.tsx` (server-compatible shared shell)
- `src/components/sections/resource-list-load-more.tsx` (`"use client"`)

### 4. Make shared `ResourceListPage` opt-in, not globally changed

Important finding:
`ResourceListPage` is reused by other list pages (`/events`, preview/demo/use-case pages, etc.).

Do NOT make load-more mandatory on the shared component.
Instead:
- add an optional prop like `initialVisibleCount?: number`
- if provided, render the load-more client component
- if omitted, keep rendering the existing full `ResourceListItems`

This avoids breaking unrelated pages and keeps the rollout scoped to blog/whitepapers.

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

### 6. Read `searchParams` in the route and compute the initial count server-side

Pattern for the route:
- accept `searchParams?: Promise<{ until?: string | string[] }>`
- load items and resolved search params in parallel
- compute `initialVisibleCount = resolveResourceListVisibleCount(items, resolvedSearchParams?.until)`
- pass `initialVisibleCount` into `ResourceListPage`

This keeps the initial render/restoration deterministic.

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

## Verification checklist

Run at least:
- targeted ESLint on touched files
- `npm run typecheck`

Suggested touched-file lint pattern:
```bash
npm run lint -- \
  src/app/blog/page.tsx \
  src/app/whitepapers/page.tsx \
  src/components/sections/resource-list-page.tsx \
  src/components/sections/resource-list-load-more.tsx \
  src/components/sections/resource-list-section.tsx \
  src/content/resources.ts \
  src/lib/resource-list-load-more.ts \
  src/lib/publications/blog-publication-records.ts \
  src/lib/publications/whitepaper-publication-records.ts \
  src/lib/publications/event-publication-records.ts \
  src/lib/publications/use-case-publication-records.ts \
  src/lib/publications/aip-demo-publication-records.ts \
  src/lib/publications/acp-demo-publication-records.ts
```

Then:
```bash
npm run typecheck
```

## Pitfalls

- making load-more mandatory in `ResourceListPage` and unintentionally changing unrelated list pages
- adding `id` only to blog/whitepaper while forgetting other `ResourceItem`-typed publication builders
- using title-based React keys instead of `id`
- storing `?page=N` when the requirement is ID-based loaded-range restoration
- restoring to the exact matching item index instead of rounding up to the current chunk size
- using an effect to force-sync client state from props and tripping React lint
- leaving the default first chunk with a redundant `until` query param

## Done criteria

- `/blog` and `/whitepapers` initially show 8 cards
- the bottom button appends 8 more cards at a time
- the currently loaded ID range is shown below the grid
- the URL uses `?until=<id>` to restore the opened range
- back/forward restoration works through URL-derived initial state + remount keying
- unrelated shared list pages still render normally unless explicitly opted in
