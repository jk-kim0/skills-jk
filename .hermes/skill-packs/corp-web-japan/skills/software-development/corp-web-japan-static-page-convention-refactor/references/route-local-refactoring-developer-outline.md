# Route-local refactoring developer outline

Use this support note when the task is to explain the route-local refactoring pattern to developers, reviewers, or AI-agent users.

## One-sentence definition

Route-local refactoring makes `src/app/**/page.tsx` the primary readable authoring surface for a static marketing page, while `src/components/sections/**` keeps only UI implementation details.

## What to emphasize

- It is not just "move files closer to routes".
- The real page copy, major section order, and CTA intent should be visible in the route file.
- Section files should own layout, styling, interaction, and reusable presentation primitives.
- Giant content registries, giant page-specific wrappers, and JSON-like data blobs are the main anti-patterns.

## Current repo examples

- `src/app/page.tsx`
  - top-page reference for route-owned hero copy, section order, and CTA intent
- `src/app/about-us/page.tsx`
  - company-intro reference for authoring repeated timeline/leader/location content directly in JSX
- `src/app/t/platforms/acp/page.tsx`
  - interactive-section reference that uses children-based composition instead of `categories=[...]` data blobs
- `src/app/t/privacy-policy/[slug]/page.tsx`
  - useful exception example: thin legal/document wrapper, not a static marketing-page target

## Suggested section order for a doc or presentation

1. introduction / problem statement
2. design principles and responsibility split
3. before/after examples from the repo
4. pros, cons, and expected effects
5. how to instruct an AI agent
6. which skill/docs/files to read next

## Useful AI-agent prompt shapes

### Whole-page prompt

Refactor `src/app/<route>/page.tsx` to follow route-local authoring. Keep the real copy and section composition in `page.tsx`, leave only UI implementation details in `src/components/sections/**`, remove large top-level data blobs if present, and do not change render order.

### Section-scoped prompt

Refactor only the `<section-name>` section into route-local authoring. Do not touch neighboring sections except for minimal support changes. Done means the section's real copy is directly visible in `page.tsx`.

### Interactive-section prompt

Replace the data-blob prop pattern with children-based route-local JSX authoring. Keep widget interaction in the section component, but move the real title/body copy into the route.

## Supporting docs to mention

- `docs/code-location-conventions.md`
- `docs/static-page-route-local-authoring.md`
- `.agents/skills/static-page-route-local-authoring/SKILL.md`
