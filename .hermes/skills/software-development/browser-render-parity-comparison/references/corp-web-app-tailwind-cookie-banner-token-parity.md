# corp-web-app Tailwind route cookie banner token parity

Session pattern: a Tailwind App Router route group used a minimal group global (`@import "tailwindcss";`) while still rendering the shared legacy `CookiePreference` banner. The banner container CSS loaded, but nested shared `Button`, `Text`, and `Link` modules depended on legacy global CSS variables such as `--rem-*`, `--text-*`, `--doc-blue-text`, `--color-blue`, `--border-gray`, and `--bg-white`. They also relied on a legacy global button reset for `white-space: nowrap`. On Tailwind routes those variables/reset values were missing, so computed output fell back to browser/default Tailwind-reset values: black cookie links, wrapping Korean button text, taller buttons/banner, and black inherited text instead of the legacy banner UI.

Diagnosis recipe:

1. Open the exact legacy reference URL and Tailwind target URL with cookie preferences unset.
2. Probe the cookie banner container, content, description, and buttons on both pages:
   - `getComputedStyle(document.documentElement).fontSize`
   - container padding/background/boxShadow/position/width
   - description font-size/line-height/color
   - cookie markdown links color/text-decoration (`--doc-blue-text` should resolve to the legacy blue)
   - each button background, border, border-radius, padding, gap, color, font-size, line-height, width/height, and `white-space`
3. If the container mostly matches but nested buttons/text/links do not, inspect the nested component CSS for `var(--...)` usage and compare against `src/app/globals.css` token definitions plus global reset assumptions such as `button { white-space: nowrap; }`.

Safe fix pattern:

- Do not copy legacy globals into `src/app/(tailwind)/globals.css`; keep the Tailwind group global minimal.
- Add only the needed legacy token values to the cookie banner CSS root/scope (for example `.container`) so CSS variable inheritance restores the nested Button/Text computed styles.
- Keep the fix in the shared component CSS only when the component is already used by both route groups and the scoped tokens preserve the legacy rendering in legacy routes too.
- Add a source-shape test or focused assertion that the scoped banner CSS contains the needed token contract while the Tailwind globals remain minimal.

Concrete token set from the cookie banner case:

```css
.container {
  --rem-28px: 1.75rem;
  --rem-22px: 1.375rem;
  --rem-20px: 1.25rem;
  --rem-16px: 1rem;
  --rem-15px: 0.9375rem;
  --rem-14px: 0.875rem;
  --rem-10px: 0.625rem;
  --rem-6px: 0.375rem;
  --text-default: #24292f;
  --text-title: #24292f;
  --text-white: #f6f6f6;
  --doc-blue-text: #0356cc;
  --color-blue: #0762d4;
  --color-blue-hover: #2f81f7;
  --border-gray: #afb8c1;
  --bg-white: #ffffff;
  --bg-white-hover: #f3f4f7;
}
```

Review note: if computed hover color is not part of the visible requested state, still copy the source-of-truth value from `src/app/globals.css` rather than guessing a nearby GitHub blue.