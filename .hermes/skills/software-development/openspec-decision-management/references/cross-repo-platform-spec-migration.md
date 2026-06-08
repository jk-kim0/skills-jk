# Cross-repo platform spec migration

Use this when moving an accepted OpenSpec platform/contract spec from one repository into another app repository.

## Pattern

1. Treat the source PR/spec as evidence, not as text to copy blindly.
   - Inspect the source PR body and changed files.
   - Pull the canonical source spec from the merged base branch when possible.
   - Identify source-app-only references: app name, paths, menus, env names, docs, test files, UI placement assumptions.

2. Check whether the target repo already has `openspec/`.
   - If it does not, add a minimal scaffold instead of a large imported hierarchy:
     - `openspec/project.md`
     - `openspec/specs/README.md`
     - `openspec/specs/<spec-id>/spec.md`
   - If it already has an OpenSpec scaffold, extend the existing structure instead of overwriting it:
     - add only the new `openspec/specs/<spec-id>/spec.md`;
     - append one inventory row to `openspec/specs/README.md`;
     - add one project-context bullet only when the new platform contract should be globally discoverable;
     - add `openspec/README.md` only if the target scaffold lacks one.
   - Make the target `project.md` describe the target repo's real stack, route conventions, docs, rollout boundaries, and spec-to-test principle.

3. Preserve the durable platform contract while adapting target-specific surfaces.
   - Keep requirement/scenario semantics such as `SHALL`, mode order, keyboard shortcut behavior, marker contract, dropdown trigger/menu behavior, cookie/API state transition semantics, and verification scenarios.
   - Replace implementation paths with target repo locations.
   - Replace source-app control placement assumptions with app-specific control-surface language.
   - Remove source-app product names unless they are explicitly used as historical/naming rationale.
   - When the target has parallel active implementations during migration (for example legacy and Tailwind route-group layout components), either update every active variant or explicitly document which variant is intentionally out of scope. Add a source-level contract test that checks all active variants share the same behavior.

4. Add discovery links in the target repo.
   - Add the new `openspec/` directory to the README/project structure if the repo documents directories.
   - Add an OpenSpec inventory link so future agents can find the canonical spec.

5. Verify narrowly.
   - `git diff --check`.
   - Run the repository's lightweight test-group/scope classifier when one exists, before relying on CI.
   - Search the new `openspec/` scope for source-app-specific terms and paths.
   - Check relative links only in changed/new OpenSpec scope, or explicitly exclude known pre-existing broken links outside the change.
   - Avoid running broad formatters over pre-existing large test/docs files just to touch one assertion; if a formatter causes unrelated line wrapping, revert the broad reformat and reapply the smallest semantic edit.

## Pitfalls

- Do not import source-app `openspec/project.md` wholesale; it often contains product/domain assumptions that do not apply to the target app.
- Do not leave source-app control placement assumptions such as a specific Help menu unless the target app intentionally has that same surface.
- Do not let pre-existing broken README links block a docs-only migration; report them as pre-existing and verify the new/changed links separately.
- Do not implement runtime code when the request is to migrate the spec; leave implementation for a follow-up PR unless the user explicitly asks for code.
