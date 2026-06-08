# Component Name Debug vs Production Preview Toggle boundary

Use this when working on `corp-web-app` Component Name Debug, Preview Toggle, or reviewer/debug UI in header/layout surfaces.

## Durable rule

Component Name Debug may be included in production builds, but this does not permit exposing the Preview Toggle component in production UI.

Preview Toggle is a non-production reviewer/developer aid for switching selected navigation surfaces into preview mode. Production visitors must not see a Preview Toggle trigger, Preview mode ON/OFF menu items, or preview-navigation state indicators simply because Component Name Debug is enabled.

## Implementation pattern

- Keep Preview Toggle gated by `showPreviewModeToggle` from `getPreviewNavigationState`.
- Render Preview Toggle components only when `showPreviewModeToggle` is true.
- If Component Name Debug needs a production-visible mode control while `showPreviewModeToggle` is false, render a separate debug control surface such as `ComponentNameDebugControl`.
- The separate debug control should be labeled around Component Name Debug (for example `Component Name Debug menu`) and should not call preview-navigation API helpers or expose Preview mode ON/OFF controls.
- Do not use a prop such as `showPreviewModeControls=false` to repurpose the Preview Toggle component as a generic reviewer-tools/debug menu in production. That makes the visible component semantics ambiguous and can leak Preview Toggle UI into production.

## OpenSpec contract

Record both sides of the boundary:

- `openspec/specs/platform-component-name-debug/spec.md`: Component Name Debug production availability does not imply Preview Toggle production availability; production debug controls must be independent from Preview Toggle.
- `openspec/specs/platform-preview-toggle/spec.md`: Preview Toggle component/control remains non-production only, and Component Name Debug availability must not override that boundary.
- `openspec/project.md`: add the broad project principle so future feature PRs discover it.

## Regression test pattern

Add/keep source-level tests that assert:

- Header variants render `<PreviewModeToggle ...>` / `<TailwindPreviewModeToggle ...>` only behind `showPreviewModeToggle`.
- Header variants render the separate debug control behind `!showPreviewModeToggle && componentNameDebugEnabled`.
- Preview Toggle sources do not contain a debug-only fallback prop/path such as `showPreviewModeControls` or `Reviewer tools menu`.
- The separate debug control source contains `Component Name Debug menu` and does not contain Preview mode labels or preview-selection handlers.

## PR workflow pitfall

If the original PR is merged before this follow-up is pushed, GitHub may keep `gh pr view <old-pr>` showing the old head SHA even after recreating/pushing a branch with the same name. Confirm with REST (`gh api repos/<owner>/<repo>/pulls/<n> --jq '{state,merged,head}'`). If the old PR is merged, create a new follow-up PR instead of trying to update the closed PR.