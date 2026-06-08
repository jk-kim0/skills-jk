# News hero image metadata pattern

Use this when improving `corp-web-app` news metadata for `/<locale>/news` or `/<locale>/news/:id/:slug`.

## Source shape

- News MDX records expose `heroImageSrc` and optional `openGraphImageSrc` through `newsPublicationRepository` and through list items returned by `listNewsPublicationItems(locale)`.
- Public news route files currently live under `src/app/(tailwind)/[locale]/news/**`.
- Locale list pages (`page.en.tsx`, `page.ko.tsx`, `page.ja.tsx`) export static `metadata` objects, so the representative Open Graph image can be computed at module scope from the latest list item as `item?.openGraphImageSrc ?? item?.imageSrc`.
- Detail metadata should use `detail.post.openGraphImageSrc ?? detail.post.heroImageSrc` from `newsPublicationRepository.getDetail(...)`.

## Implementation pattern

For list pages:

1. Keep existing `title`, `description`, and `alternates.canonical` intact.
2. Resolve the locale-specific representative image from the latest list item:
   - `const latestNewsItem = listNewsPublicationItems(Locale.EN)[0];`
   - `const englishNewsOpenGraphImage = latestNewsItem?.openGraphImageSrc ?? latestNewsItem?.imageSrc;`
   - Use the matching locale and variable name for KO/JA.
3. Add `openGraph` with:
   - `title`, `description`, `url`, `type: 'website'`
   - `images: image ? [{ url: image, width: 1280, height: 720, alt: title }] : []`
4. Add `twitter` with:
   - `card: 'summary_large_image'`
   - same title/description
   - `images: image ? [image] : []`

For detail pages:

1. Resolve `title` and `canonical` once so Open Graph/Twitter stay aligned with primary metadata.
2. Resolve `const openGraphImageSrc = detail.post.openGraphImageSrc ?? detail.post.heroImageSrc;`.
3. Add `openGraph.type: 'article'`.
4. Use `openGraphImageSrc` for both Open Graph and Twitter images.
5. Use `detail.post.title` as the Open Graph image alt text.

## Authoring and validation contract

- `openGraphImageSrc` is the explicit preview-image frontmatter field. If it is present, metadata must use it before the hero image.
- If `openGraphImageSrc` is absent, metadata falls back to `heroImageSrc`.
- Metadata generation should not validate the extension of either field; it should emit metadata based on the authored frontmatter value.
- Preparing a `.png` Open Graph preview image is an authoring requirement, not a metadata rendering responsibility.
- Asset validation should enforce that the effective preview image (`openGraphImageSrc ?? heroImageSrc`) exists under `public/**` and is `.png`.
- `heroImageSrc` may remain non-PNG, including `.svg`, when a separate `.png` `openGraphImageSrc` is authored for social previews.

## Verification

Add or update focused Vitest contracts under `src/__tests__/app/[locale]/news/metadata.test.ts` that import route `generateMetadata` functions directly and assert:

- `/<locale>/news` metadata uses `listNewsPublicationItems(locale)[0].openGraphImageSrc ?? listNewsPublicationItems(locale)[0].imageSrc` in Open Graph and Twitter.
- Detail metadata uses `record.openGraphImageSrc ?? record.heroImageSrc` in Open Graph and Twitter.
- A record with SVG `heroImageSrc` and PNG `openGraphImageSrc` emits the PNG URL in Open Graph and Twitter metadata.

Also keep or add asset-validation tests that fail when the effective preview image is not `.png`, while allowing SVG heroes that have a PNG `openGraphImageSrc`.

Run the lightest check:

```bash
npm exec vitest -- run 'src/__tests__/app/[locale]/news/metadata.test.ts'
```

When the change touches shared publication validation, also run the focused resource tests:

```bash
npm test -- --run src/__tests__/app/[locale]/news/metadata.test.ts src/lib/resources/__tests__/news-migration.test.ts src/lib/resources/__tests__/publication-repository.test.ts src/lib/resources/__tests__/resource-list.test.ts
```

## Pitfalls

- Do not start a local dev server for this metadata-only change unless explicitly requested.
- Do not alter canonical, sitemap, redirect, or navigation behavior while only improving metadata response.
- Prefer focused metadata contract tests over broad build/test runs for route-only metadata behavior.
- If the change adds or tightens a shared list-item type such as `ResourceListItem`, do not rely only on focused news metadata tests. Search for direct `ResourceListItem` object creation and all `imageSrc: item.heroImageSrc` / translation aggregate mappers, then run `npm run build` or another production typecheck before pushing. Next.js production build can catch stale mappers outside the news route, such as legacy demo hub, tutorials publication records, blog translation aggregates, and resource-list test fixtures.
- Do not "fix" a non-PNG hero by forcing the page/card hero to PNG if the intended design uses another format. Add a PNG `openGraphImageSrc` and let metadata use that field.
- Do not put extension checks in `generateMetadata`; that hides authoring problems at render time and makes metadata behavior diverge from frontmatter. Keep format enforcement in asset validation and authoring docs.
- When validating news Open Graph preview paths, allow both locale-agnostic and locale-specific shapes. Valid examples include `/news/25/thumbnail.png`, `/news/25/thumbnail.ko.png`, and `/ko/news/25/thumbnail.png`; the key contract is that the effective preview image exists and is `.png`.
- If the current branch's PR is already closed or merged, do not push follow-up fixes to that branch. Create a fresh worktree/branch from latest `origin/main`, reapply the scoped changes there, then open a new PR.
- When a social preview appears broken, first distinguish "metadata tag missing" from "image asset unsuitable": fetch the live HTML with crawler user agents and inspect `og:image`, `twitter:image`, dimensions, and the image response headers.
- If `metadataBase` or framework behavior converts `og:image` to an absolute URL but `og:url` remains relative, treat that as a metadata quality issue to fix separately; it is not the same root cause as a crawler ignoring an unsuitable image asset.
