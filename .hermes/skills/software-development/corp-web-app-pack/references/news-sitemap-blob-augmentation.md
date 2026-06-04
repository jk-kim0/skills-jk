# News sitemap augmentation for Blob-backed sitemap.xml

Use this when `corp-web-app` needs repo-local publication URLs added to the public `sitemap.xml` while the route still serves the Blob Storage `public/sitemap.xml` file.

## Proven pattern

1. Keep `src/app/sitemap.xml/route.ts` as the single public sitemap endpoint.
2. Fetch the existing Blob sitemap through the existing `FileQuery` path first.
3. Preserve the Blob XML, including XML declaration and namespace handling.
4. Build repo-local publication routes from the family repository contract, e.g. `newsPublicationRepository.getPublicRouteCandidates({ locales: [Locale.EN, Locale.KO, Locale.JA] })`.
5. Convert candidates to absolute `<loc>` values using the sitemap's first existing `<loc>` origin when available; fall back to `getBaseUrl()` only when the source sitemap has no origin.
6. Dedupe against existing `<loc>` entries before appending.
7. Insert new `<url>` nodes immediately before `</urlset>`.
8. Rely on the repository's public candidate filter so `redirect`, `noindex`, and `/t/*` verification routes stay excluded. Do not treat `hidden` as a sitemap exclusion when the detail URL is still directly accessible; `hidden` only removes the item from list pages.

## Test placement

Avoid putting Vitest files under a dotted route directory such as `src/app/sitemap.xml/route.test.ts`; Vitest may not discover it reliably. Put tests under a normal path such as:

`src/__tests__/app/sitemap-xml-route.test.ts`

Do not export test-only helpers from `src/app/sitemap.xml/route.ts`. Next.js App Router route modules allow only route-compatible exports, and `next build` can fail with `"<helperName>" is not a valid Route export field`. Put deterministic sitemap helper logic in a normal library module such as `src/lib/resources/news/sitemap.ts`, import it from the route, and import that library helper in tests.

## Targeted verification

Run the minimal relevant checks from the worktree root:

```bash
npm exec prettier -- --write src/app/sitemap.xml/route.ts src/__tests__/app/sitemap-xml-route.test.ts
npm exec vitest -- run src/__tests__/app/sitemap-xml-route.test.ts src/lib/resources/__tests__/news-migration.test.ts
```

This verifies the sitemap insertion behavior and the news repository visibility contract without starting a dev server or running a full build.
