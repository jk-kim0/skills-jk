# News internal translation coverage test drift

Use this when a corp-web-app PR fails `Test routing` in `src/__tests__/app/[locale]/internal/translations/news/page.test.tsx` after new news MDX records land on `main`.

## Symptom

CI may fail with assertions like:

- expected `listNewsTranslationItems()` to have a fixed length such as `25`, but current data has a larger count
- expected summary text such as `25 news records`, but the page renders the current count
- a hover/current-locale sample expects a hard-coded record to be missing a locale, but that record has since gained a translation

This often appears after a separate news PR adds or localizes a new record, while the sitemap or route PR itself did not change the internal translations UI.

## Root cause

The internal news translation coverage page is data-driven. Tests that hard-code total record counts, first-row IDs, or a specific “missing locale” sample become stale whenever news content changes.

## Durable fix pattern

1. Reproduce the failing test locally:
   - `npm exec vitest -- run 'src/__tests__/app/[locale]/internal/translations/news/page.test.tsx'`
2. Inspect the current data source:
   - `listNewsTranslationItems()` from `src/lib/publications/news/records.ts`
3. Keep stable contract assertions:
   - page remains noindex
   - records are in ID-descending order
   - rendered row count matches `listNewsTranslationItems().length`
   - rendered summary text uses the current length
   - known contract sample records, such as hidden ISO 42001 ID 25, still expose expected links/hidden badge when relevant
4. Replace brittle sample assumptions with data-selected samples:
   - for current-locale fallback/hover tests, find an item matching the required shape, e.g. `!item.locales.ko && item.locales.en && item.locales.ja`
   - compare rendered text/link values to the selected item’s actual locale entries
5. Verify both focused and grouped tests:
   - `npm exec vitest -- run 'src/__tests__/app/[locale]/internal/translations/news/page.test.tsx'`
   - `npm run test:routing`

## Pitfalls

- Do not update only the numeric literal; the next news record will break it again.
- Do not weaken the test to merely “renders rows”; keep ordering, count, hidden-record, and locale-preview contracts.
- If CI `Validate Test` fails after `Test routing`, inspect `Test routing` first; `Validate Test` may only be aggregating the earlier group failure.
