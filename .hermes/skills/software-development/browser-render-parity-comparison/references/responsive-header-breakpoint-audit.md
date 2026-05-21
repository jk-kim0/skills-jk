# Responsive header/GNB breakpoint audit

Use this when a header/GNB changes behavior by viewport width, especially when a mobile drawer breakpoint is being narrowed or widened.

## What to inspect

1. Find every source of the same breakpoint contract:
   - React/client hooks such as `useIsMobileHeader()` or `useIsPhoneWidth()`.
   - CSS Modules media queries controlling header layout, menu items, mega-menu/menu-space, preview/debug toggles, and global variables.
   - Global CSS custom properties that indirectly change header height or panel padding.

2. Distinguish interaction bands from visual bands:
   - Example shape: desktop horizontal GNB, tablet/narrow mobile-style drawer, compact phone drawer.
   - A mobile drawer range like `480px..850px` usually means:
     - `isMobileHeader <= 850`
     - compact phone helper / global phone styles `<= 479`
     - desktop starts at `851px`.

3. Check fixed-width containers before lowering a mobile breakpoint:
   - If desktop remains active below the previous breakpoint, fixed widths like `width: var(--content-max-width)` can create edge collisions or horizontal overflow.
   - Prefer `width: 100%; max-width: var(--content-max-width)` for desktop header containers that must shrink below the content max width.
   - Then add explicit side padding/gutters if content should not touch the viewport edge.

4. Audit mobile padding separately from desktop padding:
   - Header logo may have its own left padding.
   - Mobile utility/hamburger wrapper may have its own right/left padding.
   - Drawer panel content often uses `padding: ... var(--layout-padding) ...`.
   - Bottom CTA bars may be full-width with only button-inner padding.

5. Verify exact boundary widths in the browser or via source-level probes:
   - One pixel below/above each boundary, e.g. `479`, `480`, `850`, `851`.
   - Confirm visible controls: horizontal nav vs hamburger, header height, drawer panel top, and side gutters.

## PR notes

When updating an existing PR for this class of change, update the PR body so it names the final breakpoint ranges and any container/gutter fixes. Do not leave stale ranges from earlier iterations.