---
name: corp-web-v2-mdx-list-pagination
description: Implement blog/white-paper MDX list page.tsx routes in corp-web-v2 using button-based server pagination with ?page=, and align demo list UX to the same pattern without converting demo to MDX.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# corp-web-v2 MDX list pagination

Use this skill when the user asks to add or revise public content list pages for MDX-backed content in `corp-web-v2`, especially `blog` and `white-paper`, and wants pagination behavior reviewed or unified with existing public lists such as `demo`.

## Key decision

Prefer button-based server pagination using `page.tsx` + `?page=` query params over infinite scroll.

Why this is the preferred default here:
- Better SEO for public content lists
- Shareable, refresh-safe URLs
- Clear browser back/forward behavior
- Simpler App Router server-page implementation
- Matches the user's preference from this repo task

## Important repo-specific findings

- Real MDX list targets are currently `blog` and `white-paper` under `src/content/mdx/**`.
- `demo` is **not** an MDX list source in this repo snapshot; do not try to convert demo list loading to the MDX loader unless explicitly requested.
- For `demo`, reuse the same pagination UX and query-param pattern on the existing managed-content list page instead.
- Add public list routes to `src/app/sitemap.ts` when you introduce new list pages.
- Canonical metadata for paginated pages must use the normalized/clamped page number, not the raw `searchParams.page`, or out-of-range URLs can canonicalize incorrectly.
- Hard scope guardrail: in `corp-web-v2`, requests about route cleanup, canonical URL alignment, pagination UX, or list-page consistency do **not** imply permission to modify CMS-managed or authored-content files. Unless the user explicitly authorizes the exact file/subtree, do not change:
  - `src/app/[locale]/features/demo/**`
  - `src/content/documentation/**`
  - other CMS/authored managed HTML/Tiptap/JSON content files
- If a “small supporting change” or redirect cleanup appears to require one of those files, stop and ask instead of widening scope. Treat these as hard protected paths, not soft preferences.

## Recommended implementation shape

### 1. Add shared pagination utilities

Create a shared utility such as `src/features/pagination.ts` with:
- `parsePageParam(value?: string): number`
- `paginateItems(items, requestedPage, pageSize)`
- `buildPaginatedHref(pathname, page, searchParams?)`

Behavior:
- Invalid, empty, non-integer, or `< 1` pages normalize to `1`
- Requested pages above the last page clamp to the last page
- `page=1` should be omitted from the generated URL
- Preserve other query params when advancing pages

### 2. Add shared pagination UI

Create a small public component, e.g. `src/components/common/PaginationNav.tsx`.

Expected behavior:
- Render previous/next buttons only when applicable
- Show current page / total pages
- Hide or disable previous/next affordances at boundaries
- Localize button labels for `en`, `ko`, `ja`

### 3. Build an MDX list loader for blog/white-paper

Create a server-only loader, e.g. `src/features/mdx/list.ts`.

Suggested responsibilities:
- Read directory entries under `src/content/mdx/<category>`
- For each slug directory, load locale MDX with English fallback via existing loader pattern
- Render frontmatter through the existing MDX renderer/utilities
- Return lightweight list items only: id, title, description, dateIso, href, imageSrc
- Sort by date descending, then numeric id descending as a tiebreaker

Important typing note:
- If this loader is only for public MDX list pages, do **not** type it as the broader `MdxCategory` if that union also contains non-list categories like `demo`.
- Introduce a narrower type such as `MdxListCategory = Extract<MdxCategory, "blog" | "white-paper">`.
- Otherwise, helper records like list page copy tables will become incorrectly required to support unrelated categories.

### 4. Add list-page copy helper

A small file like `src/features/mdx/pageCopy.ts` is sufficient for page title / metadata title.

Use the narrower list-category type here too.

### 5. Add public list page UI

A shared presentational component like `src/components/pages/mdx/MdxContentListPage.tsx` works well.

Typical structure:
- Page title
- Card grid
- Optional empty state
- PaginationNav at the bottom
- Existing CTA section at page end if consistent with surrounding public pages

### 6. Implement route pages

Add:
- `src/app/[locale]/blog/page.tsx`
- `src/app/[locale]/white-paper/page.tsx`

Pattern:
- Validate locale with existing `isLocale()` / `notFound()` flow
- Read `searchParams.page`
- Load all list items
- Paginate server-side
- Render the shared list page component
- Format dates with existing public date helper

### 7. Generate metadata carefully

In `generateMetadata()`:
- Re-parse `searchParams.page`
- Load enough data to compute the normalized page via `paginateItems(...)`
- Build canonical with the clamped page number

Example principle:
- If `/blog?page=999` renders the last page, canonical should also point to that last real page, not `?page=999`.

### 8. Apply the same UX to demo, but do not MDX-convert it

For `src/app/[locale]/features/demo/page.tsx`:
- Keep the existing managed-content data source
- Add `page` to `searchParams`
- Paginate the already-filtered items server-side
- Preserve category filter in generated page links using `URLSearchParams`
- Update `generateMetadata()` canonical to preserve category and normalized page as appropriate

Also pass new props through existing components such as:
- `DemoListClientPage.tsx`
- `DemoListPage.tsx`

## Tests to add first

Prefer TDD with focused tests before implementation.

Useful test files:
- `src/features/pagination.test.ts`
- `src/features/mdx/list.test.ts`
- `src/components/common/PaginationNav.test.tsx`

Cover at minimum:
- page param normalization
- pagination slicing and page counts
- paginated href generation with preserved query params
- MDX list loader sorting and null-source exclusion
- pagination nav rendering on first/last/middle pages

## Verification workflow

1. Run targeted tests first:
   - `npm run test:run -- src/features/pagination.test.ts src/features/mdx/list.test.ts src/components/common/PaginationNav.test.tsx`
2. Check `git diff --check`
3. Run repo typecheck if needed, but distinguish pre-existing failures from regressions
4. Ensure sitemap includes any newly added public list routes
5. Commit, push, create Draft PR, and summarize the pagination decision in the PR body

## PR notes to include

Document clearly that:
- button-based server pagination was chosen over infinite scroll
- `blog` / `white-paper` are real MDX list sources
- `demo` only adopts the same UX pattern and remains managed-content based
- paginated canonical behavior was handled intentionally

## Pitfalls

- Do not assume `demo` has MDX source under `src/content/mdx`
- Do not canonicalize using raw page input when content is clamped to another page
- Do not forget sitemap updates for new public list routes
- Do not widen list-only helpers to unrelated `MdxCategory` members if the union contains categories that are not valid list-page targets
