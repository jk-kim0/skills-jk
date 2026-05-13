# Preserve orphan UI sections via an internal demo route

Use this when a follow-up on an existing PR reveals that recently deleted UI section components should be kept for design review rather than removed outright.

Trigger signals
- The PR deleted section/component files because they became unused.
- The user says not to delete them.
- The reason for keeping them is visual/UI review, design verification, or future showcase reuse.
- There is no longer a good public production route that should own them.

Recommended pattern
1. Restore the deleted component files on the existing PR branch.
2. Create an internal-only demo route such as `/internal/<demo-name>`.
3. Render the preserved components there with small representative sample data.
4. If the repo has an internal hub page, add the new demo route to that hub.
5. Add source-level tests asserting:
   - the internal demo page exists
   - it is `noindex`
   - it imports/renders the preserved components
6. Push the update to the same PR branch.

Why this pattern helps
- It preserves the component implementation without forcing it back into a production route.
- It gives reviewers a stable place to inspect the UI design.
- It avoids the false binary of either "keep it publicly wired" or "delete it entirely".

Pitfalls
- Do not assume "unused in the current route tree" means "safe to delete".
- Do not silently replace the deleted components with newly invented variants if the original files can simply be restored.
- If you add a new `tests/**/*.test.mjs` file in corp-web-japan, remember to run `node scripts/ci/assert-test-groups.mjs`.

Concrete session example
- PR follow-up on `corp-web-japan` PR #439 restored:
  - `src/components/sections/role-slides.tsx`
  - `src/components/sections/use-case-showcase.tsx`
- Added internal demo route:
  - `src/app/internal/demo-sections/page.tsx`
- Updated internal hub and tests accordingly.
