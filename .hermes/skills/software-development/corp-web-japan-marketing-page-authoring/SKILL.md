---
name: corp-web-japan-marketing-page-authoring
description: Refactor corp-web-japan marketing pages so page.tsx owns user-facing copy and section components own only UI structure and styles.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, nextjs, marketing, page-authoring, component-design]
---

# corp-web-japan marketing page authoring

Use this for corp-web-japan marketing-route refactors when the user wants the route file to read like the actual page script.

## Core convention

- `page.tsx` owns all user-facing marketing copy.
- Section component files under `src/components/sections/` own only:
  - component definitions
  - layout structure
  - class names / styling
  - animation wrappers
  - reusable UI slots
- Do not leave hardcoded marketing text inside section component files.
- Do not hide rich marketing copy in `src/content/*.ts` when the user wants route-local authoring.

## Naming convention

In `page.tsx`, component names should match visible UX elements directly.

Prefer short names like:
- `SolutionOverviewSection`
- `SolutionOverviewIntro`
- `SolutionOverviewLead`
- `SolutionChoiceGroup`

Avoid long implementation-heavy names like:
- `TopPageSolutionOverviewSection`
- `TopPageSolutionChoiceHeading`

Reason: in the route file, the component tree should read like the page's UX structure, not internal implementation details.

## Recommended refactor steps

1. Identify the marketing section whose copy should move into `page.tsx`.
2. Extract or keep only thin section wrappers in `src/components/sections/...`.
   - wrappers should prefer `children`-based composition over prop-shaped copy APIs
   - wrappers should contain no actual marketing sentences
   - avoid `title={...}` style APIs when the user wants `page.tsx` to read like the actual page script
   - avoid introducing thin `*PageContent` wrappers whose only job is to alias a direct `div.mx-auto.max-w-[1200px]` container; prefer the direct route-local or section-local container unless the wrapper has a clearly separate responsibility such as reused inner-width semantics across multiple distinct blocks
3. Move all visible copy into `page.tsx`.
   - headings
   - lead paragraphs
   - emphasized inline spans/strong text
   - card titles, subtitles, descriptions, CTA labels
4. When a section title or intro becomes visually complex, create explicit authoring components instead of packing JSX into a prop.
   - good: `SolutionOverviewTitle`, `SolutionOverviewLeadGroup`, `SolutionOverviewLead`
   - avoid: `SolutionOverviewIntro title={<><span>...</span></>}`
5. Avoid replacing one hidden copy container with another.
   - Do not move marketing copy out of `src/content/*.ts` only to reassemble it as large JSON-like constants or arrays at the top of `page.tsx`.
   - The route file should read as direct JSX authoring, e.g. `<HeroTitle>...</HeroTitle>` and `<HeroBody>...</HeroBody>`, not as `const hero = { title: ..., body: ... }` fed back into props.
   - Small URL constants are fine; large copy/data objects are not the intended outcome when the user asks for PR-145-style authoring.
6. Rename section helpers to short UX names before importing them into `page.tsx`.
7. Remove now-unused content exports from `src/content/*.ts` if the moved copy no longer belongs there.
8. If a large existing orchestrator component remains, let it accept `children` so the route can inject the route-local section without duplicating the rest of the page.
9. If the whole page is too large to refactor safely in one PR, split the work into section-scoped stacked PRs from latest `origin/main`.
   - good split order for top-page work: hero -> core value -> roadmap -> platform requirements -> security -> whitepapers -> final CTA / wrapper cleanup
   - in practice, make them as stacked PRs where each new branch bases on the immediately previous PR branch, not directly on `main`
   - proven branch chain from this repo:
     - `refactor/top-page-hero-authoring` -> base `main`
     - `refactor/top-page-core-value-authoring` -> base hero branch
     - `refactor/top-page-roadmap-authoring` -> base core value branch
     - `refactor/top-page-platform-requirements-authoring` -> base roadmap branch
     - `refactor/top-page-security-authoring` -> base platform requirements branch
     - `refactor/top-page-whitepapers-authoring` -> base security branch
     - `refactor/top-page-final-cta-authoring` -> base whitepapers branch
   - each PR should preserve the same rule: direct JSX marketing copy in `page.tsx`, UI-only section primitives in component files
   - the final CTA / wrapper cleanup PR is the right place to remove the now-obsolete `TopPageSections` wrapper entirely after all earlier sections have already migrated

10. When the wrapper is finally removed, update the top-page structure test helper to read the new section component files directly.
   - replace helper logic that assumes `src/components/sections/top-page-sections.tsx` still exists
   - aggregate current sources like:
     - `src/app/page.tsx`
     - `src/components/sections/top-page-hero-section.tsx`
     - `src/components/sections/top-page-core-value-section.tsx`
     - `src/components/sections/top-page-roadmap-section.tsx`
     - `src/components/sections/top-page-platform-requirements-section.tsx`
     - `src/components/sections/top-page-security-section.tsx`
     - `src/components/sections/top-page-whitepapers-section.tsx`
     - `src/components/sections/top-page-final-cta-section.tsx`
     - solution-overview / solution-choice section files
   - without this helper update, the final cleanup PR can pass visually while string-based structure tests still point at deleted wrapper files

## Practical pattern used on PR #145

When `TopPageSections` still owned most of the top page, the solution overview was made route-authored without rewriting the whole page:

- keep `TopPageSections` as the main shell
- add `children?: ReactNode` to `TopPageSections`
- render `{children}` at the exact section insertion point
- define the solution overview section directly in `src/app/page.tsx`

This is a good incremental step when the user wants route-local copy now, but a full page decomposition is not part of the current PR.

## Public form page variation

The same route-authoring rule also applies when the page contains a large interactive form.

Example pattern from `src/app/contact-us/page.tsx`:
- keep query-prefill resolution and metadata in the route file
- move the page-level intro copy into the route file
  - page title
  - lead paragraph
  - short checklist / expectation bullets
- keep the form component focused on:
  - field rendering
  - validation states
  - submit success/error states
  - submission wiring
- add a thin section primitive file, e.g. `contact-us-page-section.tsx`, that owns only layout/styling wrappers such as:
  - `ContactUsSection`
  - `ContactUsIntro`
  - `ContactUsTitle`
  - `ContactUsLead`
  - `ContactUsChecklist`
  - `ContactUsFormPanel`

This keeps the route readable like authored page content without forcing the form internals themselves into `page.tsx`.

## Regression-test adjustment for route-authoring moves

When moving visible copy from a component into `page.tsx`, update existing string-based tests accordingly.

Recommended assertions after the move:
- route file contains the moved page-level copy
- route file still renders the expected form/component wiring
- form component still contains submit wiring and accessibility attributes
- form component no longer hardcodes the moved intro copy

Do not leave old tests asserting that page-level intro strings still live inside the form/component file after the authoring split.

### Important source-reader pitfall

In corp-web-japan, some test helpers prefer externalized sources first, for example:
- `src/content/top-page.ts`
- then `src/app/page.tsx`

This means a test like `getTopPageDataSource()` can keep reading `src/content/top-page.ts` even after a hero CTA label/button moved into route-local JSX in `page.tsx`.

Practical fix from PR #150:
- if the assertion is about route-local hero authoring, do not check only the helper-returned data source
- instead assert against a combined input such as ```${topPageDataSource}\n${topPage}``` or otherwise read both files explicitly
- keep content-object assertions for values that still legitimately live in `src/content/*.ts`
- use route-file assertions for JSX-authored controls like `<HeroPrimaryAction ...>` / `<HeroSecondaryAction ...>`

This avoids false CI failures where the implementation is correct but the test is still looking only at the old preferred source file.

## Good outcome checklist

- Opening `page.tsx` shows the actual page narrative directly.
- Opening the section component file shows no marketing copy, only UI structure.
- Component names in `page.tsx` read like UX blocks.
- Removed content exports are not left stale in `src/content/*.ts`.
- Typecheck passes after the move.
- `npm run build` also passes, not just typecheck.

## Next.js App Router boundary rules

When route-local authoring moves markup from a client orchestrator into `src/app/page.tsx`, re-check server/client boundaries immediately.

- `page.tsx` is a Server Component by default.
- If a child section/card component uses `createContext`, `useContext`, `useState`, or event handlers, that file must be marked with `"use client"`.
- Do not pass component functions, icon constructors, or other non-serializable function props from `page.tsx` into Client Components.
- If a Client Component needs to choose an icon or other implementation detail, prefer choosing it internally from context or a serializable string/tone prop.

Practical finding from PR #145:
- Moving solution-overview card composition into `page.tsx` exposed `top-page-solution-choice-card.tsx` directly to the Server Component boundary.
- The card file needed `"use client"` because it used React context.
- Passing `Users` / `Blocks` icon functions from `page.tsx` into a Client Component caused a prerender/build failure.
- The stable fix was to restore icon selection inside the client card header based on `tone`, rather than passing icon functions from the server route.

## Pitfalls

- Do not keep part of the same section's copy in `page.tsx` and part in a section component file.
- Do not keep redundant old content objects like `topPageSolutionBranch` after migrating the section to route-local copy.
- Do not use verbose `TopPage...` prefixes in route-level authoring when the shorter UX name is unambiguous.
