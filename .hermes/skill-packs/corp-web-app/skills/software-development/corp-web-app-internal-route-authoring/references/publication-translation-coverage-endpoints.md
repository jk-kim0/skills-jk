# Publication Translation Coverage Endpoints

Session-derived pattern from adding `/internal/translations/news` after the existing blog endpoint.

## When to use

Use this pattern when adding an internal-only translation coverage page for an MDX publication family that already has locale-specific list-card helpers such as `list<Family>PublicationItems(locale)`.

## Implementation shape

1. Keep the route internal-only:
   - `src/app/[locale]/internal/translations/<family>/page.tsx`
   - `src/app/[locale]/internal/translations/<family>/_components/*`
2. Export noindex/nofollow metadata and do not add canonical alternates.
3. Add family translation grouping next to the family publication record helper:
   - `type <Family>TranslationLocaleEntry = <Family>PublicationListItem & { locale: Locale }`
   - `type <Family>TranslationListItem = <Family>PublicationListItem & { locales: Partial<Record<Locale, <Family>TranslationLocaleEntry>> }`
   - `list<Family>TranslationItems()` loops `[Locale.EN, Locale.JA, Locale.KO]`, groups by stable numeric `id`, picks primary display data by `[Locale.EN, Locale.KO, Locale.JA]`, and sorts by numeric ID descending.
4. Reuse the blog translation gallery/page UI pattern for card preview behavior:
   - Card defaults to current locale if available.
   - Available language badges link to `/<locale>/t/<family>/<id>/<slug>`.
   - Hover/focus previews the selected locale's thumbnail/title/description.
5. Add the page to `src/app/[locale]/internal/internal-pages.ts` under `Translation coverage` with `createLocaleTranslationHref('<family>')`.
6. Add route-mirrored tests under:
   - `src/__tests__/app/[locale]/internal/translations/<family>/page.test.tsx`
   - update `src/__tests__/app/internal-index-page-route-local.test.tsx` for the internal index link.

## Verification

Preferred narrow checks:

```bash
npx vitest run 'src/__tests__/app/[locale]/internal/translations/<family>/page.test.tsx'
node scripts/ci/assert-test-groups.mjs
git ls-files | grep -E '(^src/app/(\[locale\]/)?translations|^src/__tests__/app/translations)' && exit 1 || echo 'no public translations route files tracked'
git grep -nE '/(en|ko|ja)/translations|/translations/' -- src public || true
```

If the broader internal-index test imports CSS-bearing layout modules and a fresh worktree lacks local PostCSS/Tailwind dependencies, it may fail before assertions with `Cannot find module '@tailwindcss/postcss'`. Do not run `npm install` by default for this user; report it as dependency-resolution blocking and rely on the narrow route test, test-group assertion, and source exposure scans.

## Pitfalls

- Do not create top-level `/translations/*` route files or public-looking test paths.
- Do not add sitemap/canonical/public navigation exposure for these internal review pages.
- When copying the blog endpoint, grep the new family subtree for stale family strings, IDs, and expected counts before committing.
- In PR bodies, say the internal-index suite was blocked during CSS collection if that is what happened; do not describe it as an assertion failure.
