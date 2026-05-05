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
- `ResourceListSidebarViewport` is for mobile horizontal overflow only
- `ResourceListSidebarNav` is the actual sticky target on desktop
- keep the `aside` as the full-height left column
- do **not** put `sticky` on the mobile overflow wrapper; that can break sticky behavior

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
