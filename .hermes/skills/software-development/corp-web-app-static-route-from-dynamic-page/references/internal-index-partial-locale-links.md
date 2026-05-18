# Internal index partial-locale route links

Use this note when maintaining `corp-web-app` `src/app/[locale]/internal/internal-pages.ts` or the `/internal` link hub.

## Problem shape

Some internal child routes are implemented through `src/app/[locale]/internal/<slug>/page.tsx` but only provide `page.en.tsx` and intentionally `notFound()` for KO/JA. Stage can therefore look like:

- `/en/internal/<slug>` -> 200
- `/ko/internal/<slug>` -> 404
- `/ja/internal/<slug>` -> 404

If the index filters cards strictly by matching locale href, KO/JA users lose discoverability of useful English-only examples. If the index blindly creates KO/JA hrefs, it adds dead links.

## Preferred pattern

1. Verify route availability against stage or current deployed target before changing the inventory.
2. For routes available in all locales, keep locale-specific hrefs:
   - `/en/internal/sample-article`
   - `/ko/internal/sample-article`
   - `/ja/internal/sample-article`
3. For English-only routes, expose the card from every locale index, but map every locale to the existing English href:
   - EN index card -> `/en/internal/<slug>`
   - KO index card -> `/en/internal/<slug>`
   - JA index card -> `/en/internal/<slug>`
4. Do not revive explicitly removed labels or utility entries such as `MDX Preview`, `Live MDX editor`, or language selector links just because their backing route still exists. Use a neutral card label if the live route should remain discoverable.

A small helper keeps the inventory obvious:

```ts
function createEnglishOnlyInternalHref(slug: string): Record<Locale, string> {
  return {
    [Locale.EN]: `/en/internal/${slug}`,
    [Locale.KO]: `/en/internal/${slug}`,
    [Locale.JA]: `/en/internal/${slug}`,
  };
}
```

## Test expectations

Add/maintain tests that assert:

- English-only records are visible from all three locale indexes via the `/en/internal/...` href.
- Known missing KO/JA paths are not present, e.g. `/ko/internal/usage`, `/ja/internal/usage`, `/ko/internal/plans`, `/ja/internal/plans`.
- Fully localized pages keep their locale-specific hrefs.
- Removed labels stay absent from the page inventory.

## Example stage probe set

Useful probe shape:

```bash
for path in \
  /en/internal/usage /ko/internal/usage /ja/internal/usage \
  /en/internal/plans /ko/internal/plans /ja/internal/plans \
  /en/internal/sample-article /ko/internal/sample-article /ja/internal/sample-article; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://stage.querypie.com${path}")
  printf '%s -> %s\n' "$path" "$code"
done
```

Do not start a dev server for this check unless the user explicitly asks.
