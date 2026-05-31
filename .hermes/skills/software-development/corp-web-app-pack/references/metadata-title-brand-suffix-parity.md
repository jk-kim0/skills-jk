# Metadata Title Brand Suffix Parity

Use when reviewing or changing `metadata.title`, `openGraph.title`, or social titles in `corp-web-app`, especially when the page was migrated from or compared against `corp-web-japan`.

## Review pattern

1. Inspect the PR diff for the specific metadata fields being changed.
2. Find the corresponding implementation in `corp-web-japan` when the task asks for parity or the route was migrated from the Japan site.
3. Compare all relevant title surfaces, not just `metadata.title`:
   - `metadata.title`
   - `openGraph.title`
   - `twitter.title` if present in the source implementation
   - actual deployed `<title>` / `og:title` when a live reference URL exists
4. Apply the current `corp-web-app` default before choosing a source-site pattern:
   - For the time being, `corp-web-app` should default to `Page Title | QueryPie` for ordinary page metadata titles.
   - Use the same `| QueryPie` suffix for `metadata.title`, `openGraph.title`, and `twitter.title` when those surfaces are present, unless a page family has a more specific documented rule.
   - Treat `corp-web-japan`'s common `Page Title | QueryPie AI` pattern as source-site evidence, not as the default for `corp-web-app`.
   - Use `| QueryPie AI` only when the user explicitly asks for exact Japan-site parity or a documented page-family/product policy requires it.
5. For ordinary subpages, prefer `Page Title | Brand` over `Brand: Page Title` unless the source implementation or brand policy intentionally uses a slogan/product-title form.

## Session-derived example

PR 716 changed the Japanese certifications page title from `認証` to `QueryPie AI: 認証`. Evidence found during review:

- `corp-web-contents/pages/company/certifications/ja/meta.json` used `QueryPie AI: 認証`.
- `corp-web-japan/src/app/certifications/page.tsx` used `認証 | QueryPie AI` for `metadata.title`, `openGraph.title`, and `twitter.title`.
- Live `https://querypie.ai/certifications` rendered `<title>認証 | QueryPie AI</title>` and `og:title=認証 | QueryPie AI`.
- Many newer `corp-web-app` Tailwind/publication routes use `Page Title | QueryPie`.
- `QueryPie AI: ...` matched homepage/slogan-style titles more than ordinary subpage metadata.

Current recommendation for `corp-web-app`:

> Use `認証 | QueryPie` by default for `corp-web-app` metadata title surfaces. Mention that `認証 | QueryPie AI` is the closest Japan-site parity form, but do not choose it over `| QueryPie` unless the user explicitly prioritizes exact `corp-web-japan` parity or a page-family policy requires `QueryPie AI`.
