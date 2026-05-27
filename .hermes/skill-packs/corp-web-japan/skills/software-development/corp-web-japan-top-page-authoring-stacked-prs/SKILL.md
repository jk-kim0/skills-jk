---
name: corp-web-japan-top-page-authoring-stacked-prs
description: Refactor corp-web-japan top page sections into direct page.tsx JSX authoring using small UI-only section components, delivered as section-scoped stacked PRs.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, nextjs, stacked-pr, page-authoring, refactor]
---

# corp-web-japan top page authoring via stacked PRs

Use this when refactoring `src/app/page.tsx` and top-page section components in `corp-web-japan` toward the user's preferred authoring model.

## Core intent

The target is not merely "move copy into page.tsx".

The real requirement is:
- `page.tsx` should read like the actual page manuscript
- marketing copy should be authored as direct JSX such as:
  - `<Component>marketing text</Component>`
- avoid large JSON-like objects and props blobs in `page.tsx`
- section component files should contain UI contracts only:
  - layout
  - className
  - spacing
  - animation
  - interaction logic
- page-level component names should match UX element names directly
  - prefer `SolutionOverviewSection` over `TopPageSolutionOverviewSection`

## Important user preference learned

Bad pattern:
- `const hero = { ... }`
- `const roadmap = { ... }`
- `<HeroSection hero={hero} />`
- `<RoadmapSection roadmap={roadmap} />`

Preferred pattern:
- `<HeroSection> ... actual copy ... </HeroSection>`
- `<RoadmapSection> ... actual copy ... </RoadmapSection>`
- page.tsx should expose the real title/body/CTA text inline

This applies even when the copy already lives in page.tsx. If it is still hidden inside a big object literal, it does **not** meet the user's intended method.

## When to split into stacked PRs

If the top page still uses a large wrapper like `TopPageSections` and multiple sections remain data-driven, do not force the whole rewrite into one PR.

Prefer stacked PRs, one section at a time, in this order:
1. hero authoring
2. core value authoring
3. roadmap authoring
4. platform requirements authoring
5. security authoring
6. whitepapers authoring
7. final CTA authoring + wrapper cleanup

Why this order worked well:
- early PRs establish the authoring pattern on simpler sections
- later PRs can stack on confirmed structure
- the final PR can safely remove now-obsolete wrapper/content plumbing

## Branch / PR strategy

Create each PR as a stacked PR based on the previous section branch, not all from main.

Example chain:
- `refactor/top-page-hero-authoring` -> base `main`
- `refactor/top-page-core-value-authoring` -> base `refactor/top-page-hero-authoring`
- `refactor/top-page-roadmap-authoring` -> base `refactor/top-page-core-value-authoring`
- ...and so on

Use fresh worktrees for each branch.

## Section refactor recipe

For each section:

1. Inspect the current `page.tsx`, `top-page-sections.tsx`, and `src/content/top-page.ts`.
2. Add or update a small section component file under `src/components/sections/`.
   - keep it UI-only
   - expose authoring-friendly JSX entry points
3. Move the section's marketing copy into `src/app/page.tsx` as direct JSX.
4. Remove the old content object for that section from `src/content/top-page.ts`.
5. Remove the old rendering block for that section from `top-page-sections.tsx`.
6. Update tests/helpers that assume `top-page-sections.tsx` or old content exports are still the main source.
7. Run:
   - `npm run lint`
   - `npm run typecheck`
   - `npm run build`
8. Commit, push, open/update the stacked PR.

## Testing helper update pattern

When the old wrapper is gradually removed, `tests/helpers/static-marketing-page-sources.mjs` must be updated.

Recommended approach:
- aggregate from `src/app/page.tsx` plus the current section component files
- do not assume `src/components/sections/top-page-sections.tsx` is always present
- `isTopPageSectionExternalized()` should check for the new section component files, not only the legacy wrapper

## Rebase / squash lessons for stacked PRs

When an earlier stacked PR merges into main, a later PR may still contain the older sibling commits in its branch history.

If the user asks to squash and rebase a later stacked PR onto latest main:
1. create a fresh worktree from the PR head branch
2. inspect `origin/main..HEAD`
3. if earlier sibling commits are already on main, use:
   - `git reset --soft origin/main`
4. verify the staged diff only contains the intended section's final net changes
5. create a single commit with the intended PR title
6. `git push --force-with-lease origin HEAD:<pr-branch>`

This worked well for a platform-requirements stacked PR after its earlier sibling PRs had already merged.

## Content highlight lesson

For roadmap step titles, the original content data already separated titles into:
- `before`
- `highlight`
- `after`

If a refactor starts rendering the highlight text with visible accent styling, that is usually restoring the original content intent rather than inventing a new emphasis. Preserve the original highlight target when converting from data-driven rendering to direct JSX.

## Completion criteria

A section refactor is done when:
- page.tsx shows the section's real marketing copy inline as JSX
- no large object blob in page.tsx is used to pass that section's copy as props
- the corresponding `src/content/top-page.ts` section data is removed
- section component files only hold UI contracts/interactions
- lint, typecheck, and build pass
