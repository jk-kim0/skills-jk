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

## Overlay placement and direction

Choose the panel direction from available space and trigger location, not from the word “dropdown” alone.

Common placement contracts:
- Top-bar/team switcher menus usually open downward: `.menu-panel { top: calc(100% + gap); }`.
- Sidebar footer/account menus usually open upward so they remain inside the viewport: `.sidebar-user-menu .menu-panel { top: auto; bottom: calc(100% + gap); }`.
- Right-aligned triggers should set `right: 0; left: auto;` when the panel must stay within the viewport edge.
- Responsive/mobile layouts often need to reset absolute placement to normal document flow: `.menu-panel { position: static; width: 100%; margin-top: gap; }`.

When a shared dropdown component is used in several places, prefer a placement-specific class on the instance (`sidebar-user-menu`, `menu-right`, `feature-visibility-panel`) rather than adding one-off placement logic to the component unless dynamic collision detection is actually required.

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

## Test guidance

For source-level UI contracts, add focused tests that assert:

- the menu uses a button trigger with `aria-expanded`, not native `<details>`, when explicit behavior is required;
- the trigger toggles state;
- outside-click listener is present;
- contextual keep-open markers are recognized;
- the shared component is used by each target menu;
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
