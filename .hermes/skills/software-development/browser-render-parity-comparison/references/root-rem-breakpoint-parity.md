# Root rem breakpoint parity

Use this note when comparing corp-web-app against corp-web-japan or another QueryPie surface and the UI looks globally scaled differently.

## What to inspect

Check the computed root font size at the same viewport width on both pages:

```js
({
  url: location.href,
  width: window.innerWidth,
  rootFontSize: getComputedStyle(document.documentElement).fontSize,
  headerHeight: getComputedStyle(document.documentElement).getPropertyValue('--header-height'),
  layoutPadding: getComputedStyle(document.documentElement).getPropertyValue('--layout-padding'),
})
```

Do not rely only on source CSS or desktop screenshots. A page can report 16px at a wide viewport and 15px or 14px after responsive breakpoints.

## corp-web-app pattern observed

corp-web-app has used responsive `html` font-size rules in `src/app/globals.css`:

- default: `16px`
- `max-width: 1400px`: `15px`
- `max-width: 768px`: `15px`
- `max-width: 480px`: `14px`

corp-web-japan commonly keeps the browser default `16px` root because it does not set responsive `html` font-size overrides.

## Impact math

When normalizing corp-web-app from responsive roots to a constant 16px root, rem-based dimensions change by viewport band:

- above 1400px: `16px -> 16px` = no change
- 769–1400px: `15px -> 16px` = `+6.7%` for rem-based values
- 481–768px: `15px -> 16px` = `+6.7%` for rem-based values
- 480px and below: `14px -> 16px` = `+14.3%` for rem-based values

This affects rem-based typography, spacing, gaps, radii, heights, icon boxes, and custom properties such as `--rem-*`. It does not directly change px-fixed tokens, viewport units, percentages, or explicitly fixed mobile tokens such as `--layout-padding: 24px`.

## Safe implementation shape

If the task is to align corp-web-app root rem behavior with corp-web-japan, keep the change narrow:

1. Remove only the responsive `html { font-size: ... }` overrides.
2. Preserve unrelated mobile-specific root variables such as `--header-height` and `--layout-padding`.
3. Run `git diff --check` as a light verification.
4. In the PR body, call out the rem-scale impact percentages so reviewers know this is a global visual scaling change, not a local component bugfix.
