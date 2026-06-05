# Existing implemented feature to OpenSpec pattern

Use this when the user asks to document behavior that is already implemented in the repository under `openspec/`, especially UI/debug/operator-facing features.

## Pattern

1. Treat the task as documentation-only unless the user explicitly asks for implementation changes.
2. Inspect the current implementation and tests before writing requirements.
   - Identify the source files that own the behavior, user controls, state transitions, persistence, environment gating, and edge cases.
   - Inspect existing source-level or UI tests so the spec reflects locked behavior instead of chat memory.
3. Inspect OpenSpec inventory before creating a spec.
   - Read `openspec/README.md`, `openspec/specs/README.md`, `openspec/project.md`, and candidate existing `openspec/specs/**/spec.md` files when present.
   - Prefer extending an existing class-level `platform-*` or `contract-*` spec when it already owns the foundation area.
   - Create a new `platform-*` or `contract-*` spec only when the feature is independently reusable or no existing owner exists.
4. Convert implementation behavior into explicit Requirements and Scenarios.
   - Use `SHALL`, `SHALL NOT`, `MAY`, and `SHOULD` deliberately.
   - Split behavior into small requirement groups such as authoring/source contract, mode controls/shortcuts, state transition cycle, visibility/overlay rendering, click/copy interactions, accessibility, persistence, and environment availability.
   - Write GIVEN/WHEN/THEN scenarios that a future test or smoke check could validate.
5. Keep product/app neutrality when documenting reusable platform behavior.
   - Avoid app-specific config prefixes, menu placements, or component names in the reusable contract unless they are current implementation evidence.
   - If a feature can be adopted by multiple apps, define the platform contract separately from the current app's control surface.
6. Verify docs-only work lightly.
   - Run `git diff --check` and a lightweight scan for conflict markers, required headings, and stale relative links if docs moved.
   - Do not run full app build/test for Markdown-only OpenSpec changes unless the repository requires it or the user asks.

## Pitfalls

- Do not document from chat memory alone; inspect code and tests first.
- Do not add code, tests, wrappers, or visual changes when the user only asked to document existing behavior.
- Do not bury concrete mode cycles, shortcuts, labels, placement rules, copy behavior, or environment availability in prose only; make them explicit Scenarios.
- Do not create a narrow one-off spec when a broader platform/contract spec already owns the topic.
