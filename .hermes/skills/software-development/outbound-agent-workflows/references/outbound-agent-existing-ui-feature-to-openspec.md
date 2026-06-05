# Outbound Agent existing UI feature to OpenSpec pattern

Use this when the user asks to document an already-implemented Front App UI/debugging behavior in `openspec/` rather than implement new code.

This is the Outbound Agent specialization of the generic `openspec-decision-management` reference `references/existing-implemented-feature-to-openspec.md`; use that generic pattern first, then apply the repo-specific anchors below.

## Pattern

1. Treat the work as docs-only unless the user explicitly asks for implementation.
2. Inspect the current implementation first enough to avoid documenting stale assumptions.
   - For Component Name Debug, useful anchors were `front/src/lib/ui/component-name-debug.ts`, `front/src/components/component-name-debug-overlay.tsx`, and `front/src/components/component-name-debug-menu-section.tsx`.
   - Search tests as well when behavior is already locked by source-level tests.
3. Inspect existing OpenSpec inventory before creating a new spec.
   - Read `openspec/README.md`, `openspec/specs/README.md`, `openspec/project.md`, and candidate `openspec/specs/**/spec.md` files.
   - Prefer extending the existing canonical platform or contract spec when the behavior is part of a broader foundation contract.
   - Exception: if the user explicitly wants an independent, reusable, cross-app feature spec, create a dedicated `platform-*` foundation spec instead of burying it in a broad app foundation spec. For Component Name Debug, use `platform-component-name-debug` rather than `show-component-name` or `platform-front-app-foundation`.
   - For reusable Component Name Debug availability, do not introduce runtime environment-variable toggles; use a build-time implementation code constant. If any related config/spec names are needed, avoid app-specific prefixes such as `OUTBOUND` and keep names app-neutral.
4. Convert implementation behavior into OpenSpec Requirements and Scenarios.
   - Use `SHALL`, `SHALL NOT`, `MAY`, `SHOULD` carefully.
   - Split broad behavior into small Requirements: authoring/source contract, controls/shortcuts, visibility/collection, label placement/copy behavior, and environment availability.
   - For Component Name Debug, explicitly document the mode cycle (`Off -> Pointer -> Pointer + Ancestors -> Always -> Off`), the `Alt+Shift+N` shortcut, corner label placement, click-to-copy, and production availability.
   - Scenarios should be implementable as source-level tests or UI smoke tests.
5. Capture production/debug availability as a first-class contract when the feature is operator-facing.
   - Default availability should be explicit, including whether production is enabled by default.
   - If an environment variable can restrict the feature to non-production, specify both the enabled and disabled production scenarios.
   - When a build-time code constant disables the feature, document all affected surfaces consistently: keyboard shortcut, overlay/markers, and the app-specific mode control surface should be absent or inert. Do not make Outbound Agent's Help menu placement a universal requirement for other apps such as corp-web-japan.
   - Prefer app-neutral config names for new reusable specs. If documenting an already-landed app-specific variable, record the exact current variable only as implementation-alignment detail and avoid expanding the reusable contract around the app prefix.
6. Keep implementation terms only when needed for future agents to wire tests/code correctly.
   - Internal marker names such as `data-component-name` are acceptable in platform specs.
   - Avoid over-documenting one component file as the product contract when the contract is really mode behavior.
7. Verify as docs-only work.
   - Run `git diff --check`.
   - Run a lightweight check for required headings/phrases and conflict markers when no OpenSpec validator exists.
   - Do not run full app build/test for a Markdown-only OpenSpec change unless the user asks or repo policy requires it.
8. If creating a PR, clearly state that app CI/build was skipped because the change is docs-only and report any docs-scope CI result.

## Pitfalls

- Do not create a new narrow spec when an existing `platform-*` spec already owns the foundation contract.
- Do not document from chat memory alone; inspect the current implementation and current OpenSpec first.
- Do not add wrappers, code changes, or tests when the request is to document existing behavior.
- Do not bury keyboard shortcut sequence, menu labels, or copy-to-clipboard behavior inside prose only; make them explicit Scenarios.
