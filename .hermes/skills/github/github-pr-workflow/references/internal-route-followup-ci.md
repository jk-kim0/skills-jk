# Internal route follow-up CI pitfalls

Use this reference when an existing PR follow-up moves public-looking pages into an internal/admin route namespace and CI fails in routing tests.

## Pattern observed

A PR added translation coverage links to an internal index and then moved the coverage pages from public-like routes such as `/translations/events` and `/{locale}/translations/blog` to internal routes such as `/{locale}/internal/translations/events`.

The app changes were correct, but the routing CI failed in a broad source-level guard:

```text
expected ... not to contain 'English'
```

The failing test was intentionally protecting against resurrecting an old locale selector or MDX editor entries in the internal index. New copy introduced the words `English`, `Korean`, and `Japanese` in descriptions, so the guard failed even though no selector UI had been restored.

## Preferred fix

Do not weaken or delete the negative guard first. Preserve the test's intent and adjust the new internal/admin copy so it does not reuse guarded selector labels.

Example:

```ts
// Risky for an internal index with broad negative locale-label guards
'Review event translation coverage across English, Korean, and Japanese records.'

// Safer
'Review event translation coverage across EN, KO, and JA records.'
```

## Verification checklist

1. Read the failed CI log for the exact failing assertion and line number.
2. Identify whether the assertion is guarding removed UI/copy rather than testing the new feature directly.
3. Search the touched internal index/config files for the forbidden strings.
4. Prefer a copy/label adjustment that keeps the existing negative assertion meaningful.
5. Run the narrow test if dependencies allow; otherwise run source greps plus the route-specific tests that do not require the missing local dependency.
6. Push to the same PR branch and verify fresh CI attaches to the new head SHA.
