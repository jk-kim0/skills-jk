# Tailwind/legacy shared UI compatibility

Use this reference when a shared layout or UI component renders correctly in `(legacy)` routes but differs in `(tailwind)` routes.

## Durable lesson

`(legacy)` routes import the broad legacy globals, including design tokens and element resets. `(tailwind)` routes intentionally keep globals minimal. When a component shared by both route groups depends on legacy tokens or resets indirectly through shared primitives, the component can render differently in Tailwind routes even if the React tree is identical.

Prefer fixing the component's scoped CSS contract over broadening Tailwind globals, unless the task explicitly asks to change global Tailwind route behavior.

## Diagnostic workflow

1. Confirm whether the same component is mounted from both route-group layouts or pages.
2. Trace all shared primitives used inside the affected component, especially `Button`, text components, markdown/link renderers, and layout wrappers.
3. List CSS variables and element resets those primitives expect from `src/app/globals.css`.
4. Compare that contract with `src/app/(tailwind)/globals.css`; do not assume Tailwind routes inherit legacy globals.
5. For a component-scoped fix, define only the required legacy-compatible tokens/resets under the component root selector, not at `:root` or in Tailwind globals.
6. Keep scoped values source-aligned with `src/app/globals.css`; if a token like hover background exists there, copy the exact value rather than approximating it.
7. Add a source-shape check/test when possible so future changes keep the compatibility contract visible.
8. If browser parity is used, compare computed values and visible geometry for the exact affected route, not just whether the component appears.

## Cookie preference banner example

The cookie preference banner is mounted by both `(legacy)/layout.tsx` and `(tailwind)/layout.tsx`. Its UI can differ in Tailwind routes because it uses shared primitives that expect legacy tokens such as text colors, rem-size variables, document link blue, button colors, border/background colors, and `button { white-space: nowrap; }` behavior.

A narrow fix is to declare those required variables and button reset behavior under the cookie banner container selector. This preserves the minimal Tailwind globals contract while making the shared banner self-sufficient in both route groups.

## Pitfalls

- Do not fix a single shared component mismatch by importing all legacy globals into `(tailwind)` routes unless the requested scope is a global route-group policy change.
- Do not use visually close token values. Match the legacy source-of-truth values exactly, including hover tokens.
- Do not claim full future compatibility for every possible shared primitive variant. State the verified contract: current component tree, current variants, and current responsive/interaction states checked.
