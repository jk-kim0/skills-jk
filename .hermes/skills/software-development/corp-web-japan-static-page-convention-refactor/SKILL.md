---
name: corp-web-japan-static-page-convention-refactor
description: Refactor corp-web-japan static marketing pages so page.tsx becomes the primary readable implementation surface, while keeping only small reusable or interactive helpers extracted.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, nextjs, static-pages, code-location-conventions, refactor]
    related_skills: [corp-web-japan-origin-main-worktree-safety]
---

# corp-web-japan static-page convention refactor

Use this when cleaning up static marketing pages in `corp-web-japan` to match `docs/code-location-conventions.md` section 1.

## Goal

Make the route file itself the primary readable implementation surface:
- `src/app/<route>/page.tsx` should show the main copy, section order, and page-specific JSX
- reduce dependence on page-specific wrapper components under `src/components/sections/**`
- reduce dependence on page-specific content registries under `src/content/**`
- keep only truly reusable primitives or small interactive helpers extracted

## When this applies

Typical targets:
- top page
- solution landing pages like AI Crew / AI Dashi
- other mostly static marketing pages with little or no data fetching

Do NOT apply this pattern to:
- publication/detail/list routes that should stay thin
- feature routes whose implementation belongs in `src/lib/**` + shared sections
- CMS or data-backed pages unless the user explicitly asks

## Baseline workflow

1. Start from latest `origin/main` in a fresh worktree.
2. Read:
   - `README.md`
   - `docs/code-location-conventions.md`
   - the current `page.tsx`
   - the extracted section component
   - the page-specific content module
3. Compare with an in-repo aligned example such as `src/app/solutions/ai-dashi/page.tsx`.
4. Move the main copy, constants, section order, and page-specific JSX into `page.tsx`.
5. Keep extracted only:
   - reusable shared components already used elsewhere
   - tiny interactive/client-only sections that would otherwise force the whole page to become a client component
6. Re-run type checking.

## Preferred extraction rule

Ask: “If I open only `page.tsx`, can I understand the page quickly?”

If no, pull more structure back into the route.

Good to keep extracted:
- `RevealOnScroll`
- shared showcases already used across pages
- a small client component for isolated interactivity, e.g. a tabbed roadmap section

Bad to keep extracted:
- a giant page-specific `<SomethingSections />` wrapper that hides most of the route
- a large `src/content/<page>.ts` object whose main job is to store the page’s marketing copy and section composition

## Practical pattern used successfully

### Recommended staged approach for static marketing pages

When the user wants a cleaner route-level static page but also wants reusable section/UI extraction first, prefer this order:

1. Primitive-extraction PR first
   - stay on latest `origin/main`
   - keep the route thin for now
   - identify repeated section-level patterns such as:
     - intro/header blocks
     - pills / badges
     - elevated bordered surfaces
     - icon frames
     - repeated CTA button treatments
   - extract those into small reusable components under `src/components/sections/**`
   - if a giant content object exists, begin decomposing it into section-level exports instead of one monolithic registry
   - do not move the full page implementation into `src/app/.../page.tsx` yet in this PR

2. Route-localization PR second
   - start again from the latest `origin/main` after the primitive PR merges
   - move the static page implementation into `src/app/<route>/page.tsx`
   - reuse the already-extracted primitives so the route mostly reads like:
     - `<SectionPrimitive>`
     - `<h2>マーケティング文句</h2>`
     - `<p>説明文</p>`
   - keep only small interactive/client helpers extracted, e.g. a roadmap tab section

This staged approach is especially useful when the current page has both:
- repeated styling patterns worth extracting
- a giant page-specific content object that should eventually be dismantled

### Important latest-main discipline for staged refactors

In fast-moving repos, do not keep executing a long static-page refactor plan against a worktree if `origin/main` advanced materially while you were preparing or partially editing a previous attempt.

If a prerequisite PR merged and advanced `origin/main`:
- stop
- fetch latest main again
- create a fresh worktree from the new tip
- re-read the now-current files
- then continue the next stage from that new baseline

Do not assume an earlier fresh worktree is still fresh enough after upstream movement.

### For server route pages

If the page is mostly static and currently imports:
- `page-specific sections component`
- `page-specific content module`

then refactor to:
- import shared layout components in `page.tsx`
- prefer putting section copy close to the JSX that renders it
- define a local `function <Page>Sections()` inside `page.tsx` for the page body if that improves readability
- render that local function from the default export page component

This keeps `page.tsx` readable without forcing everything into one giant JSX return.

### Naming extracted UX-semantic components

When extracting top-page-specific UX-semantic components, prefer names that describe the user-facing choice being presented rather than lower-level implementation structure.

Practical example from top-page solution cards:
- prefer `SolutionChoice*`
- avoid longer or less direct names like `TopPageSolutionPath*`

Good examples:
- `SolutionChoiceCard`
- `SolutionChoiceHeader`
- `SolutionChoiceBadge`
- `SolutionChoiceTitle`
- `SolutionChoiceSubtitle`
- `SolutionChoiceDescription`
- `SolutionChoiceAction`

Why:
- the file path already gives top-page context, so repeating `TopPage` in every exported symbol adds noise
- `Choice` reads more clearly than `Path` for a landing-page UI where the user is choosing between alternatives
- shorter UX-semantic names make `page.tsx` read more like content structure and less like implementation plumbing

Important nuance learned from PR follow-up:
- Do **not** merely replace `src/content/<page>.ts` with a giant top-level `const pageContent = { ... }` inside `page.tsx` and consider the job done.
- That still leaves markup and Japanese marketing copy logically separated, just in a different file location.
- The better direction is:
  - inline the most important page copy directly in JSX where practical, or
  - at minimum, move page-specific content objects down into the local page/body function scope so the structure and copy are read together in one implementation surface.
- If a reviewer/user says the route still feels like `markup + content registry`, treat that as valid feedback and keep collapsing the distance between copy and JSX.

### For isolated client interactivity

If only one subsection needs `useState` / client behavior:
- keep `page.tsx` as a server component
- extract only that subsection into a tiny dedicated client component
- pass the minimum data in as props

This worked well for the top page roadmap tab section.

Important App Router build pitfall learned from follow-up refactors:
- if an extracted helper uses React client-only APIs such as `createContext`, `useContext`, `useState`, `useEffect`, or other client hooks, mark that extracted file with `"use client"`
- do not assume that because the parent page is mostly static, Next/Turbopack will tolerate `createContext` in an unmarked component imported by `page.tsx`
- a typical failure looks like:
  - `You're importing a module that depends on createContext into a React Server Component module`
- practical example: `SolutionChoiceCard` used `createContext/useContext`, so the component file itself needed `"use client"` after being imported from `src/app/page.tsx`

## Cautions from experience

- Do not try to mechanically auto-merge section/content files into page files without checking multiline imports and local helper constants; broken imports are easy to introduce.
- When copying from a large section component, ensure these local definitions are preserved if still referenced:
  - icon arrays
  - theme/style constant objects
  - small text rendering helpers
  - `isExternalHref` style helpers
- If you extract one small interactive subsection, also remove the old inlined client-only state logic from the server page.
- Prefer direct `Link` usage over click-wrapper + `router.push` when the card can simply be a link.
- Most important practical cleanup rule learned from PR follow-up: if content truly moved into `page.tsx`, delete or stop using the old page-specific source files as part of the same change. Otherwise the refactor is only a copy, not a move.
- After moving static-page content into route files, explicitly search for leftover imports/usages of the old modules such as:
  - `src/components/sections/<page>-sections.tsx`
  - `src/content/<page>.ts`
- Typical residual consumers may be adjacent support surfaces like `not-found.tsx`, floating guides, or tests that still import old CTA constants.
- After the move, either inline those remaining small constants locally where used, or re-home them into a still-valid shared module. Do not leave dead page-content files around just because one small helper still imports them.
- Update structure/assertion tests in the same batch. Repository tests may explicitly read old files by path, so deleting the obsolete files without updating tests can fail CI even when runtime code is correct.

## Strongly recommended two-PR test strategy

When the repository already contains structure tests that read exact source files such as:
- `src/content/top-page.ts`
- `src/content/home.ts`
- `src/components/sections/top-page-sections.tsx`
- `src/components/sections/home-page-sections.tsx`

prefer this order:

1. Test-only PR first
   - change only tests/helpers
   - make tests validate the same user-facing content/CTA/structure invariants whether the implementation still lives in old content/section files or has already moved into route files
   - do not change production code in this PR
2. Refactor PR second
   - move/delete the old content and section files
   - keep the already-generalized tests green

Why:
- If you refactor runtime code and test expectations in the same PR, it becomes harder to prove behavior equivalence.
- A separate test-only PR preserves a cleaner signal: the tests become location-agnostic first, then the implementation is free to move.

### Practical helper pattern for compatibility tests

A reusable pattern is to extend test helpers with functions like:

```js
export function sourceExists(relativePath) { ... }
export function readFirstExistingSource(relativePaths) { ... }
```

Then assertions can prefer old canonical paths first and fall back to new route-local paths:

```js
const topPageDataSource = readFirstExistingSource([
  "src/content/top-page.ts",
  "src/app/page.tsx",
]);
```

Use this for tests that should verify equivalence of:
- CTA targets
- section markers / anchor ids
- required copy fragments
- security / download / contact route wiring
- route-level readability invariants

Important nuance:
- These tests should validate stable semantics, not one exact implementation location.
- Only assert exact file-path absence/presence when the specific PR goal is cleanup of dead source files.
- For transition-safe tests, prefer “old OR new location contains the invariant” instead of “must exist only here.”

## Verification

Minimum verification for this refactor class:

```bash
npm run typecheck
```

If the user explicitly wants more verification or the change affects broader rendering risk, then also run:

```bash
npm run test:ci
npm run build
```

But for this user, prefer the lightest meaningful verification first.

## Done criteria

- `page.tsx` is the primary readable implementation surface
- page-specific content registry dependence is reduced or removed
- giant page-specific wrapper dependence is reduced or removed
- only small reusable/shared or isolated interactive helpers remain extracted
- `npm run typecheck` passes
