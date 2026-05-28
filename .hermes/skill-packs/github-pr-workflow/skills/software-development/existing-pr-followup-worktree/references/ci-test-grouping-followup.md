# CI test grouping follow-up pitfall

Use this reference when an existing PR follow-up fails CI after adding, moving, or renaming tests.

## Symptom

A CI aggregate such as `Validate Lint`, `test:smoke`, or `assert-test-groups` fails even though the targeted test passes locally.

Example failure shape:

```text
AssertionError [ERR_ASSERTION]: Unassigned test files:
src/__tests__/app/<new-test>.test.tsx
```

A downstream aggregate job such as `Validate Test` may also fail only because the earlier lint/smoke dependency failed.

## Root cause pattern

Some repos explicitly partition tests into named CI groups. A newly added test file can be valid Vitest code but still fail CI if its path/name does not match any group matcher.

## Fix pattern

1. Read the CI log first and identify the exact failing step.
2. Reproduce the grouping gate locally, not just the targeted test:
   - `node scripts/ci/assert-test-groups.mjs`
   - or the repo wrapper such as `npm run test:smoke`
3. Inspect the repo's grouping matcher file, commonly under `scripts/ci/test-groups.*`.
4. Prefer matching the existing filename/path convention over widening grouping rules for a one-off test.
   - In corp-web-app routing tests, route-local tests commonly need a `*-route-local.test.tsx` filename to enter the routing group.
5. After the grouping gate passes, run the affected CI group locally, e.g. `npm run test:routing`.
6. If older tests fail, update their assertions to the new intended route/link/metadata contract rather than reverting the product change.

## Verification checklist

- Targeted test passes.
- Grouping assertion passes.
- Affected test group passes.
- Smoke/lint wrapper passes if it was the CI entrypoint.
- Push to the existing PR branch and monitor until the PR check rollup is clean.
