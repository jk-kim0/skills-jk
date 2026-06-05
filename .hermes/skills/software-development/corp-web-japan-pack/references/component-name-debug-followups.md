# Component Name Debug follow-up marker authoring

Use this when a corp-web-japan PR adds or changes the platform Component Name Debug capability, or when reviewers report that named components are not visible on most pages.

## Durable lesson

The Component Name Debug runtime only displays names for DOM nodes that have a `data-component-name` marker. If the overlay/control exists but most pages show no names, the likely missing work is marker authoring, not overlay logic.

## Current implementation pattern from PR 592

- Marker attribute contract: `data-component-name`.
- Helper: `componentNameDebugProps("ReactComponentName")` from `src/lib/component-name-debug.ts`.
- PR 592 implemented the feature and initially marked mostly global header/debug menu surfaces such as `SiteHeader*` and `ComponentNameDebugMenuSection`.
- Most route/page/section surfaces need separate follow-up marker coverage.

## Follow-up workflow

1. Confirm whether the feature code exists on latest `origin/main` before describing or implementing follow-up work.
2. Search for existing markers:
   - `git grep -n "componentNameDebugProps" origin/main`
   - `git grep -n "data-component-name" origin/main`
3. Treat missing names on pages as a marker coverage gap unless the markers are present but the overlay still fails.
4. Add markers to existing meaningful DOM roots only:
   - route-level `main` wrappers, e.g. `HomePage`, `AipPage`, `AiCrewPage`
   - existing section component roots, e.g. `HomeHeroSection`, `AICrewResultsSection`, `AipValueSection`
   - existing cards/panels/CTA/list/detail surfaces that already own UI responsibility
5. Do not add wrappers, shells, or generic containers solely to make a debug label appear.
6. Prefer a phased coverage plan for broad sites:
   - common layout: footer, floating CTA, persistent navigation surfaces
   - primary marketing pages: home, AI Crew, AI Dashi, AIP, ACP, FDE
   - resource list/detail pages: blog, whitepapers, events, use cases, news
   - repeated shared cards and sidebars
7. Add lightweight source-level tests for marker coverage on representative pages/components. The core overlay behavior tests should remain separate from coverage tests.

## Pitfalls

- Do not frame this as a bug in the overlay when the page DOM simply lacks `data-component-name` markers.
- Do not create `FooWrapper`, `PageShell`, `ContentContainer`, or equivalent wrapper-only components for Component Name Debug.
- Keep marker names in React Component Name style: non-empty, no whitespace, beginning with an uppercase letter according to the current helper validation.
