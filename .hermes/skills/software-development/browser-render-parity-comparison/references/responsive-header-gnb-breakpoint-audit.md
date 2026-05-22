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

## Example findings from corp-web-app

Treat these as examples, not durable truth for every branch. Always re-check the active worktree and exact deployed URL before applying breakpoint values; the user's correction in a later session showed that carrying an older example forward can produce the wrong implementation.

### Historical stage example

On one historical `https://stage.querypie.com/en/t/platform/ai/aip/usage-based-llm` snapshot, the GNB had two interaction modes but three responsive visual bands:

- `> 1260px`: desktop horizontal GNB. Logo left, horizontal menu (`Solutions`, `Features`, `Company`, `Plans`) center, language/search/CTA right, hamburger hidden.
- `769px–1260px`: mobile-style hamburger GNB with an ~88px header. Logo + language/search/hamburger are visible; opened hamburger shows a full-width vertical panel with Solutions, Features, Company, Plans and bottom Contact Us / Free Now CTAs.
- `<= 768px`: same hamburger interaction, but compact phone header height changes to 60px and the panel starts at the shorter header offset.

Historical source confirmation in that snapshot:

- `src/components/layout/header/lib/use-is-mobile-header.hook.ts`: `window.innerWidth <= 1260`
- `src/components/layout/header/lib/use-is-phone-width.hook.ts`: `window.innerWidth <= 768`
- `src/components/layout/header/ui/header.module.css`: `@media (max-width: 1260px)` switches desktop tools off and mobile toggle/nav panel on.
- `src/app/globals.css`: `@media (max-width: 768px)` changes `--header-height` to `60px`.

### Later corp-web-app route-group example

A later corp-web-app branch used a different contract. The correct reading came only after rechecking both hooks and CSS:

- `> 1260px`: desktop container, `max-width: 1200px`, no side padding.
- `851px–1260px`: tablet/narrow band with desktop horizontal GNB still visible; only container side padding is added via `var(--layout-padding)`.
- `<= 850px`: mobile/compact interaction band; desktop GNB/tools are hidden and hamburger/mobile menu appears.
- `<= 479px`: phone compact band; global variables set `--header-height: 60px` and `--layout-padding: 24px`.

Source confirmation in that branch:

- `src/components/layout/header/lib/use-is-mobile-header.hook.ts`: `window.innerWidth <= 850`
- `src/components/layout/header/lib/use-is-phone-width.hook.ts`: `window.innerWidth <= 479`
- `src/components/layout/header/ui/header.module.css`: `@media (max-width: 1260px)` adds side padding only; `@media (max-width: 850px)` switches to mobile toggle/nav panel.
- `src/app/globals.css`: `@media (max-width: 479px)` changes compact phone header/layout variables.

## Pitfalls

- Do not rely only on screenshots near the breakpoint. A viewport screenshot can be mislabeled after a resize if not rechecked; use `window.innerWidth` and DOM rects in the same probe.
- Do not count opened/closed hamburger states as separate viewport UI types unless the user asks for state count. Distinguish interaction modes from responsive layout bands.
- Browser accessibility snapshots may include hidden menu descendants. Confirm visibility with computed style, rect size, opacity, and pointer-events before treating an item as visible.
