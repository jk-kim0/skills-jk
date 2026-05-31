---
name: css-sticky-overflow-debugging
description: "Debug why position: sticky works on one page but not another by comparing computed styles, ancestor overflow, and scroll containers before changing layout code."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [css, sticky, layout, browser, debugging, overflow]
---

# Debug sticky positioning with overflow-aware comparison

Use this when `position: sticky` appears correct in code but behaves differently across pages.

Core idea:
- Do not guess from JSX alone.
- Compare a working page and a broken page in the browser.
- Sticky failures are often caused by an ancestor with non-visible overflow becoming the sticky containing block / scroll container.

## When to use
- One route's sidebar/header sticks, another route's identical component does not
- The sticky element already has `position: sticky` and `top: ...` in code
- Layout wrappers differ slightly between pages

## Investigation steps

### 1. Confirm the sticky element itself is the same
Search for the shared component/class.

Example checks:
- same component file
- same `sticky` utility/classes
- same `top` offset

If the sticky element differs, fix that first. If not, continue.

### 2. Compare the page wrappers in code
Search each page for the nearest large layout wrapper, especially `<main>` and section containers.

Look for differences such as:
- `overflow-x-hidden`
- `overflow-hidden`
- `overflow-auto`
- transforms / containment / custom scroll containers
- different wrapper nesting

### 3. Verify in the browser with computed styles
Use browser/devtools evaluation, not just source reading.

Read for both working and broken pages:
- sticky element computed `position`
- sticky element computed `top`
- nearest relevant ancestor classes
- wrapper computed `overflowX` / `overflowY`

Useful browser-side snippet pattern:
- find `main`
- find the sidebar nav by aria-label or unique text
- walk up to the nearest `aside`
- return class names and computed overflow/position values

### 4. Form the root-cause hypothesis
Most common result:
- working page: ancestor overflow remains `visible`
- broken page: ancestor has `overflow-x-hidden` and computed overflow becomes non-visible / `auto`
- sticky is still `position: sticky`, but it is constrained by that ancestor instead of the viewport

Important nuance:
- even if only `overflow-x-hidden` was set in source, browser computed behavior can still make the wrapper act as a sticky-breaking scroll container for the layout.
- Treat the computed browser result as the source of truth.

## Fix strategy
Prefer the smallest safe fix:
1. remove the overflow constraint from the layout wrapper on the affected sticky-list pages only
2. if overflow is needed for some other child, move that overflow rule down to a narrower wrapper instead of the page root
3. keep the sticky component itself unchanged if it already works on the reference page

## Sticky sidebar footer pattern

Use this when the user asks for a left-sidebar footer/account area to remain visible even while the main content scrolls.

UI terminology:
- call the behavior a **sticky sidebar footer**, **sticky account area**, or **viewport-pinned user account area**;
- CSS implementation is usually `position: sticky` on the sidebar/container, not `position: fixed` on the account box, unless the sidebar is outside the normal layout flow.

Implementation pattern:
1. Make the sidebar the viewport-height sticky column:
   - `.sidebar { position: sticky; top: 0; height: 100vh; min-height: 100vh; display: flex; flex-direction: column; }`
2. Make the navigation/content area the scrollable region:
   - `.sidebar > nav { min-height: 0; flex: 1 1 auto; overflow-y: auto; }`
3. Keep the footer/account area outside the scrollable nav and non-shrinking:
   - `.sidebar-footer { flex: 0 0 auto; margin-top: auto; }`
4. In responsive/mobile layouts where the sidebar becomes a normal top section, explicitly reset sticky/height and restore normal overflow.

Pitfall: do not put `overflow-y: auto` on the whole sidebar if the account area must stay visible. Put overflow on the nav area only, otherwise the footer scrolls away with the navigation.

## Verification
After the fix:
- re-check computed styles in the browser
- confirm the affected wrapper no longer has the sticky-breaking overflow behavior
- confirm the sticky element still has the same `position: sticky` and `top`
- run the narrowest relevant tests/typecheck

## Repo-workflow note
If doing this inside an open PR follow-up:
- use a fresh worktree from the PR branch tip
- commit and push back to the same PR branch
- mention explicitly that the root cause was ancestor overflow, not the sticky sidebar component itself
