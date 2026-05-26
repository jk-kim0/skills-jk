# Shared component compatibility across route groups

Use this when a PR moves duplicated chrome/UI code into a shared component used by multiple Next.js App Router route groups, especially `(legacy)` and `(tailwind)` in corp-web-app.

## Lesson

A shared React component file proves API/code reuse, but it does not prove UI parity. Route groups can import different global CSS files, Tailwind layers, resets, CSS variables, and token definitions. The same component and CSS module can render differently when it depends on ambient variables or shared atomic components whose styles depend on those variables.

Concrete pattern observed in corp-web-app:

- `(legacy)/layout.tsx` imported `../globals.css`, which defined legacy tokens such as `--bg-group`, `--bg-white`, `--text-body`, and `--rem-*`.
- `(tailwind)/layout.tsx` imported `(tailwind)/globals.css`, which only imported Tailwind.
- A shared locale nudge banner used the same component/CSS in both route groups, but its nested `Button variant="black" size="sm"` computed a black background in legacy and a transparent background in the Tailwind route group because the button style depended on ambient legacy CSS variables/cascade.
- Declaring scoped variables on the shared wrapper may not be enough if the deployed CSS cascade still leaves a nested primitive property wrong. In that case, add a component-scoped class to the exact nested control and assert the critical style in the component CSS Module.

## Audit checklist

1. Confirm code reuse separately from visual parity:
   - both route-group shims import/re-export the same shared component;
   - both call sites pass the same props;
   - old duplicate implementations were identical or intentionally reconciled.
2. Inspect route-group layouts and global CSS imports:
   - compare `(legacy)/layout.tsx` and `(tailwind)/layout.tsx`;
   - compare each group’s `globals.css`;
   - list CSS variables/tokens used by the shared component and nested atomic components.
3. Probe actual rendered output at relevant breakpoints:
   - force the condition that shows the UI (for locale banners, browser language mismatch and no selected-locale cookie);
   - compare computed styles for container, text, select, action button, close button, and root CSS variables;
   - include nested elements, not only the shared wrapper.
4. Treat missing variable values as a compatibility risk even when geometry looks correct.
5. If the wrapper variables are present but a nested control still differs, inspect the nested control's computed property directly and fix with a component-scoped class on that exact control rather than broadening globals.
6. Do not claim “UI cannot break” from shared source alone. The strongest defensible source-only claim is “source drift is prevented”; UI parity requires computed-style evidence or explicit scoped fallbacks/classes plus deployed verification.

## Safer fixes

- Prefer adding the minimal required token/fallback surface for the affected route group or component.
- Avoid copying all legacy globals into a Tailwind route group just to fix one shared component.
- When a nested shared primitive still renders differently after scoped variables are added, do not assume the variable declaration alone wins the deployed cascade. Add a component-scoped class to the exact nested control (for example a locale banner action button) and assert the final property there, such as `background: var(--bg-dark)`, while keeping the fix inside the shared component's CSS Module.
- After any such fix, re-run a deployed Preview computed-style probe against both route-group URLs and the relevant breakpoints. Verify the nested primitive's computed value, not only the wrapper variables.
- Add source-level contract tests for shared imports and the scoped compatibility class/token surface, but pair them with browser/computed-style checks when reporting UI safety.
