# Component Name Debug Mode staged implementation pattern

Use this reference when planning or implementing the outbound-agent `Show Component Name` debug UI or similar shell-wide debug utilities.

## Mode naming

Prefer these labels:

1. `Off`
2. `Pointer`
3. `Pointer + Ancestors`
4. `Always`

Use `Pointer`, not `Hover`, because the implementation should track pointer targets and `data-component-name` markers, not CSS `:hover` state.

Use `Pointer + Ancestors`, not `Hover & Ancestors`, because it makes the target-plus-ancestor-chain behavior explicit and reads better in a menu.

## Control placement

Apply the mode selector and overlay to all app shells, not only the authenticated shell:

- Authenticated `AppShell`: add a `Show Component Name` section inside the existing `HelpMenu`, below `Feature Visibility`.
- Public docs `DocsShell`: add an equivalent debug menu in the docs header nav, because docs pages do not use the authenticated Help dropdown.
- Mount `ComponentNameDebugOverlay` once per shell.

## Stacked PR sequence

For broad marker coverage, split the work as a stacked PR series rather than one large PR.

1. Documentation plan PR.
2. Shell foundation + shared component markers + representative route-local pages:
   - implement `Off`, `Pointer`, and `Pointer + Ancestors` only;
   - do not enable `Always` yet;
   - apply all-shell controls/overlay;
   - add markers to shared components;
   - cover three representative pages such as home, contact-lists, and settings/email-senders.
3. Second route-local coverage PR for another three representative pages such as companies, sales-people, and campaigns.
4. Remaining route-local coverage PR for the rest of authenticated routes, hidden routes, docs routes, teams/my-account/login as needed.
5. Final `Always` mode PR after coverage exists:
   - enable the fourth mode;
   - collect viewport-visible markers;
   - throttle position computation with `requestAnimationFrame`;
   - recalculate after scroll/resize/route transitions;
   - decide and implement max-label/overlap mitigation in that PR.

Before `Always` ships, keyboard cycling should be `Off → Pointer → Pointer + Ancestors → Off`.

After `Always` ships, keyboard cycling should be `Off → Pointer → Pointer + Ancestors → Always → Off`.

## Planning doc hygiene

When the user answers open questions:

- remove the open-question wording;
- add a `Resolved decisions` section;
- update PR sequencing and acceptance criteria so the resolved choices are concrete directives;
- distinguish final target modes from the modes implemented in early stacked PRs.
