---
name: react-rsc-children-slot-detection
description: Fix client components that lose server-authored child slot content because they identify children by `node.type === SomeComponent` across a React Server Component to Client Component boundary.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [react, nextjs, rsc, client-components, children, debugging]
---

# React RSC children slot detection

Use this when a Next.js or React app has this pattern:
- a server component authors JSX children like `<Tab>` / `<Step>` / `<Slot>`
- a client component receives those children and extracts them with `Children.toArray(...).filter(...)`
- some or all authored text appears to vanish at runtime after a refactor
- the client code checks `node.type === SomeComponent`

Typical symptom:
- source text is still present in `page.tsx`
- tests for static source may still pass
- but the rendered UI loses whole tab panels / cards / steps / labels because the client component no longer recognizes the child elements

## Root cause

Across a React Server Component -> Client Component boundary, relying on exact `node.type === SomeComponent` identity can be brittle. The child props may arrive, but exact component identity checks are not a safe discriminator for slot extraction.

This commonly breaks route-local authoring refactors where page.tsx starts composing a client component with structured child elements.

## Recommended fix

Do not detect slot children by exact component identity.

Instead, detect them by stable prop shape or explicit marker props.

Important practical rule from corp-web-japan AI Crew PR 219:
- when the server-authored route already has distinct semantic child roles like category/title/body, the most reliable fix is to add an explicit marker prop such as `slot="card-category"`, `slot="card-title"`, and `slot="card-body"`
- then parse children in the client component by `child.props.slot` rather than by `child.type === SomeSlotComponent`
- for repeatable child items such as tabs, use required prop-shape checks (`label`, `detailHref`, `videoHref`) instead of exact type identity
- this preserves route-local JSX authoring while surviving the RSC -> client boundary

Example replacement:

Bad:
```tsx
function isRoadmapTabElement(node: ReactNode): node is ReactElement<RoadmapTabProps> {
  return isValidElement(node) && node.type === RoadmapTab;
}
```

Better:
```tsx
function isRoadmapTabElement(node: ReactNode): node is ReactElement<RoadmapTabProps> {
  return (
    isValidElement(node) &&
    typeof node.props === "object" &&
    node.props !== null &&
    (node.props as { tabKey?: unknown }).tabKey !== undefined &&
    typeof (node.props as { label?: unknown }).label === "string"
  );
}
```

And similarly for nested step items:
```tsx
function isRoadmapStepElement(node: ReactNode): node is ReactElement<RoadmapStepProps> {
  return (
    isValidElement(node) &&
    typeof node.props === "object" &&
    node.props !== null &&
    typeof (node.props as { label?: unknown }).label === "string" &&
    (node.props as { title?: unknown }).title !== undefined
  );
}
```

## Workflow

1. Confirm the text still exists in the server-authored source file.
   - usually `src/app/page.tsx` or another server route/component
2. Inspect the client component receiving those children.
3. Search for child extraction logic using:
   - `Children.toArray(...)`
   - `filter(...)`
   - `node.type ===`
4. If exact type checks are used, treat that as the primary suspect.
5. Replace exact type checks with prop-shape checks or explicit marker props.
6. Re-run the relevant tests.
7. Add a regression test that forbids reintroducing exact `node.type === SlotComponent` checks in that component, when practical.

## Good discriminator choices

Prefer:
- required semantic prop names like `tabKey`, `label`, `title`, `variant`, `slot`
- explicit marker props such as `slot="roadmap-tab"`
- combinations of props that uniquely identify the slot type

Avoid:
- `node.type === SomeComponent`
- brittle displayName assumptions unless there is no safer option

## Regression-test idea

For static-structure test suites, add a check that the extracted component source does not reintroduce exact type-identity filtering.

Example:
```js
assert.doesNotMatch(componentSource, /node\.type === RoadmapTab|node\.type === RoadmapStep/);
```

## Important follow-up: static test inputs may also need to change

In route-local authoring refactors, fixing the runtime bug is often not enough.

A second failure mode is that tests still read only one legacy source file such as:
- `src/content/top-page.ts`
- `src/components/sections/top-page-sections.tsx`

After route-local decomposition, the relevant authored strings may now live across:
- `src/app/page.tsx`
- one or more section-local component files
- the remaining content file for shared constants

This means tests can fail even though the UI is correct, simply because the test is reading the wrong file.

### What to do

1. Identify where the text or attributes now actually live.
2. If the page now mixes route-local JSX and section-local components, build the assertion source from multiple files.
3. Prefer concatenating source strings rather than forcing all expectations into one legacy file.
4. Update tests to accept both:
   - legacy data-object patterns
   - route-local JSX/component-call patterns

Example pattern:
```js
const page = readSource("src/app/page.tsx");
const section = readSource("src/components/sections/top-page-security-section.tsx");
const source = `${getTopPageStructureSource()}\n${section}\n${page}`;

assert.match(source, /target="_blank"/);
assert.match(source, /rel="noopener noreferrer"/);
```

For CTA/data assertions, also consider combining content and page source:
```js
const source = `${topPageDataSource}\n${topPage}`;
assert.match(source, /primaryCta: ...|<HeroPrimaryAction ...>/);
```

For fully route-local final states, a repo helper like `getTopPageStructureSource()` may need to aggregate multiple section files instead of falling back to only one old container file.

## When this skill is especially relevant

- route-local authoring refactors in Next.js App Router
- converting static data objects into direct JSX composition
- tabbed panels, step lists, card groups, or other slot-based UI APIs authored in server files and consumed by client components

## Verification

Minimum:
- targeted test covering the affected structure
- repo baseline CI if the repo is small enough or the user asked for confidence

Strong signal the fix worked:
- authored strings that previously vanished are visible again in the rendered surface
- client component still supports both initial render and interaction state (for example tab switching)

## Important follow-up: restoring hidden slot content can expose visual regressions in nested controls

A practical lesson from the AI Crew use-case tabbed card:
- after replacing brittle `node.type === ...` checks with prop-shape or marker-prop detection, the missing body text came back correctly
- but the restored nested tab chips (`見積分析`, `見積書作成`) then rendered slightly taller than the stage reference because they inherited a larger line-height from the restored body wrapper context
- the correct runtime fix was not another slot-detection change, but an explicit button text line-height on the nested chip control

What to verify after the slot-content fix:
1. compare the affected nested interactive controls in the browser, not just the restored text blocks
2. inspect `getComputedStyle()` for
   - `line-height`
   - `padding-top` / `padding-bottom`
   - final element height
3. if stage/live and preview differ only because of inherited typography rhythm, set the control's own text metrics explicitly (for example `leading-[18px]` on a small 12px chip button)

Typical signal:
- the restored slot content is correct, but small pills/tabs/buttons inside that content become 2–4 px taller than the reference while padding values stayed the same
- this usually means inherited line-height changed, not padding
