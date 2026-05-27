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

Additional reusable follow-up pattern learned from PR layout polishing:
- If a PR first proves a desired UI by attaching many `className` overrides directly in `page.tsx`, and the user then asks to apply that validated design to the shared components, do not keep the route as the permanent source of spacing/typography fixes.
- Instead, promote the proven layout defaults into the shared primitives themselves (for example hero typography, sidebar width/sticky behavior, CTA spacing, shared CTA-button geometry/icon sizing), then remove the now-redundant page-level overrides.
- After promoting the defaults, also update any compatibility wrapper such as `ResourceListPage` so existing list routes inherit the same validated structure and a11y/container pattern (for example shared sidebar viewport + nav labeling), not just the one demo page.
- Verify by searching the route file for the old sizing/spacing override classes and confirming they are gone, while the shared component now carries the intended default values.

Additional narrow-refactor pattern learned from the `/t/events` + `/internal/events-demo` follow-up:
- When the user asks to refactor one repeated subsection block out of two route files, do not jump to a new high-level wrapper component.
- Prefer extracting a very small set of shared presentational primitives into the existing shared section file (for example heading container / eyebrow / title row / title / description) while keeping the actual copy authored directly in each `page.tsx`.
- Good fit: two or more routes share identical structural markup and classes, but the user still wants route-local ownership of the visible words.
- Bad fit: moving the entire subsection into a single opaque component that hides the headline/description strings from the route.
- For this pattern, add structure tests that assert:
  - the shared section file exports the new small primitives
  - each route imports and uses those primitives
  - the old inline class bundle is gone from the route source
- This keeps route-local authoring intact while still removing duplicated structure.

Additional lesson from the `/news` list-width regression:
- If you split a page-level `max-w-[1200px]` wrapper into separate intro and list primitives, do not assume the list still inherits the same width contract automatically.
- Re-check which primitive now owns the actual content-column width. Title-only wrappers such as `NewsPageIntro` should not silently become the only `max-w-[1200px]` boundary if the visible list/content block is expected to align to that same column.
- When the list block itself owns width and spacing (for example top margin plus `mx-auto max-w-[1200px]`), prefer a semantically strong name such as `*ListSection` over a vague wrapper name like `*ListArea`.
- Naming rule for this repo: if a wrapper carries real layout responsibility (content-column width, section spacing, list block boundary), treat it as a section primitive, not a generic area/container.
- Add a source-level regression assertion for the width contract when this kind of split happens so future spacing/title refactors do not accidentally free the list back to a wider parent section.

Additional lesson from cookie-preference route-local item authoring:
- When a list item component receives visible copy through prop-shaped APIs such as `label="..."` and `description={<p>...</p>}`, treat it as suspect under route-local authoring even if the copy technically lives in `page.tsx`.
- Prefer splitting the item into small child primitives so the route reads like authored JSX:
  - wrapper primitive owns only the list item shell, e.g. `<CookiePreferenceItem>...</CookiePreferenceItem>`
  - toggle/control primitive owns the toggle button + label wiring, e.g. `<CookiePreferenceToggleField id="necessary" disabled>必須 Cookie</CookiePreferenceToggleField>`
  - toggle description primitive owns only the semantic paragraph tag for the toggle's explanatory text, e.g. `<CookiePreferenceToggleDescription>...</CookiePreferenceToggleDescription>` renders a plain `<p>` internally for one-paragraph descriptions.
- Keep functional identifiers such as toggle IDs as explicit props on the control primitive, but author visible labels and prose as children.
- Do not require route files to wrap every one-paragraph description in `<p>` when the primitive always represents a paragraph; keep the route focused on visible prose and let the primitive own repetitive semantic markup.
- For legal-page-adjacent components, do not define page-specific typography classes in these cookie-preference primitives. Let the legal page / inherited legal text contract handle typography unless a separate shared token is explicitly introduced.
- After refactoring, search the route and shared component for the old prop API (`<XItem id=`, `label="`, `description={`, `label: string`, `description: ReactNode`), old vague names (`CookiePreferenceItemHeader`, `CookiePreferenceItemDescription`), route-owned paragraph wrappers such as `<CookiePreferenceToggleDescription><p>...`, and cookie-specific typography/CTA leftovers such as `CookiePreferenceCta*`, `text-[...]`, `font-*`, `leading-[...]`, `tracking-[...]`, or hex text colors; add structure tests that assert those old contracts are absent.

## Done criteria

- `page.tsx` visibly owns the page copy and links
- sidebar is reusable but not content-owning
- CTA box is reusable but not content-owning
- list renderer remains reusable for functional consistency
- verification passes
- if this is PR follow-up work, the existing PR is updated rather than replaced
