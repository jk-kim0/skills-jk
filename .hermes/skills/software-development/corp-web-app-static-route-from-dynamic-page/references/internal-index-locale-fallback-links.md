# corp-web-app internal index locale fallback links

Use when maintaining `src/app/[locale]/internal` index links.

## Problem shape

Some internal child pages exist only for English even though the internal index is locale-scoped. If the index filters by `hrefByLocale[locale]`, KO/JA users cannot discover those English-only pages. If the index blindly builds `/ko/internal/...` or `/ja/internal/...`, it can surface known 404s.

## Proven handling

1. Verify the route matrix against stage/current behavior when in doubt.
2. For fully localized routes, keep locale-specific links, for example:
   - `/en/internal/sample-article`
   - `/ko/internal/sample-article`
   - `/ja/internal/sample-article`
3. For English-only routes where KO/JA currently 404, expose cards from every locale index but point every locale to the English route:
   - `plans` -> `/en/internal/plans`
   - `usage` -> `/en/internal/usage`
   - `key-values` -> `/en/internal/key-values`
   - `risks` -> `/en/internal/risks`
   - `main-feature-description` -> `/en/internal/main-feature-description`
   - `killer-features` -> `/en/internal/killer-features`
   - `compare-table` -> `/en/internal/compare-table`
4. Keep explicitly removed index labels removed if the user asked for removal, even if the underlying route remains live.

## Test expectations

Add or update tests so they assert both sides of the contract:

- KO/JA index data includes English-only cards with `/en/internal/...` hrefs.
- The index data does not include known missing localized hrefs such as `/ko/internal/usage`, `/ja/internal/usage`, `/ko/internal/plans`, or `/ja/internal/plans`.
- Removed labels like `MDX Preview`, `Live MDX editor`, and language-selector labels stay absent if that was the requested cleanup.
