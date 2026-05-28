# Preview route public rollout promotion

Use this when review feedback says a preview/review route such as `/<locale>/t` is ready to be publicly rolled out.

## Core rule

Treat rollout as promotion, not duplication.

Do:

1. Move the existing route entry from the preview path to the public path.
   - Example: `src/app/[locale]/t/page.tsx` -> `src/app/[locale]/page.tsx`.
2. Move colocated locale authoring files with it.
   - Example: `page.en.tsx`, `page.ko.tsx`, `page.ja.tsx` move out of the preview directory too.
3. Move or rewrite route-local README/provenance notes so they describe the public route contract.
4. Move mirrored tests to match the public source route.
   - Example: `src/__tests__/app/[locale]/t/page.test.tsx` -> `src/__tests__/app/[locale]/page.test.tsx`.
5. Remove obsolete preview route entries and internal preview-index entries for the promoted page.
6. Update metadata tests to assert public canonical routes, such as `/en`, `/ja`, and `/ko`.
7. Add a negative source/file assertion only if helpful: the old preview route file should no longer exist.

Do not:

- Add a new public route that imports from the old preview route while leaving the preview route in place.
- Keep preview-route canonical metadata as a safety check after rollout.
- Keep an internal preview-index link for the exact promoted page.
- Describe the PR as preserving `/t` behavior unless the user explicitly asked to keep that compatibility path.

## Existing PR correction pattern

If this mistake was already pushed to an open PR:

1. Update the same PR branch; do not open a replacement PR.
2. Use `git mv`/file moves where possible so the PR shows promotion rather than copy-paste duplication.
3. Run the route-specific tests plus any internal preview-index test touched by removing the entry.
4. Run the repo's test-group assertion if a test file moved.
5. Amend the commit or squash the correction so the final branch has a clean rollout story.
6. Force-push with lease and rewrite the PR body to describe the final moved-route contract.
