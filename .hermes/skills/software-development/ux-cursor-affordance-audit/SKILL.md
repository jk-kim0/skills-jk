---
name: ux-cursor-affordance-audit
description: Audit and fix cursor affordance issues in web UIs by checking actual browser computed cursor states, preferring CSS-only fixes, and verifying interactive controls vs. static text behavior.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ux, cursor, browser-verification, css, accessibility]
---

# UX Cursor Affordance Audit

Use this skill when a user reports that the cursor does not match the UI’s interaction model, especially for headers, nav items, cards, buttons, and headline/text regions.

## Goal

Make cursor behavior explicit and consistent:
- interactive controls should show `cursor: pointer`
- static text/headings should keep the default arrow cursor
- avoid unnecessary markup changes when CSS can express the intent

## Workflow

1. Inspect the live page in a browser.
2. Read computed cursor values on the relevant elements.
3. Check the actual DOM ancestry of the element being hovered; the visual element may be wrapped in a different section/container than expected.
4. Identify whether the issue is caused by:
   - missing `cursor-pointer` on an interactive control
   - accidental inherited cursor styling from an ancestor
   - an overly broad selector that affects text
   - browser default text-cursor behavior on headings or selectable text
   - the absence of a shared cursor affordance contract in global CSS
5. Prefer the smallest CSS change that expresses intent clearly.
6. Only change markup when semantics or event handling actually require it.
7. When the UI has a repeated interaction pattern, prefer a global CSS contract in `globals.css` (for example: body default, interactive elements pointer, editable text text-cursor) over per-component cursor declarations.
8. Match selectors to the actual rendered DOM, not the component name or an assumed wrapper ID. For example, a hero heading may live under `main section:first-of-type h1` even if the source component uses a different internal structure.
9. If you add a global cursor contract, remove redundant per-component cursor declarations that would duplicate or conflict with the global rule.
10. Re-verify in the browser after the fix.

## Practical Rules

- Buttons, clickable links, disclosure triggers, menu toggles, and clickable cards should use `cursor-pointer`.
- Titles, paragraphs, labels, and other static copy should not be forced to `pointer`.
- If a heading is intended to behave like ordinary text, ensure it stays `cursor-default` or `cursor: default` via CSS.
- Use selectors that match the real rendered structure, not assumptions from the component name or route section name.
- When using utility classes or CSS modules, ensure the cursor rule lands on the actual clickable element, not only on a parent wrapper.

## Common Pitfalls

- Assuming semantic HTML alone guarantees pointer affordance. It does not in all browsers/UI states.
- Targeting the wrong container because the page uses nested sections or reusable layout components.
- Using an ID selector that does not exist in the rendered page.
- Applying pointer styles too broadly and accidentally making headings or body copy look clickable.
- Fixing a cursor issue with JSX changes when a CSS rule is sufficient.

## Verification

After changing styles:
- confirm interactive controls report `pointer` in `getComputedStyle(el).cursor`
- confirm static headings/text report `auto` or `default` as intended
- check the live browser hover state on the affected elements
- if the page uses a fixed header or hero section, verify both the control area and the title/body area

## Example Approach

- Header menu button: add `cursor-pointer`
- Hero headline: add `cursor-default` only if needed to override unintended text-cursor behavior
- Keep the markup untouched unless the element is semantically wrong or not actually interactive
