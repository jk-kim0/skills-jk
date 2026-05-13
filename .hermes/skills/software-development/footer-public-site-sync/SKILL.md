---
name: footer-public-site-sync
description: Sync the repo footer with the live public site footer, verify locale/legal/address copy, add regression tests, and ship via PR.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [footer, localization, copy, verification, pull-requests]
    related_skills: [github-pr-workflow, github-code-review]
---

# Footer Public-Site Sync

Use this skill when the user asks to update the repo footer to match the live public site footer, including copyright year, office addresses, legal labels, and locale-specific copy.

## When to use
- Footer copy needs to match the public website
- Office/address/legal text may have changed upstream
- The change should be verified against the live site before editing

## Workflow

1. Inspect the live or reported footer behavior in the browser
   - Open the exact page the user reported, not just the home page
   - Check footer text, layout, and computed sizing in the browser
   - If the site has locale-specific variants, inspect `/en`, `/ko`, and `/ja`
   - For mobile layout bugs, emulate the reported device width first

2. Compare against repo sources
   - `src/components/layout/Footer.tsx` or repo-specific footer component path
   - footer CSS/module file
   - shared navigation/legal/footer constants
   - any locale copy helpers used by the shell/footer

3. For mobile right-side blank space or horizontal scrolling, identify the true overflow source before editing
   - Measure `document.documentElement.scrollWidth` vs viewport width
   - Enumerate overflowing footer descendants rather than assuming the route body is at fault
   - Inspect computed `display`, `gridTemplateColumns`, `gap`, `whiteSpace`, and per-link widths
   - Prefer structural fixes over masking with `overflow-x: hidden`
   - A reusable probe is documented in `references/mobile-footer-overflow-and-mixed-columns.md`

4. Update the footer source of truth
   - Keep the footer component and navigation/legal mapping in sync
   - Prefer updating shared constants over hardcoding duplicates
   - If the public site uses a different English legal label, align the mapping everywhere the label is surfaced
   - Update copyright year when needed
   - For mobile footer menus, keep the section stack itself single-column if needed for safe width, and vary the link-list layout per section instead of forcing one global rule
   - If long localized labels exist, keep those sections in a single-column mobile list; use two-column mobile grids only for shorter sections that fit safely
   - If a compact two-column list is mobile-only, explicitly reset it back to the normal single-column vertical list at tablet/desktop breakpoints

5. Add or update a regression test
   - Add a focused footer test that checks the updated year/copy/address/legal label when copy changed
   - If the work is layout-only, at least keep the diff narrowly scoped to the footer component/CSS and verify the exact rendered behavior in the browser

6. Verify
   - `npm run typecheck`
   - targeted footer tests
   - `npm run build`
   - for mobile layout fixes, verify in-browser at the reported device width that document `scrollWidth` no longer exceeds the viewport

7. Ship via PR
   - Create a branch from the latest `main`
   - Commit and push the change
   - Create a PR and keep the branch name aligned with the actual PR head branch

## Pitfalls
- Do not trust only one locale; footer/legal labels can differ by locale
- Do not update the footer component without checking shared navigation/legal constants
- Do not assume a label like `Terms of Use` is correct if the live site says `Terms of Service`
- Do not assume the main page body caused mobile horizontal overflow; the footer itself can widen the whole document
- Do not keep a mobile multi-column footer layout when long localized links still use `white-space: nowrap`; column minimums plus gap can exceed the viewport
- Do not solve footer overflow by slapping on `overflow-x: hidden` before measuring the real offender
- When introducing compact two-column mobile link lists, do not accidentally keep that grid on tablet/desktop if the established desktop pattern is a vertical list
- Confirm the PR head branch with `gh pr view` before pushing to avoid pushing to the wrong branch
- If the change is already merged into `main`, do not create a duplicate PR

## Mobile mixed-column policy

Use this pattern when the user wants a footer that is denser on mobile without reintroducing overflow:
- keep the outer footer sections stacked in one column on mobile when that is the safest width policy
- choose mobile link-list layout per section
  - `single`: long labels or preview/internal sections
  - `compact`: shorter marketing/navigation sections that can be shown as two columns
- implement the policy in component data rather than by special-casing visible text in CSS
- reset `compact` lists to the normal vertical list at tablet/desktop breakpoints unless the site explicitly wants grids there

## Suggested verification command sequence

```bash
npm run typecheck
npm run test:run -- src/components/layout/Footer.test.tsx
npm run build
```
