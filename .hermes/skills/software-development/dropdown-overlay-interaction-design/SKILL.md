---
name: dropdown-overlay-interaction-design
description: Design and implement dropdown/popover menus with correct trigger toggle, outside-click dismissal, and contextual modal/modeless keep-open behavior in React/Next.js UIs.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [React, Next.js, UI, Dropdown, Popover, Accessibility]
    related_skills: [systematic-debugging, browser-render-parity-comparison]
---

# Dropdown / Overlay Interaction Design

Use this when implementing or reviewing dropdown menus, popovers, top-bar menus, account/team switchers, visibility filters, or similar overlay controls.

## Core naming model

Use precise names when discussing the UI:

- **Trigger / collapsed trigger**: the visible collapsed area the user clicks before the menu opens.
- **Dropdown panel / overlay panel**: the expanded menu body.
- **Menu item / action item**: a selectable item inside the panel.
- **Contextual UI**: a modal or modeless surface launched from the menu that remains conceptually connected to that menu action.

If the user calls the collapsed visible area “A”, map A to the trigger/collapsed trigger.

## Default interaction contract

1. Clicking the trigger toggles the menu open/closed.
   - Closed + trigger click => open.
   - Open + same trigger click => close.
2. Clicking outside the menu closes it by default.
3. Pressing Escape closes it.
4. Selecting an ordinary menu item closes it.
5. A contextual modal/modeless surface launched from the menu may keep the menu open if it is explicitly marked as connected context.
   - Use an explicit opt-in marker such as `data-dropdown-context` or `data-dropdown-keep-open`.
   - Clicks inside that contextual surface should not be interpreted as outside-click dismissal.
6. Do not keep menus open for arbitrary outside clicks.
   - The exception is only for connected modal/modeless context, not unrelated page content.

## React implementation pattern

Prefer a shared client component for repeated menu behavior instead of relying on native `<details>/<summary>` when outside-click and contextual exceptions matter.

Minimum behavior to encode:

```tsx
const contextSelector = "[data-dropdown-context], [data-dropdown-keep-open]";
const selectableSelector = "a, button, [role='menuitem'], [data-dropdown-close]";

function handlePointerDown(event: PointerEvent) {
  const target = event.target;
  if (!(target instanceof Element)) return;
  if (menuRef.current?.contains(target) || target.closest(contextSelector)) return;
  setIsOpen(false);
}

function closeAfterSelection(event: React.MouseEvent<HTMLDivElement>) {
  const target = event.target;
  if (!(target instanceof Element)) return;
  if (target.closest(contextSelector)) return;
  if (target.closest(selectableSelector)) {
    window.requestAnimationFrame(() => setIsOpen(false));
  }
}
```

Trigger attributes:

```tsx
<button
  aria-controls={panelId}
  aria-expanded={isOpen}
  aria-haspopup="menu"
  onClick={() => setIsOpen((current) => !current)}
  type="button"
>
  ...
</button>
```

Panel attributes:

```tsx
{isOpen ? (
  <div id={panelId} role="menu" onClickCapture={closeAfterSelection}>
    {children}
  </div>
) : null}
```

## Adapting shadcnui-blocks Workspace Switcher patterns

When the user asks to use the shadcnui-blocks `Workspace Switcher` example for a real app team/workspace switcher, treat the block as a visual and interaction pattern, not as complete product logic.

- Keep the shadcn/Radix `DropdownMenu` structure.
- Map `Workspace` to the app’s actual domain term, such as `Team`.
- Use the trigger pattern with avatar/fallback, primary name, secondary metadata, and `ChevronsUpDown`.
  - If the user asks for a blank profile image, render an intentionally empty/neutral `AvatarFallback`; do not invent an initial, logo, or profile image.
- Use menu rows with avatar/fallback, primary/secondary text, and a `Check` icon for the current item.
- Preserve authoritative app switching behavior such as server actions, form submit, routing, redirects, and session persistence; do not replace it with the demo’s client-only `useState` unless the product explicitly only needs local selection.
- Prefer item-shaped current rows (`DropdownMenuItem disabled` or equivalent) over unrelated plain `<span>` rows when visually matching the switcher.
- Keep real product actions only. If the user says dropdown grouping is unnecessary, remove section labels/group headings instead of preserving demo labels like `Workspaces`, `Switch Team`, or `Team actions`.
- When pruning actions, explicitly remove stale menu items from both UI and source-level tests; for example, if only `Create Team` remains, assert that `Manage Team` and `Team settings` are absent.
- If the user asks to introduce the Workspace Switcher as a reusable UI Widget, extract a client component such as `WorkspaceSwitcher` instead of leaving the pattern inline in `AppShell` or a page. The widget should accept generic items, `selectedWorkspaceId`, optional action link props, and the app's authoritative switch action/form behavior.

See `references/shadcnui-blocks-workspace-switcher-adaptation.md` for the extracted example shape and adaptation checklist.
See `references/reusable-workspace-switcher-widget.md` for the reusable widget extraction contract and source-level test checklist.

## Overlay placement and direction

Choose the panel direction from available space and trigger location, not from the word “dropdown” alone.

Common placement contracts:
- Top-bar/team switcher menus usually open downward: `.menu-panel { top: calc(100% + gap); }`.
- Sidebar footer/account menus usually open upward so they remain inside the viewport: `.sidebar-user-menu .menu-panel { top: auto; bottom: calc(100% + gap); }`.
- Right-aligned triggers should set `right: 0; left: auto;` when the panel must stay within the viewport edge.
- With Radix/shadcn dropdowns, prefer the primitive placement props for this contract: `side="bottom" align="end"` makes a top-bar panel open below the trigger while aligning the panel’s right edge to the trigger’s right edge, so the panel expands toward the left instead of off to the right.
- Responsive/mobile layouts often need to reset absolute placement to normal document flow: `.menu-panel { position: static; width: 100%; margin-top: gap; }`.

When a shared dropdown component is used in several places, prefer a placement-specific class on the instance (`sidebar-user-menu`, `menu-right`, `feature-visibility-panel`) rather than adding one-off placement logic to the component unless dynamic collision detection is actually required.

## Menu item copy and alignment

For compact internal utility menus, keep the collapsed trigger terse but the panel readable:

- Use a short visible trigger only when space is constrained, and keep the full purpose/current state in `aria-label`.
- Prefer concise item labels with sentence-style capitalization unless the product term is a proper noun.
- Keep descriptions short enough to scan in one or two lines.
- Apply explicit left alignment and normal wrapping to option rows when using button-like menu items; centered button defaults often make dropdown option text look broken.
- If the selected item needs emphasis, style the row state separately from the text layout so the active row does not change alignment.

## When native `<details>` is not enough

Native `<details>/<summary>` can be fine for simple disclosure content, but it is usually not enough when the product contract requires:

- closing on arbitrary outside clicks,
- preserving open state for connected modal/modeless contexts,
- shared behavior across multiple menus,
- consistent Escape handling,
- testable open-state contracts.

In those cases, replace it with an explicit stateful client component.

## Form-flow dropdowns that may redirect users away

When a dropdown field is backed by a separate setup/registry screen (for example selecting an Email Sender, credential, team asset, billing profile, or similar prerequisite), design the form sequence around the fact that the user may need to leave the form to add a missing option.

1. Put the prerequisite dropdown at the top of the form, before fields that would be lost if the user navigates away.
2. Put the setup action inside the dropdown panel, not as a detached paragraph/button below unrelated fields.
   - Prefer concise action copy such as `+ Add an Email Sender`, `+ Connect account`, or `+ Add option` over long explanatory copy in the form body.
3. Move long conceptual guidance to the backing setup/registry screen when that guidance explains how the registry works rather than how to fill the current form.
4. If the custom dropdown feeds a server action or ordinary HTML form, keep a hidden form input in sync with the selected item and make the visible trigger purely interactive.
5. When there are no selectable items, keep the dropdown actionable: show an empty-state row plus the setup link so the user learns the recovery path at the moment they discover the missing option.
6. Source-level tests should pin both the field order and the placement of the setup action so future edits do not regress the flow.

## Viewport resize dropdowns

When implementing an internal dropdown that changes the browser to standard review viewport sizes, treat the documented CSS-pixel viewport as the target for `window.innerWidth / window.innerHeight`, not as an outer window size.

Use `window.resizeTo(window.outerWidth + widthDelta, window.outerHeight + heightDelta)` where the deltas are computed from the current inner viewport, then re-check and retry a bounded number of times. A single outer-size calculation can miss the target because browser chrome, toolbar changes, maximized windows, or OS clamping can change the relationship between outer and inner dimensions.

Also show the current viewport using `innerWidth × innerHeight`, highlight the matching option only when the inner viewport is actually at the target, and note browser/OS limitations in PR or docs. See `references/viewport-resize-dropdown-pattern.md` for a compact implementation pattern and tests.

## Test guidance

For source-level UI contracts, add focused tests that assert:

- the menu uses a button trigger with `aria-expanded`, not native `<details>`, when explicit behavior is required;
- the trigger toggles state;
- outside-click listener is present;
- contextual keep-open markers are recognized;
- the shared component is used by each target menu;
- when a migration has multiple active implementations of the same control (for example legacy CSS Modules and Tailwind variants), every active variant exposes the same dropdown trigger/menu semantics or the out-of-scope variant is explicitly documented;
- form-flow dropdowns that can redirect users away appear before later form fields whose values would otherwise be lost;
- missing-option setup actions live inside the dropdown panel rather than as detached explanatory buttons below the field.

If runtime browser testing is not requested or would require starting a dev server, keep local verification light and rely on CI, while still running `git diff --check` and narrow source-level tests when dependencies are available.

## Pitfalls

- Do not describe every clickable top-bar control simply as “dropdown”; name the trigger, panel, and menu items separately so reviewers can discuss behavior precisely.
- Do not treat modal/modeless clicks as ordinary outside clicks when that surface was launched from the dropdown and remains part of the same task context.
- Do not make the contextual keep-open behavior implicit for all page elements. Require an explicit marker.
- Do not leave inconsistent labels such as plural/singular variants if the user has named the action explicitly, for example prefer the requested `Manage Team` label over an accidental `Manage teams` variant in that context.

## References

- `references/team-feature-visibility-dropdown-contract.md` — compact example from a top-bar Team switcher and Feature visibility menu refactor.
