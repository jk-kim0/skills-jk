# Content availability CI after main advances

Use this when an open corp-web-app PR starts failing routing/content availability tests after another content PR lands on `main`.

## Symptom

- PR CI runs on GitHub's pull request merge ref, not only the PR head.
- A workflow such as `Test routing` fails in an internal content availability route even though the current PR touched unrelated UI/CSS files.
- Example failure shape:
  - `src/__tests__/app/[locale]/internal/translations/blog/page.test.tsx`
  - expected a previous top-card locale/title or a missing locale badge
  - received newly restored/migrated content from latest `origin/main`

## Root cause pattern

Content availability tests may intentionally pin the current visible inventory and representative top row. When a separate PR adds missing MDX locale files, the loader output can legitimately change:

- record count or visible language availability changes;
- representative card title/description changes because fallback order selects a newly available locale;
- “English content missing” / “Japanese content missing” assertions become stale.

This is not necessarily a regression in the active PR.

## Repair workflow

1. Read the failed CI log and identify the exact failing test and expected/received content.
2. Rebase the PR branch onto latest `origin/main` before changing product code.
3. Re-run the failing test locally after the rebase.
4. Inspect the loader contract and current `src/content/**` files for the affected record.
5. If the current content state is correct, update the source-level test expectation to match the new inventory/locale availability.
6. Keep the active feature fix narrow; do not alter unrelated content loaders unless the loader contract itself is wrong.
7. Push with `--force-with-lease` after rebase and verify fresh CI runs are attached to the new head SHA.

## Example: blog translation fallback

`listBlogTranslationItems()` groups blog records by ID and uses the current fallback priority from `src/lib/publications/blog/records.ts`. If a new `.en.mdx` file is added for a top record, representative title/description assertions may shift from JA/KO to EN according to that fallback order. Update the internal translation route test to assert the new available locale link and remove stale “content missing” expectations for that locale.
