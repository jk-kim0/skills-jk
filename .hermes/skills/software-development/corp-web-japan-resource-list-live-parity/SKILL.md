---
name: corp-web-japan-resource-list-live-parity
description: Match a corp-web-japan resource list page or internal demo to the live QueryPie documentation list UX, including left-aligned hero copy and a truly sticky sidebar.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, resource-list, sidebar, sticky, live-parity, nextjs]
---

# Match corp-web-japan resource list UX to live QueryPie documentation

Use this when a corp-web-japan list page such as `/internal/mdx-list-demo`, `/blog`, `/whitepapers`, `/t/events`, or similar should visually/behaviorally match a live QueryPie documentation list page.

## When to use
- The user points to a live QueryPie documentation page and asks for the same layout/behavior.
- The task involves a left sidebar, list cards, hero title/description alignment, or sticky-on-scroll behavior.
- The page is route-authored in `src/app/**/page.tsx` but uses shared list primitives under `src/components/sections/`.

## Required inspection workflow
1. Open the exact reference URL in the browser first.
2. Inspect not only visible text structure but also computed layout/sticky behavior.
3. Use browser JS evaluation to capture:
   - `getBoundingClientRect()` for hero title, description, sidebar, and first card/list
   - `getComputedStyle()` for `position`, `top`, `fontSize`, `lineHeight`, `textAlign`
4. If sticky behavior matters, scroll the page and re-check the same element.

Useful browser-console probes:
```js
(() => {
  const nav = document.querySelector('main nav[aria-label="Sidebar Navigation"]');
  return {
    position: getComputedStyle(nav).position,
    top: getComputedStyle(nav).top,
    rect: nav?.getBoundingClientRect(),
  };
})()
```

## Key finding from whitepaper parity work
For the live QueryPie documentation whitepaper page:
- the hero title/description are left-aligned
- the hero text spans the main content width, not a narrow centered block
- the sidebar column width is about `240px`
- the sticky element is the actual `nav`, not the mobile overflow wrapper
- sticky top is about `128px`
- the sidebar starts on the same vertical line as the content card grid

## Correct implementation pattern
Use this structure in shared primitives / page composition:

```tsx
<ResourceListSidebar>
  <ResourceListSidebarLabel>...</ResourceListSidebarLabel>
  <ResourceListSidebarViewport>
    <ResourceListSidebarNav className="lg:sticky lg:top-[128px]" label="Sidebar Navigation">
      <ResourceListSidebarList>...</ResourceListSidebarList>
    </ResourceListSidebarNav>
  </ResourceListSidebarViewport>
</ResourceListSidebar>
```

Important:
- `ResourceListSidebarViewport` is for mobile overflow handling only
- `ResourceListSidebarNav` is the actual sticky target on desktop
- keep the `aside` as the full-height left column
- do **not** put `sticky` on the mobile overflow wrapper; that can break sticky behavior

## Mobile overflow diagnosis pattern
When the user reports that the demo/resource sidebar becomes too wide on phones, do not guess from desktop snapshots. Reproduce with a mobile viewport and measure the real overflow.

Use DevTools/mobile emulation or browser JS evaluation to capture:
- `window.innerWidth`
- `document.body.scrollWidth`
- sidebar `aside` width
- viewport wrapper `scrollWidth`
- sidebar list `scrollWidth`
- each link chip width

Useful probe:
```js
() => {
  const nav = document.querySelector('nav[aria-label="Sidebar Navigation"]');
  const viewport = nav?.parentElement;
  const aside = viewport?.parentElement;
  const list = nav?.querySelector('ul');
  const links = [...(nav?.querySelectorAll('a') || [])].map((a) => ({
    text: a.textContent?.trim(),
    width: Math.round(a.getBoundingClientRect().width),
  }));
  return {
    viewportWidth: window.innerWidth,
    bodyScrollWidth: document.body.scrollWidth,
    asideWidth: aside?.getBoundingClientRect().width,
    viewportScrollWidth: viewport?.scrollWidth,
    listScrollWidth: list?.scrollWidth,
    links,
  };
}
```

A common failure mode is this combination in the shared sidebar primitives:
- mobile `overflow-x-auto`
- list `flex`
- list `min-w-max`
- `nowrap` chip row

This creates a horizontally scrolling chip bar whose total width can exceed the mobile viewport, especially on resource pages with longer Japanese labels such as `ホワイトペーパー`.

## Preferred fix for mobile sidebar overflow
Preferred approach:
- keep the current desktop sticky vertical sidebar behavior
- change only the mobile layout so the category chips no longer force one long horizontal row

Current corp-web-japan preference:
1. bottom-sheet / drawer pattern for resource-style sidebars with 5+ items or longer Japanese labels
2. mobile grid / flex-wrap only for shorter, low-count category sets where seeing all options immediately is better
3. only if the design explicitly wants horizontal scrolling, shrink chip padding/font size as a fallback

Drawer pattern contract:
- keep mobile and desktop render trees separate
- render a mobile trigger button that shows the active label
- render the category links in a `role="dialog"` / `aria-modal="true"` bottom sheet
- keep the desktop sidebar as a separate `hidden lg:block` sticky nav
- keep `aria-expanded` on the trigger and close on backdrop/Escape

Default recommendation for resource families:
- use the drawer pattern instead of preserving horizontal scrolling
- remove mobile `min-w-max`
- remove the forced one-line `nowrap` row on mobile
- avoid relying on horizontal scroll as the primary mobile behavior
- keep desktop `lg:flex-col` / sticky behavior unchanged

Typical class-direction changes when using grid/flex-wrap instead of drawer:
- `ResourceListSidebarViewport`: reduce/remove mobile `overflow-x-auto` when moving to wrapped/grid mobile layout
- `ResourceListSidebarList`: replace `flex min-w-max gap-3` mobile behavior with `grid grid-cols-2 gap-3` or `flex flex-wrap gap-3`
- `ResourceListSidebarLink`: make mobile chips `w-full` and center them if using grid/wrap

## Verification additions
For mobile sidebar fixes, verify at least one demo page and one resource page in a mobile viewport after the change.
Check that:
- no sidebar row visually exceeds the viewport
- no unnecessary horizontal scroll remains for the sidebar area
- desktop sticky/sidebar behavior is unchanged

## Hero alignment pattern
If matching the live whitepaper page, use route-local authoring like:
- `ResourceListHeroSection className="text-left"`
- title and description with route-specified class overrides
- description should usually use `mx-0 max-w-none` rather than the default centered/narrow block

## Scope rule
If the request is only about an internal demo or one route, keep the change scoped there.
Do not automatically refactor all public list pages unless the user explicitly asks.
A safe approach is:
- add optional class hooks to shared primitives
- apply the live-parity overrides only in the target route

## Resource-list section taxonomy / helper placement
When a follow-up asks whether a resource-list helper belongs at `src/components/sections/` root or under a family directory, classify ownership before moving files:
- keep broad shared entry surfaces at root when they are intentionally imported across many resource/demo/publication list routes
- move helper-only implementation details under a family directory when they are only surfaced through a root entry or concrete sidebar component
- update source-reading tests at the same time because this repo has tests that read component files by exact path

Current pattern from issue #432:
- keep `src/components/sections/resource-list-section.tsx` as the root shared entry
- move the drawer helper to `src/components/sections/resource-list/mobile-sidebar-drawer.tsx`
- keep `resource-list-section.tsx` re-exporting `ResourceListMobileSidebarDrawer` from that family helper path so existing callsites can continue importing from the shared entry
- update `tests/resource-list-page-structure.test.mjs` to read `src/components/sections/resource-list/mobile-sidebar-drawer.tsx`

Do not move `resource-list-section.tsx` itself just because its helper moved; it remains a broad shared primitive/entry unless the user explicitly asks to collapse the root entry too.

## Verification
Run the lightest checks first:
```bash
npx eslint src/app/<target>/page.tsx src/components/sections/resource-list-section.tsx
npm run typecheck
```

If the user reports the sticky behavior is still wrong, re-open the live reference page and compare the exact sticky target hierarchy (`aside` -> viewport wrapper -> `nav`) before making further changes.

## Pitfalls
- applying `sticky` to a wrapper that also handles overflow
- assuming a visually similar structure is enough without checking computed `position: sticky`
- keeping the hero centered when the live reference is left-aligned
- changing unrelated list pages when the request only targets one internal demo
