# Reference: /services/fde Rollout Test Patterns

This reference captures the exact test/CI patterns used when promoting `/t/services/fde` to canonical `/services/fde` in PR #554.

## Test files touched

| File | Action | Key change |
|------|--------|------------|
| `tests/src/app/services/fde/page.test.mjs` | **Created** | Asserts public page exists, `route.ts` absent, `robots: { index: true, follow: true }`, canonical `/services/fde` |
| `tests/src/app/t/services/fde/page.test.mjs` | **Deleted** | Old preview test removed |
| `tests/redirect-endpoints.test.mjs` | **Edited** | Removed FDE redirect rule from `expectedRedirectRules`; count changed `17` -> `16`; added absence assertions for preview and public redirect |
| `tests/services-preview-routes.test.mjs` | **Edited** | Removed FDE from `previewPages` and `redirectRoutes` |
| `tests/canonical-endpoints.test.mjs` | **Edited** | FDE header/footer links changed from `t(...)` to `"/services/fde"`; sitemap assertion for `/services/fde` added |
| `tests/link-and-metadata-integrity.test.mjs` | **Edited** | FDE header/footer links changed from `t(...)` to `"/services/fde"` |
| `tests/publication-detail-indexability.test.mjs` | **Edited** | Added `src/app/services/fde/page.tsx` to `publicIndexableListRoutes`; removed `src/app/t/services/fde/page.tsx` from `nonIndexableRoutes` |
| `tests/preview-navigation-path-helper.test.mjs` | **Unchanged** | `t()` helper contract stays valid even after rollout |
| `scripts/ci/test-groups.mjs` | **Edited** | Added `^tests/src/app/services/` to `staticPages` matchers |

## Key pitfall learned

When a public route replaces a `route.ts` redirect (not just a `/t/*` preview promotion), the redirect-endpoint test is the primary contract that must be updated. Do not only rename/move files; also:
1. Remove the redirect rule from the test data table
2. Decrement the total count assertion in the same test
3. Add explicit existence/absence assertions showing the rollout is complete

When moving a preview test to the canonical path, preserve the existing assertion content and adapt it for the public route — do not delete the old assertions and write a thin replacement from scratch. The public route test should be just as comprehensive as the preview test it replaces.
