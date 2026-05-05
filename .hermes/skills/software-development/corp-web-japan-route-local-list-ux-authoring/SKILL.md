---
name: corp-web-japan-route-local-list-ux-authoring
description: Implement or refactor corp-web-japan internal/preview MDX list pages so page.tsx owns the title, description, sidebar links, and CTA copy, while shared components keep only list/layout primitives.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, route-local-authoring, mdx-list, sidebar, cta, nextjs]
---

# corp-web-japan route-local MDX list UX authoring

Use this when a corp-web-japan internal or preview list page should follow the repo's route-local authoring style, but the page still needs reusable functional list UX.

Typical targets:
- `src/app/internal/**/page.tsx`
- `src/app/t/**/page.tsx`
- demo/list UX example routes that should showcase a reusable MDX list pattern

## Goal

Make `page.tsx` the readable authoring surface for:
- page title
- page description
- sidebar link definitions
- CTA box copy
- CTA button labels and destinations

Keep extracted components only for:
- layout primitives
- sidebar rendering primitives
- item-list rendering
- small CTA container/button primitives

## Preferred structure

Good end state:
- `page.tsx` directly composes hero, sidebar, list, and CTA sections
- `page.tsx` contains the real visible copy and links
- shared components under `src/components/sections/**` are reduced to UI/layout primitives
- item-list rendering can stay extracted as a functional component such as `ResourceListItems`
- older routes can keep using a thin wrapper during migration

Bad end state:
- `page.tsx` passes a giant config object into a shared `ResourceListPage`
- sidebar links remain hidden inside the shared wrapper
- CTA copy and button wiring remain hidden inside the shared wrapper
- a new giant content object is moved into `page.tsx` instead of authored in JSX

## Recommended extraction boundary

Split the old shared list page into:
- hero primitives: section/title/description
- sidebar primitives: sidebar/container/list/item/link
- item-list renderer: receives items only
- CTA primitives: section/box/title/description/actions/button

Keep a compatibility wrapper if existing routes already depend on the old component:
- `ResourceListPage` can become a thin wrapper that assembles the new primitives
- new or refactored showcase pages should bypass that wrapper and author directly in `page.tsx`

## Workflow

1. Inspect the current list page wrapper and identify which values are hardcoded inside it.
2. Move visible page-specific authoring values into `page.tsx`:
   - title
   - description
   - sidebar links
   - active state
   - CTA headline/body/buttons
3. Extract only reusable rendering primitives into `src/components/sections/**`.
4. Keep list data loading in `page.tsx` or a publication-record helper, whichever already exists.
5. Preserve existing route behavior for other pages with a thin wrapper if changing them all at once would widen scope.
6. Run light verification first:
   - targeted eslint on touched files
   - `npm run typecheck`
7. For PR follow-up work, use a fresh worktree on the existing PR branch and push back to the same branch.

## Practical lesson

For internal MDX list UX demo work, the user wanted the same route-local authoring philosophy used on static marketing pages, but not a full rewrite of list rendering. The successful balance was:
- route owns authoring
- shared component owns rendering primitives
- old wrapper remains only as a compatibility layer

## Done criteria

- `page.tsx` visibly owns the page copy and links
- sidebar is reusable but not content-owning
- CTA box is reusable but not content-owning
- list renderer remains reusable for functional consistency
- verification passes
- if this is PR follow-up work, the existing PR is updated rather than replaced
