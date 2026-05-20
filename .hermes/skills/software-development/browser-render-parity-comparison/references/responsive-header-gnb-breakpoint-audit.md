# Responsive header/GNB breakpoint audit note

Use when a user asks how a site's global navigation changes around viewport widths, especially when the issue is a desktop-width page switching to a mobile/hamburger UI.

## Proven workflow

1. Open the exact requested deployed URL in the browser.
2. Resize across likely breakpoints and collect both visual and DOM/accessibility evidence:
   - 1280px / 1261px / 1260px / 1200px for desktop-to-mobile header cutovers.
   - 769px / 768px / 767px for tablet-to-phone header or spacing cutovers.
3. For each width, probe:
   - `window.innerWidth`
   - header height and rect
   - logo, language selector, search, CTA, hamburger button rects
   - main nav rect, `position`, `opacity`, `transform`, `display`
   - hamburger `aria-label` and `aria-expanded`
   - visible top-level menu labels and opened-panel menu sections
4. If a local repo is available, verify the responsive contract in source after observing the live page. Look for:
   - CSS media queries controlling header layout.
   - JS hooks such as `useIsMobileHeader` or `useIsPhoneWidth` that duplicate breakpoint logic.
   - global CSS variables such as `--header-height` that change at narrower widths.
5. Report the result in two layers:
   - Interaction modes: e.g. desktop horizontal nav vs mobile hamburger/full-panel nav.
   - Viewport bands: e.g. desktop, tablet/narrow-desktop hamburger, compact phone hamburger.

## Example finding from corp-web-app stage

On `https://stage.querypie.com/en/t/platform/ai/aip/usage-based-llm`, the GNB has two interaction modes but three responsive visual bands:

- `> 1260px`: desktop horizontal GNB. Logo left, horizontal menu (`Solutions`, `Features`, `Company`, `Plans`) center, language/search/CTA right, hamburger hidden.
- `769px–1260px`: mobile-style hamburger GNB with an ~88px header. Logo + language/search/hamburger are visible; opened hamburger shows a full-width vertical panel with Solutions, Features, Company, Plans and bottom Contact Us / Free Now CTAs.
- `<= 768px`: same hamburger interaction, but compact phone header height changes to 60px and the panel starts at the shorter header offset.

Source confirmation in that repo:

- `src/components/layout/header/lib/use-is-mobile-header.hook.ts`: `window.innerWidth <= 1260`
- `src/components/layout/header/lib/use-is-phone-width.hook.ts`: `window.innerWidth <= 768`
- `src/components/layout/header/ui/header.module.css`: `@media (max-width: 1260px)` switches desktop tools off and mobile toggle/nav panel on.
- `src/app/globals.css`: `@media (max-width: 768px)` changes `--header-height` to `60px`.

## Pitfalls

- Do not rely only on screenshots near the breakpoint. A viewport screenshot can be mislabeled after a resize if not rechecked; use `window.innerWidth` and DOM rects in the same probe.
- Do not count opened/closed hamburger states as separate viewport UI types unless the user asks for state count. Distinguish interaction modes from responsive layout bands.
- Browser accessibility snapshots may include hidden menu descendants. Confirm visibility with computed style, rect size, opacity, and pointer-events before treating an item as visible.
