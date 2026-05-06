---
name: corp-web-japan-generic-cta-primitive-extraction
description: Extract CTA layout primitives from a feature-specific section file into a reusable generic CTA section module in corp-web-japan, then update callsites and split the refactor into its own PR.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, cta, refactor, shared-components, worktree, github]
---

# corp-web-japan generic CTA primitive extraction

Use this when a CTA section currently lives inside a feature- or page-specific section file, but the user wants it generalized into reusable shared primitives and reviewed in a separate PR.

## When to use

Use this when:
- a component name like `ResourceListCtaSection` is misleading because the CTA is not actually resource-list-specific
- the same CTA layout pattern is likely to be reused by multiple pages
- the user explicitly asks for a separate refactor PR instead of bundling the rename/extraction into the feature PR
- the current CTA primitives are layout primitives, not content-specific business logic

## Core goal

Turn feature-specific CTA primitives into a neutral shared module while keeping:
- the existing visual output unchanged
- the feature/page route copy unchanged
- the original feature-specific file focused on its real domain concerns

Typical desired outcome:
- new shared file like `src/components/sections/cta-section.tsx`
- generalized names like `CtaSection`, `CtaContent`, `CtaCopy`, `CtaTitle`, `CtaDescription`, `CtaActions`
- existing route/page imports updated to the generic module
- old feature-specific CTA exports removed from the original file
- a separate PR dedicated only to the naming/extraction refactor

## Workflow

1. Start from latest `origin/main` in a fresh worktree.
2. Identify all feature-specific CTA exports and every current usage.
3. Decide whether the existing CTA button primitive is already generic enough.
   - If yes, keep it.
   - If not, extract/rename that too.
4. Create a new shared CTA module under `src/components/sections/`.
5. Move the CTA layout primitives there with generalized names.
6. Update the existing caller(s) to import from the new file.
7. Remove the old CTA exports from the feature-specific file.
8. Add or update a structure-oriented test that proves:
   - the caller imports the generic CTA module
   - the old feature-specific CTA export names are gone
9. Run `npm run test:ci` and `npm run build`.
10. Commit, push, create a separate PR, and wait for CI to finish.

## Naming guidance

Prefer names that describe reusable page-section structure rather than the current feature family.

Good examples:
- `CtaSection`
- `CtaContent`
- `CtaCopy`
- `CtaTitle`
- `CtaDescription`
- `CtaActions`
- `CtaButton` only if the button primitive truly belongs with this section module

Avoid names that unnecessarily tie the primitive to one feature area when the layout is generic:
- `ResourceListCtaSection`
- `DemoCtaSection`
- `AboutUsCtaSection`

## Practical heuristic for button ownership

If a button component is already generic and intentionally shared across the repo, do not rename or move it just because the section primitives moved.

Example:
- keep `BrandGradientCtaButton` where it is if it is already a shared UI primitive used by unrelated surfaces
- only extract/rename the layout shell around it

## Testing pattern

Prefer a structure-oriented test instead of only relying on runtime screenshots.

Example assertions:
- `src/app/internal/mdx-list-demo/page.tsx` imports from `@/components/sections/cta-section`
- `src/app/internal/mdx-list-demo/page.tsx` uses `<CtaSection>`
- `src/components/sections/resource-list-section.tsx` no longer contains `ResourceListCtaSection`
- `src/components/sections/cta-section.tsx` exports `CtaSection`, `CtaTitle`, and other intended primitives

This is especially useful when the refactor is mostly naming and file-boundary cleanup with little or no visual change.

## Separate-PR rule

If the user asks for a separate refactor PR:
- do not piggyback the extraction onto the existing feature/fix PR
- create a new latest-main branch just for the generic CTA cleanup
- keep the diff limited to extraction, renaming, callsite updates, and tests

## Pitfalls

- bundling the generic extraction into an unrelated visual/content PR
- renaming a truly shared button primitive unnecessarily
- leaving old feature-specific CTA names exported in the original file
- updating only one callsite when the old name still exists elsewhere
- skipping structure tests because the runtime output looks unchanged

## Verification

Required:
- `npm run test:ci`
- `npm run build`
- confirm PR CI passes after push

## Done criteria

You are done when:
- CTA primitives live in a dedicated generic shared module
- the original feature-specific section file no longer owns those CTA primitives
- current callsites use the new generic names
- structure tests reflect the new ownership
- the refactor is submitted as its own PR and CI is green
