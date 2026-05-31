# Team / Feature visibility dropdown contract example

Session pattern captured from a React/Next.js top-bar refactor with two adjacent menus:

- Team name menu: current Team display, Team switch action, and Team actions.
- Feature visibility menu: local UI visibility filter (`Released only`, `Released + In-Progress`, `All features`).

## User-facing review conclusion

The requested interaction model is sound:

1. The collapsed visible area should be treated as the dropdown trigger.
2. Trigger click should toggle open/closed state.
3. Clicking outside should close by default.
4. If a menu action such as `Create Team` or `Manage Team` opens a connected modal/modeless UI, clicks inside that contextual surface should keep the menu open.
5. Other unrelated page clicks should cancel the expanded menu state.

## Implementation sketch used

Create a shared client dropdown component with:

- `isOpen` state;
- a `button` trigger with `aria-expanded`, `aria-controls`, and `aria-haspopup="menu"`;
- document-level `pointerdown` outside-click handling while open;
- document-level `keydown` Escape handling while open;
- `data-dropdown-context` / `data-dropdown-keep-open` exceptions for connected modal/modeless UI;
- ordinary item selection close behavior through a selectable target selector.

Important selectors:

```ts
const contextSelector = "[data-dropdown-context], [data-dropdown-keep-open]";
const selectableSelector = "a, button, [role='menuitem'], [data-dropdown-close]";
```

## Labeling note

When the user explicitly names a menu action, align the UI label with that name. In the captured case, the menu action was normalized from `Manage teams` to `Manage Team` because the user referred to the action as `Manage Team` and the surrounding context was a Team menu.

## Verification shape

A lightweight source-level test can assert:

- no native `<details>` remains in the target menu sources;
- the shared dropdown component exposes `aria-expanded` and trigger toggle logic;
- outside-click handling checks the contextual keep-open selector;
- target menus use the shared dropdown component;
- user-facing labels match the agreed action names.

If the worktree lacks installed dependencies, do not encode that as a durable tool limitation. Run `git diff --check`, push the PR, and let CI validate once dependencies are present.
