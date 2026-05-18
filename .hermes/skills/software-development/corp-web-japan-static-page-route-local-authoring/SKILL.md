---
name: corp-web-japan-static-page-route-local-authoring
description: Refactor and maintain corp-web-japan static marketing/preview routes so page.tsx owns visible copy/composition while shared section modules own UI primitives and tests cover route plus cross-cutting contracts.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, static-pages, route-local-authoring, nextjs, tests]
---

# corp-web-japan static page route-local authoring

Use this when maintaining corp-web-japan static marketing or preview routes, especially when a route should remain readable from `src/app/**/page.tsx` and section modules under `src/components/sections/**` should own only reusable UI primitives.

## Core route-local rule

- `page.tsx` owns route entry, metadata, visible copy, section order, and composition.
- `src/components/sections/**` owns styling, layout primitives, isolated client interaction, and visual implementation details.
- Avoid hiding a whole page or route-specific sequence behind wrappers such as `PlansPageContent`, `AipPlansContent`, or `PlansContentShell` when the wrapper merely bundles hero, tabs, pricing cards, or comparison tables.
- Prefer direct JSX primitive calls in each route when that makes review easier.

## Plans page pattern

For `/t/plans/aip` and `/t/plans/acp`:

- Keep finite variants as explicit sibling route files, not a dynamic `[product]` route.
- Keep pricing cards and comparison table copy directly in each route when reviewers need to inspect the authored content.
- Use shared plans primitives only for UI and behavior, such as:
  - `PricingContextProvider`
  - `ProductTabs` / `ProductTab`
  - `PlanCard` and child primitives
  - `CompareTable*` cell/row primitives
- Do not reintroduce `Object.assign(...)` local compound aliases or prop blobs like `rows={[...]}` / `columns={[...]}` for authored comparison-table content.

## Company-info hero reuse for plans

When plans AIP/ACP should match the company-info family pages like `/certifications` or `/news`, reuse the company page hero/container primitives directly in each route:

- `CompanyPageSection`
- `CompanyPageIntro`
- `CompanyPageTitle`
- `CompanyPageLead`

If these replace the plans-specific hero/container wrappers, remove the unused wrappers from the plans section module instead of leaving duplicate visual contracts:

- `PlansPageSection`
- `PricingHeader`
- `PlansHeroTitle`
- `PlansHeroDescription`

## Hidden test pitfall

Changing a route from one page-section/container primitive family to another can break cross-cutting source tests that are not the obvious route-specific test.

For plans hero/container changes, update both:

- `tests/src/app/t/plans/page.test.mjs`
- `tests/static-page-mobile-container-contract.test.mjs`

Do not stop after the narrow plans route test passes. Run the whole static-pages group because it catches cross-cutting contract failures:

```bash
node --test tests/src/app/t/plans/page.test.mjs tests/static-page-mobile-container-contract.test.mjs
node scripts/ci/run-node-tests.mjs staticPages
node scripts/ci/assert-test-groups.mjs
git diff --check
```

## PR follow-up workflow

When this work is a follow-up on an open PR:

1. Reuse the existing PR branch/worktree if it is open and current.
2. Inspect failing CI job logs with `gh run view <run-id> --job <job-id> --log` before guessing.
3. If CI fails only because a source-inspection test still encodes the old primitive contract, update the test to describe the new contract rather than reverting the implementation.
4. Re-run the affected test file and the relevant grouped test locally before pushing.
5. Verify the remote branch SHA with `git ls-remote origin refs/heads/<branch>` after push.

## Done criteria

- Route-visible copy/composition is readable in `page.tsx`.
- Shared section modules contain UI primitives only, not hidden authored content blobs.
- Route-specific and cross-cutting source tests agree on the final primitive/container contract.
- Static-pages group passes for changes touching static page layout, hero, or container primitives.
