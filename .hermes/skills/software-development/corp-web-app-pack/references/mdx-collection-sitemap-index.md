# MDX collection sitemap index rollout

Use this when replacing one-off sitemap augmentation with collection-level sitemap endpoints in `corp-web-app`.

## Pattern

1. Keep `/sitemap.xml` as a sitemap index, not a giant generated urlset.
   - Include `/sitemap/legacy.xml` for the existing Blob-backed public sitemap.
   - Include only child sitemaps whose collection routes are already public, not still under `/<locale>/t/*` verification prefixes.
2. Preserve legacy sitemap behavior by moving the old Blob fetch/namespace handling into a reusable legacy helper.
   - `/sitemap/legacy.xml` should return the original XML content.
   - Keep bot-vs-browser `xhtml` namespace handling with the legacy endpoint, not the index.
3. Add concrete App Router route files for each child sitemap rather than relying on a dotted dynamic segment when simple static route files are enough:
   - `src/app/sitemap/news.xml/route.ts`
   - `src/app/sitemap/blog.xml/route.ts`
   - etc.
4. Put shared XML serialization and route handlers under `src/lib/sitemap/**`.
   - XML escaping and dedupe should live in a generic helper.
   - Child route files should be thin wrappers around a factory such as `createMdxSitemapRouteHandler(collectionKey)`.
5. Use repository route-candidate APIs as the source of truth for collection URLs.
   - Include list routes and URL-accessible detail routes.
   - Exclude `redirectUrl` and `noindex` records.
   - Do not exclude `hidden` solely because it is hidden from list pages when the detail route remains publicly URL-accessible.
6. Do not include privacy-policy in the collection sitemap index; it is an MDX-backed document family but not a sitemap target.
7. If latest `main` contains a narrower one-off helper such as news-only Blob sitemap augmentation, replace it with the broader collection sitemap structure instead of keeping both.
   - Remove obsolete helper files/tests that only append one collection into the legacy urlset.
   - Preserve their covered behavior in the new collection registry/source tests.

## Test pattern

Add lightweight Vitest source tests before implementation:

- XML serializer test:
  - dedupes duplicate locs
  - escapes `&`, `<`, etc.
  - serializes sitemap index entries
- Collection registry test:
  - asserts exact collection key order and endpoint paths
  - asserts representative public route candidates include list/detail URLs
  - asserts `/t/` preview/verification routes are excluded
  - asserts a concrete App Router endpoint file exists for every registered collection plus `/sitemap/legacy.xml`

CI grouping pitfall: when adding new tests under a new subtree such as `src/lib/sitemap/__tests__/`, update `scripts/ci/test-groups.mjs` in the same PR. Otherwise `npm run test:smoke` / CI fails with `Unassigned test files` even if the focused Vitest command passes. Sitemap registry/helper tests belong in the `publications` group because they validate MDX/resource publication URL exposure.

Example verification command:

```bash
npm exec vitest -- run src/lib/sitemap/__tests__/xml.test.ts src/lib/sitemap/__tests__/mdx-collections.test.ts
```

## CI follow-up: index exposure vs endpoint registry

When CI/review catches `/sitemap.xml` exposing verification-only publication families, do not delete the child route endpoints or collapse the registry back to news-only.

Use a two-list model instead:

- Keep a complete child endpoint registry, for example `mdxSitemapCollections`, so every implemented `/sitemap/<collection>.xml` route remains covered by registry tests and can be enabled later without recreating files.
- Add an index-exposure filter/list, for example `mdxSitemapIndexCollections`, that contains only child sitemaps whose URLs are already public and should be discoverable from `/sitemap.xml`.
- Represent the switch explicitly with a field such as `includeInSitemapIndex: true`; avoid relying on collection-key name checks spread through the route handler.
- In the current rollout pattern, `news` may be index-exposed while families still served under `/<locale>/t/*` preview/verification routes should remain absent from `/sitemap.xml` until public route rollout.
- Keep tests separate: endpoint/registry coverage can assert every concrete route file exists, while sitemap-index tests assert only index-exposed child sitemap URLs appear.

## Rebase pitfall

When rebasing over a just-merged PR that added one-off sitemap behavior, expect conflicts in `src/app/sitemap.xml/route.ts`. Resolve toward the sitemap-index architecture:

- `/sitemap.xml` returns `<sitemapindex>` only.
- `/sitemap/legacy.xml` owns the original Blob sitemap.
- `/sitemap/<collection>.xml` owns repo-local collection URLs.
- Delete obsolete one-off append helpers/tests after confirming equivalent coverage in the collection tests.
