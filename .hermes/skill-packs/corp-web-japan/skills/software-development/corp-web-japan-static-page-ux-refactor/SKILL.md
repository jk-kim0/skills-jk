---
name: corp-web-japan-static-page-ux-refactor
description: Refactor corp-web-japan static marketing pages so route files become readable implementation surfaces by first extracting UX-semantic components, then moving copy/structure into page.tsx without leaving duplicate content registries behind.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, static-pages, nextjs, refactor, ux-components, worktree, github-pr]
    related_skills: [corp-web-japan-origin-main-worktree-safety, existing-pr-followup-worktree, github-pr-workflow]
---

# corp-web-japan static page UX refactor

Use this when refactoring static marketing pages in `corp-web-japan`, especially the top page and solution landing pages, where the user wants route files to be the primary readable implementation surface.

## When to use

Use this workflow when the user asks for any of the following:
- make `src/app/.../page.tsx` the main readable implementation surface
- reduce or remove dependence on `src/content/**` registries or page-specific `components/sections/*-sections.tsx`
- extract repeated section box / heading / CTA / card UI before moving markup into the route
- eliminate style/theme JSON config objects like `solutionBranchThemes`
- make page code read like direct page authoring with JSX and nearby copy

## Core user preference to respect

The user does **not** want static marketing pages to end up as:
- giant content JSON objects in `src/content/**`
- the same giant content JSON moved unchanged into `page.tsx`
- route files that only delegate to a page-specific wrapper component
- style/theme registries in page files when a UX-semantic component can represent the pattern better

The preferred end state is:
- reusable UX-semantic components first
- then page-local readable composition
- page copy visible close to the JSX that renders it
- route-local explicitness over hidden indirection

## Recommended sequence

### 0. Always start from latest main

In this repo, this is mandatory.

```bash
git fetch origin --prune
git rev-parse origin/main
git log --oneline --decorate -n 10 origin/main
```

Create a fresh worktree for new independent work.

```bash
git worktree add .worktrees/<flat-name> -b <branch-name> origin/main
```

For follow-up changes on an open PR, use a fresh worktree on the **existing PR branch**, not a new PR branch.

### 1. If tests are structure-dependent, split or harden them first

Before changing implementation structure, inspect tests for direct file-path assumptions like:
- `src/content/top-page.ts`
- `src/components/sections/top-page-sections.tsx`
- `src/content/home.ts`
- `src/components/sections/home-page-sections.tsx`

If the refactor will move or delete these files, first create or update a **separate test-only PR** so tests can validate both pre-refactor and post-refactor layouts.

Preferred helper pattern:
- add `tests/helpers/static-marketing-page-sources.mjs`
- expose helpers such as:
  - `getTopPageDataSource()`
  - `getTopPageStructureSource()`
  - `getAiCrewDataSource()`
  - `getAiCrewStructureSource()`
  - `isTopPageContentExternalized()`
  - `isTopPageSectionExternalized()`

Also prefer page-specific tests over one mixed structure test:
- `tests/top-page-structure.test.mjs`
- `tests/ai-crew-page-structure.test.mjs`

This keeps later implementation PRs focused on code, not test survival.

### 2. Derive repeated UX patterns before moving route code

Read the current section implementation and identify repeated patterns such as:
- section intros: eyebrow + title + body
- rounded pills / labels / tags
- bordered/elevated surface cards
- icon frames
- CTA button rows
- repeated marketing cards (for example AI Crew vs AI Dashi choice cards)

Do **not** start by moving huge content objects into the route.

Instead, first extract shared or top-page-specific UX primitives under `src/components/sections/**`.

### 3. Prefer UX-semantic components over style JSON registries

If you see structures like:
- `solutionBranchThemes`
- `*CardThemes`
- arrays of className presets used to skin the same JSX structure

prefer extracting a top-page-specific component with UX meaning.

Bad intermediate pattern:
```ts
const solutionBranchThemes = [
  { badgeClass: "...", cardClass: "...", ... },
  { badgeClass: "...", cardClass: "...", ... },
] as const;
```

Preferred direction:
- `TopPageSolutionPathCard`
- `TopPageSolutionPathHeader`
- `TopPageSolutionPathBadge`
- `TopPageSolutionPathTitle`
- `TopPageSolutionPathSubtitle`
- `TopPageSolutionPathDescription`
- `TopPageSolutionPathAction`

Then page code can read like:
```tsx
<TopPageSolutionPathCard href="/solutions/ai-crew" tone="crew">
  <TopPageSolutionPathHeader icon={Users}>
    <TopPageSolutionPathBadge>AI Crew</TopPageSolutionPathBadge>
  </TopPageSolutionPathHeader>
  <TopPageSolutionPathTitle>...</TopPageSolutionPathTitle>
  <TopPageSolutionPathSubtitle>...</TopPageSolutionPathSubtitle>
  <TopPageSolutionPathDescription>...</TopPageSolutionPathDescription>
  <TopPageSolutionPathAction>...</TopPageSolutionPathAction>
</TopPageSolutionPathCard>
```

This is closer to the user’s requested authoring style than a theme JSON.

### 4. Use reusable generic primitives sparingly but deliberately

Good reusable generic primitives extracted during the top-page-first refactor included:
- `MarketingPill`
- `MarketingIconFrame`
- `MarketingSurface`
- `MarketingSectionIntro`

These work well when multiple sections repeat the same box/intro idioms.

Implementation notes:
- use `cn()` from `@/lib/utils`
- allow `as` polymorphism on surfaces if you need `div`, `article`, or `Link`
- allow eyebrow/title/body slots on intro containers
- keep these components focused on UX meaning, not arbitrary style dumping

### 5. After primitives exist, move the route implementation into `page.tsx`

Only after the repeated UX patterns are extracted should you move the static page implementation into the route.

For top page work:
- move the main JSX from `src/components/sections/top-page-sections.tsx` into `src/app/page.tsx`
- keep only truly necessary extracted helpers, for example an interactive roadmap tabs block like `top-page-roadmap-section.tsx`
- keep page-local constants near the route if they are still needed

### 6. Dismantle giant content objects in phases

A good phased path is:
1. split `topPageContent` into section-level exports
2. move page structure into `src/app/page.tsx`
3. remove obsolete wrapper component
4. remove unused duplicated content sections from `src/content/top-page.ts`
5. where possible, replace content-data-driven repeated cards with direct page JSX using the extracted UX components

Important lesson:
- moving `topPageContent` unchanged from `src/content/top-page.ts` into `page.tsx` is **not enough**
- that still leaves markup and copy conceptually separated
- the user expects the route to become readable, not merely self-contained

### 7. Remove duplicates fully

If content was moved to the route, remove or shrink the old source of truth.

Do **not** leave the same marketing content both in:
- `src/app/page.tsx`
- and `src/content/top-page.ts`
- or in a now-unused `top-page-sections.tsx`

Also clean up remaining imports in other files, for example:
- `src/app/not-found.tsx`
- any floating guide component still importing old content constants

### 8. Update tests after implementation changes, but preserve behavioral equivalence

If the implementation PR must update tests, keep the test changes minimal and aligned with the test-only compatibility layer already introduced.

Prefer:
- helper-based source discovery
- page-specific tests
- assertions on behavior / content / route readability

Avoid:
- rewriting tests so broadly that equivalence becomes unclear
- deleting structural assertions without replacing them with a better route-level assertion

### 9. PR discipline

- New independent refactor step -> new worktree, new branch, new PR
- Follow-up on existing open PR -> fresh worktree on same PR branch
- Write PR body with `--body-file`
- Only use `Closes` / `Fixes` when the PR fully resolves the issue
- Otherwise use `Related to #N`

## Verification

At minimum for implementation PRs in this repo:

```bash
npm run typecheck
npm run test:ci
```

Rely on CI as the primary verification path after push.

## Practical patterns that worked

### A. Top-page-first route migration
- extract generic primitives first
- optionally split content into section-level exports
- move JSX into `src/app/page.tsx`
- keep roadmap as a separate client helper if interactive state remains
- delete `src/components/sections/top-page-sections.tsx` once no longer needed

### B. Top-page solution choice cards without theme JSON
Use a top-page-specific compound component instead of `solutionBranchThemes`.
This makes the route read closer to authored page markup and removes config indirection.

### C. Keep truly shared data only when still useful
For example:
- metadata and stable URLs may remain exported from `src/content/top-page.ts`
- but duplicated card copy that is now directly authored in `page.tsx` should be removed from the content module

## Anti-patterns to avoid

- giant `topPageContent` object copied wholesale into `page.tsx`
- keeping both route-local copy and old content source in parallel
- theme/style JSON registries where a UX-semantic component should exist
- one generic wrapper component that hides the whole static page structure
- changing tests in the same PR without preserving clear equivalence, when a test-only preparation PR should come first

## Done criteria

- repeated UX box/heading/card patterns are represented by reusable semantic components
- page-level markup is readable in `src/app/page.tsx`
- the route no longer depends on a page-specific wrapper section component for the top page
- duplicate content sources are removed or reduced to only still-useful shared constants/section exports
- tests still verify the intended behavior and route readability
- `npm run typecheck` and `npm run test:ci` pass
