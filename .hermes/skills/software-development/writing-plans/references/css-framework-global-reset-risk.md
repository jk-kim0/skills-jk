# CSS framework adoption: global reset and cascade risk

Use this reference when writing a plan for introducing or expanding Tailwind/another utility CSS framework in a repository that already has global CSS and CSS Modules.

## Session-derived pitfall

A page ported from `corp-web-japan` to `corp-web-app` appeared to have the right Tailwind class names and generated CSS rules, but the deployed page still rendered with missing spacing. Browser computed styles showed section padding as `0px` even though classes such as `pt-[112px]`, `lg:pt-[144px]`, and `px-[30px]` were present.

Root cause: `corp-web-app/src/app/globals.css` kept an unlayered reset:

```css
* {
  box-sizing: border-box;
  padding: 0;
  margin: 0;
}
```

Tailwind v4 emits utilities inside `@layer utilities`. Unlayered CSS can outrank layered utility rules, so the legacy reset defeated spacing utilities. The reference repo placed base/reset behavior inside `@layer base`, allowing utilities to win.

## Planning guidance

When a plan introduces Tailwind or migrates a route to Tailwind while legacy CSS remains:

1. Treat global reset/base-layer changes as a broad visual-risk item, not a small implementation detail.
2. Separate route/page migration from global reset restructuring unless the user explicitly asks to bundle them.
3. For the first route migration, prefer route-scoped temporary CSS Module or stable `data-*` selector corrections over changing global reset behavior.
4. Require browser computed-style validation, not just source review or class-name checks:
   - `padding`, `margin`, `width`, `maxWidth` on the section and ancestors
   - root/body font settings
   - exact Preview URL against exact reference URL when parity is the goal
5. Plan a later dedicated PR to move reset/base rules into the correct framework layer, e.g. `@layer base` for Tailwind v4.
6. Plan a cleanup follow-up after the global-layer PR to remove temporary route-scoped corrections that are no longer needed.

## Plan wording pattern

Use wording like:

- "This route migration must not change `src/app/globals.css` reset behavior. While the legacy unlayered reset remains, use route-scoped CSS Modules / stable `data-*` selectors to preserve computed spacing for this route."
- "A separate visual-risk PR should move reset/base rules into `@layer base` and verify representative CSS Modules surfaces before removing route-scoped workarounds."
- "Acceptance criteria must verify computed styles in the browser; className presence alone is insufficient."
