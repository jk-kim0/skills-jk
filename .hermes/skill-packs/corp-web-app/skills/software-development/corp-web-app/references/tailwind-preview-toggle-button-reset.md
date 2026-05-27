# Tailwind preview toggle vs scoped header button reset

Use this note when a Tailwind-authored control is rendered inside the corp-web-app header or other shared chrome that still carries CSS Module reset rules.

## Symptom

A Tailwind button renders with the right size/layout/text color, but its intended background or border does not appear after route-group Tailwind migration.

Example surface:
- Preview Toggle button in the Tailwind header

## Root cause pattern

The legacy/shared header scope still defines a broad button reset such as:

- `background: none;`
- `border: none;`

In this repo that pattern exists in header-scoped CSS like `headerScope button { ... }`.

That means a Tailwind utility such as `bg-*` or `border` can lose to the scoped reset depending on selector strength/order, especially inside mixed Tailwind + CSS Module chrome.

## Preferred fix in corp-web-app

1. Confirm the control is inside a shared scope that resets `button` styles.
2. Prefer the Tailwind-specific component on Tailwind routes/chrome instead of reusing the CSS Module version by habit.
3. Re-assert the visual contract on the actual button element with explicit utilities.
4. When the scoped reset is the competing rule, use important Tailwind utilities for the affected properties rather than broad wrapper changes.

Concrete pattern used successfully:
- `!bg-[#15181d]`
- `!bg-white/95`
- `!border`
- `!border-[rgba(21,24,29,0.12)]`

Keep the change narrow to the affected control. Do not weaken or delete the shared header reset unless the task is explicitly about repo-wide chrome cleanup.

## Good verification

Use a source-level regression check when local Tailwind/PostCSS execution is flaky or expensive.

Useful assertions:
- Tailwind header imports the Tailwind preview toggle component rather than the CSS Module variant.
- The Tailwind preview toggle source still contains the forced background/border utilities.

This is especially helpful in fresh worktrees where CSS-related test startup can fail before reaching assertions.
