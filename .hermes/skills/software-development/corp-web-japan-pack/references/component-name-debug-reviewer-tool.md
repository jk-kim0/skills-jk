# Component Name Debug reviewer tool in corp-web-japan

Use this reference when implementing or extending the `platform-component-name-debug` capability in `corp-web-japan`.

## Durable implementation pattern

- Treat Component Name Debug as reviewer tooling that may be available in production builds.
- Do not gate availability by runtime environment variables or operations settings on the same build artifact.
- Use a build-time code constant, defaulting to enabled unless a Product Owner or launch policy explicitly chooses a disabled build.
- Keep shared contract code under `src/lib/`, including:
  - mode definitions and ordering
  - localStorage key and CustomEvent name
  - `data-component-name` marker helper and marker validation
  - shortcut mode cycling helpers
- Use a single global client overlay under `src/components/layout/` rather than per-component hover labels.
- Use `data-component-name` on meaningful existing component roots only. Do not add wrapper-only components just to show labels.

## Required mode contract

Expose the modes in this exact order:

1. `Off`
2. `Pointer`
3. `Pointer + Ancestors`
4. `Always`

`Alt+Shift+N` cycles in that order and is ignored while focus is in `input`, `textarea`, `select`, or `contenteditable` elements.

## corp-web-japan control placement

`corp-web-japan` can attach the selector to the existing site-header reviewer tools surface rather than copying Outbound Agent's Help menu.

Important production-availability pitfall:

- The Preview Mode Toggle may be hidden by preview-navigation policy.
- Component Name Debug must still be reachable when its build-time constant is enabled.
- Therefore the header should show a reviewer/debug tools menu when either preview controls are visible OR Component Name Debug is enabled.
- If preview controls are hidden, render the Component Name Debug section without exposing preview ON/OFF controls.

## Overlay behavior

- `Off`: no labels.
- `Pointer`: closest marked component for the current pointer target.
- `Pointer + Ancestors`: closest marked component plus marked ancestors.
- `Always`: viewport-visible marked components only; ignore offscreen or zero-size markers and cap the label count to avoid overload.
- Render each component label twice: bottom-left and top-right of the component bounds.
- Label buttons should be clickable copy targets with `pointer-events: auto` while the overlay root remains non-interfering with `pointer-events: none`.
- Preserve the previous pointer target while the pointer moves onto a copy label so the label does not disappear before click.

## Verification pattern

Prefer source-level Node tests in `tests/component-name-debug.test.mjs` and register them in `scripts/ci/test-groups.mjs` under `assetsShell`.

Minimum source-test assertions:

- build-time constant is enabled and does not read `process.env`
- mode labels/order and shortcut wiring
- marker attribute and validation
- header marker coverage for representative surfaces
- pointer/ancestor/always collection code paths
- bottom-left/top-right placement and no top-left label
- Clipboard copy path and label copy attribute
- Component Name Debug menu remains independent from preview controls

Run focused verification before PR:

```bash
git diff --check
./node_modules/.bin/eslint src/lib/component-name-debug.ts src/components/layout/component-name-debug-overlay.tsx src/components/layout/component-name-debug-menu-section.tsx src/components/layout/preview-mode-toggle.tsx src/components/layout/site-header-client.tsx --max-warnings=0
npm run test:assets-shell
```

If repo-wide `typecheck` fails because dependencies are missing from local `node_modules`, report it as an environment/setup limitation and keep the focused verification evidence. Do not encode missing packages as a durable repo rule.
