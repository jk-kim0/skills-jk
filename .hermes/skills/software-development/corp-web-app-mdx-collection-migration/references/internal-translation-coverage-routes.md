# Internal translation coverage routes for MDX collections

Use this pattern when the user asks for an internal route that audits whether an MDX publication family has EN/JA/KO records, such as `/_translations/events`, `/:locale/_translations/events`, `/_translations/blog`, or `/:locale/_translations/blog`.

## Route shape

- Prefer an internal underscore path: `/_translations/<family>` and `/:locale/_translations/<family>`.
- Do not use `/translations/<family>` unless the user explicitly requests a public non-underscore route.
- Implement the unprefixed and locale-prefixed pages separately in App Router:
  - `src/app/_translations/<family>/page.tsx`
  - `src/app/[locale]/_translations/<family>/page.tsx`
- Validate `params.locale` in the locale-prefixed route and call `notFound()` for unsupported locales.

## Data model

Build a small `src/lib/translations/<family>.ts` loader that groups publication records by stable numeric/string `id`:

- one row per content ID
- `locales` map keyed by `Locale.EN`, `Locale.JA`, `Locale.KO`
- exclude `hidden` and `redirectUrl` records when the route is meant to mirror visible list-page coverage
- sort rows by ID descending with numeric comparison where possible
- use fallback display priority `EN -> KO -> JA`

For each locale entry, carry enough fields for the intended review UI rather than only booleans:

```ts
type LocaleEntry = {
  id: string;
  locale: Locale;
  title: string;
  description?: string;
  slug: string;
  date?: string;
  eventDate?: string;
  imageSrc?: string;
  badge?: string;
  href: string;
  sourcePath: string;
};
```

## UI contracts by family

Events-style coverage:
- show the title once per row
- title fallback: English title first, then Korean, then Japanese
- show EN/JA/KO availability badges; make available badges links to the corresponding detail/preview route
- hide thumbnails if the user says they are unnecessary
- display `eventDate` when present, otherwise fall back to `date` frontmatter

Blog/resource-list-style coverage:
- use the same card data as the `/:locale/t/<family>` list page when the user asks for list-card parity
- include thumbnail (`heroImageSrc`), title, `listDescription ?? description`, formatted date, badge, and detail link
- on `/:locale/_translations/<family>`, default the preview card to the current locale when that locale record exists
- allow hover/focus on an available locale badge to preview that locale's full card data, not just the title
- keep missing locales as disabled badges/spans, not broken links

## Tests

Add route/loader tests that pin the contract:

- loader returns only the intended visible records and sorts by ID descending
- root route renders the summary and availability rows/cards
- locale-prefixed route uses the current URI locale as the default display locale
- hover/focus over an available language changes the preview data when the UI supports previewing
- tests mirror the source route path under `src/__tests__/app/_translations/<family>/...` when the repo uses that convention

Run the targeted test plus the repo's test-group assertion when new test files are added:

```bash
npx vitest run src/__tests__/app/_translations/<family>/page.test.tsx
node scripts/ci/assert-test-groups.mjs
git diff --check
```

## Pitfalls

- Do not revive an old merged translation-route branch for the next family. After one family PR merges, create a fresh worktree/branch from latest `origin/main` for the next family.
- Do not count every MDX file blindly if the visible list contract excludes hidden or redirect-backed records. State the visible count explicitly in tests and PR body.
- Do not show one title per locale when the user wants one title per content ID; use the fallback title once and keep locale availability separate.
- Do not leave `/translations/*` paths in tests/docs after the route policy changes to `/_translations/*`.
