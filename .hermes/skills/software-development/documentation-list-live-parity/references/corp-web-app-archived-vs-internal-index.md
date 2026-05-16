# corp-web-app archived vs internal index parity investigation

Session context: after PR 702 added `/archived`, the user reported that `https://stage.querypie.com/ko/archived` was much harder to read than `https://stage.querypie.com/ko/internal`.

## Evidence gathered

Compared exact deployed URLs in the browser:
- `https://stage.querypie.com/ko/archived`
- `https://stage.querypie.com/ko/internal`

Source files on latest main:
- `src/app/layout.tsx`
- `src/components/layout/main/ui/main.component.tsx`
- `src/components/layout/main/ui/main.module.css`
- `src/app/archived/archived-index-page.tsx`
- `src/app/archived/archived-pages.ts`
- `src/app/dynamic-page.tsx`
- `src/components/atomic/md-list/md-list.component.tsx`
- `src/components/atomic/md-list/md-list.module.css`
- `src/app/globals.css`

## Root cause pattern

The two pages looked conceptually similar but were rendered through different paths.

`/ko/internal` was served through the dynamic MDX path:
- `dynamic-page.tsx` evaluated MDX with `commonMdxComponents()` / `serverMdxComponents()`.
- MDX `<ul>`/`<li>` became `MdUnorderedList` / `MdListItem` classes.
- The default dynamic-page branch appended `DownloadBottom`, producing the polished CTA below the list.

`/ko/archived` was route-local TSX:
- `src/app/layout.tsx` already wrapped children in `<Main hasHeader>`.
- `archived-index-page.tsx` rendered another inner `<main>` with inline `maxWidth` but no `width: 100%`.
- The outer `Main` has flex column + `align-items: center`, so the inner main shrank to content width.
- Plain `<ul>/<li>/<Link>` was affected by global reset: `ul { list-style: none; }` and `a { color: inherit; text-decoration: none; }`.

Observed computed-style differences on stage:
- archived inner main width: about 520px; list item width: about 460px.
- internal content/list width: about 1200px.
- archived list markers: none; link color inherited body color; no underline.
- internal list markers: disc; link color blue; underline.

A secondary issue: `src/app/archived/archived-pages.ts` listed only `why-querypie-acp` and `become-a-parter`, while latest main also had `simplified-access-control` available under `/ko/archived/simplified-access-control`.

## Recommended fix pattern

For route-local index pages that should be readable like an internal/demo list:
1. Do not nest `<main>` under the root layout `<Main>`; use `<section>` or `<div>`.
2. Give the inner container `width: 100%` plus an explicit max width and route-appropriate padding.
3. Do not rely on browser/default list/link styles in this codebase. Add route-local CSS module classes or use shared components for list markers, link color, underline/focus states, and spacing.
4. If parity with `/internal` includes the bottom CTA, add the CTA explicitly; do not assume route-local pages get dynamic-page CTA injection.
5. Keep the explicit index registry synchronized with actual archived child routes and test that newly added routes appear in the index.

## Verification ideas

- Browser computed-style check on a representative list item before/after.
- Unit test: every intended archived route appears in the index registry.
- Structure test: archived index does not create nested `main` landmarks.
