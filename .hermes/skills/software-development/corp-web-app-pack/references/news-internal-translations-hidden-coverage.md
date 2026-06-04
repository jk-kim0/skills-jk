# News internal translation coverage and hidden records

Use this when updating `corp-web-app` internal news translation coverage at `/{locale}/internal/translations/news`.

## Pattern

- Keep the public news list behavior unchanged: `listNewsPublicationItems(locale)` should still use `newsPublicationRepository.list({ locale })` by default, so `hidden` records stay out of public `/news` list pages.
- For the internal translation coverage route only, add/use an explicit option such as `includeHidden: true` so the coverage inventory is complete.
- Build hidden-inclusive entries from `newsPublicationRepository.records`, filtered by exact locale and `!record.redirectUrl`; preserve URL-accessible hidden records.
- Carry `hidden: boolean` on both locale entries and grouped translation list items.
- Render a visible `Hidden` label/badge on cards whose displayed locale entry is hidden.
- Keep sitemap/search semantics aligned with URL accessibility: hidden should not imply exclusion when the detail URL is accessible; `redirectUrl` and `noindex` still govern exclusion for public search surfaces.

## Verification

Run the focused internal route test plus related repository/sitemap tests:

```bash
npm exec vitest -- run src/__tests__/app/[locale]/internal/translations/news/page.test.tsx src/lib/resources/__tests__/news-migration.test.ts src/__tests__/app/sitemap-xml-route.test.ts src/lib/resources/__tests__/publication-repository.test.ts
npm run test:smoke
```

## Pitfalls

- Do not make the public `/news` list include hidden records while trying to fix the internal translation route.
- Do not label the whole row from a stale grouped flag if the UI previews another locale; prefer showing `Hidden` based on the currently displayed locale entry.
- Do not put tests under dotted route directories such as `src/app/sitemap.xml`; CI/Vitest discovery and test grouping may miss them. Use `src/__tests__/app/...` and update `scripts/ci/test-groups.mjs` if a new test path is introduced.
