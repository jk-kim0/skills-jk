# corp-web-app Archived Index Route Pattern

Use this reference when adding a lightweight index/list page for migrated archived static routes.

Session pattern: after PR 671 added archived route-local pages, add a separate PR from latest `origin/main` when the original PR is already merged. Do not revive or force-push the merged branch.

## Route shape

- Default index: `src/app/archived/page.tsx` -> `/archived`
- Locale wrappers:
  - `src/app/en/archived/page.tsx` -> `/en/archived`
  - `src/app/ko/archived/page.tsx` -> `/ko/archived`
  - `src/app/ja/archived/page.tsx` -> `/ja/archived`
- Shared route-local authoring files:
  - `src/app/archived/page.en.tsx`
  - `src/app/archived/page.ko.tsx`
  - `src/app/archived/page.ja.tsx`
  - `src/app/archived/archived-index-page.tsx`
  - `src/app/archived/archived-pages.ts`

## UI pattern

Match the existing `/internal` page style when the user asks for that comparison: keep it simple, e.g. a heading plus a bullet list of links. Avoid over-designing the page.

Manual registry is acceptable and often preferable for a small archived section:

```ts
export const archivedPages = [
  {
    title: 'Why QueryPie ACP',
    description: 'Archived Why QueryPie ACP route-local page',
    hrefByLocale: {
      en: '/en/archived/why-querypie-acp',
      ko: '/ko/archived/why-querypie-acp',
      ja: '/ja/archived/why-querypie-acp',
    },
  },
];
```

Use automatic route discovery only if it is genuinely simple and does not require brittle filesystem logic or runtime server work. For two or three archived pages, direct links are clearer.

## Metadata

Use `noindex, nofollow` for internal/maintenance-oriented archived index pages unless the user explicitly wants public indexing.

Canonical examples:

- `/archived` default page canonical: `${baseUrl}/archived`
- KO wrapper canonical: `${baseUrl}/ko/archived`

## Verification

Add a targeted route test that verifies:

- heading renders;
- each listed page link points to the correct locale-specific archived path;
- metadata has `robots: 'noindex, nofollow'`;
- canonical URLs match default and localized routes.

Run:

```bash
npm run test:run -- src/__tests__/app/archived-index-route.test.tsx
npx prettier --check <new route files and test>
```
