---
name: semantic-strong-emphasis-for-marketing-copy
description: Replace long inline highlight span classnames in static marketing copy with semantic strong tags while keeping visual emphasis in the wrapper component.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Semantic `<strong>` emphasis for marketing copy

Use this when a static marketing page has route-authored copy like:
- `<span className="bg-gradient-to-r ... text-transparent">highlighted copy</span>`
- repeated inline emphasis spans that make `page.tsx` noisy

## Goal

Keep the route file readable and semantic:
- `page.tsx` should author emphasis as `<strong>...</strong>`
- section/component files should own the styling details for emphasized descendants
- avoid long presentation-heavy class strings inside route-level copy when a semantic emphasis tag is enough

## Preferred pattern

1. In the route-authored JSX, replace the long inline span with plain semantic markup:

```tsx
<strong>圧倒的な導入スピード</strong>
```

2. In the section wrapper component, style descendant `strong` elements with selector-based classes, for example:

```tsx
<h2 className="... [&_strong]:bg-gradient-to-r [&_strong]:from-[#E45A2A] [&_strong]:via-[#ED602E] [&_strong]:to-[#F08A3C] [&_strong]:bg-clip-text [&_strong]:font-inherit [&_strong]:text-transparent">
  {children}
</h2>
```

3. Keep the route copy explicit. Do not reintroduce string matching or prop-shaped highlight APIs just to style one phrase.

## When this is a good fit

- route-local authoring refactors for static marketing pages
- reviewer/user feedback that a span classname is too long or noisy
- a section already has a dedicated wrapper component under `src/components/sections/**`
- the emphasized phrase is authored directly in page copy and does not need independent behavior

## When not to use it

- emphasis needs different styles per occurrence inside the same wrapper and descendant `strong` styling would be too broad
- the emphasized element needs interaction, icons, or layout behavior beyond simple text emphasis
- copy is not route-authored and the current owner is intentionally a shared UI primitive

## Verification

- confirm `page.tsx` now uses `<strong>...</strong>` for the targeted phrase
- confirm the visual styling moved to the wrapper component, not to a new long inline class string elsewhere
- if there is a structure/source test, scope it narrowly to the intended phrase or section; do not fail on unrelated gradient spans elsewhere on the page

## Practical pitfall

If you add a regression test, do not assert that the whole page contains no gradient spans at all. Large marketing pages often still have other intentional gradient text. Scope the assertion to the specific phrase or section being refactored.
