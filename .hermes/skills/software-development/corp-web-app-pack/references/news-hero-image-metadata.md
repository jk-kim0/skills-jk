# News hero image metadata pattern

Use this when improving `corp-web-app` news metadata for `/<locale>/news` or `/<locale>/news/:id/:slug`.

## Source shape

- News MDX records expose `heroImageSrc` through `newsPublicationRepository` and through list items returned by `listNewsPublicationItems(locale)`.
- Public news route files currently live under `src/app/(tailwind)/[locale]/news/**`.
- Locale list pages (`page.en.tsx`, `page.ko.tsx`, `page.ja.tsx`) export static `metadata` objects, so the representative Open Graph image can be computed from `listNewsPublicationItems(Locale.X)[0]?.imageSrc` at module scope.
- Detail metadata can use the resolved `detail.post.heroImageSrc` from `newsPublicationRepository.getDetail(...)`.

## Implementation pattern

For list pages:

1. Keep existing `title`, `description`, and `alternates.canonical` intact.
2. Add locale-specific representative image:
   - `const englishNewsOpenGraphImage = listNewsPublicationItems(Locale.EN)[0]?.imageSrc;`
   - Use the matching locale for KO/JA.
3. Add `openGraph` with:
   - `title`, `description`, `url`, `type: 'website'`
   - `images: image ? [{ url: image, width: 1280, height: 720, alt: title }] : []`
4. Add `twitter` with:
   - `card: 'summary_large_image'`
   - same title/description
   - `images: image ? [image] : []`

For detail pages:

1. Resolve `title` and `canonical` once so Open Graph/Twitter stay aligned with primary metadata.
2. Add `openGraph.type: 'article'`.
3. Use `detail.post.heroImageSrc` for both Open Graph and Twitter images.
4. Use `detail.post.title` as the Open Graph image alt text.

## Verification

Add or update a focused Vitest contract under `src/__tests__/app/[locale]/news/metadata.test.ts` that imports route `generateMetadata` functions directly and asserts:

- `/<locale>/news` metadata uses `listNewsPublicationItems(locale)[0].imageSrc` in Open Graph and Twitter.
- Detail metadata uses `newsPublicationRepository.list({ locale })[0].heroImageSrc` in Open Graph and Twitter.

Run the lightest check:

```bash
npm exec vitest -- run 'src/__tests__/app/[locale]/news/metadata.test.ts'
```

## Pitfalls

- Do not start a local dev server for this metadata-only change unless explicitly requested.
- Do not alter canonical, sitemap, redirect, or navigation behavior while only improving metadata response.
- Prefer focused metadata contract tests over broad build/test runs for this narrow surface.
- Do not use `.svg` assets for `heroImageSrc` when that field feeds Open Graph/Twitter preview images. Social preview crawlers may ignore SVG even when the page emits valid `og:image` tags and the SVG URL returns 200. Convert to a raster asset such as `.png`, `.jpg`, `.jpeg`, or `.webp`, then update the MDX frontmatter.
- When validating news Open Graph hero paths, allow both locale-agnostic and locale-specific shapes. Valid examples include `/news/25/thumbnail.png`, `/news/25/thumbnail.ko.png`, and `/ko/news/25/thumbnail.png`; the key contract is that the referenced `public/**` file exists and the extension is Open Graph preview-compatible.
- If the current branch's PR is already closed or merged, do not push follow-up fixes to that branch. Create a fresh worktree/branch from latest `origin/main`, reapply the scoped changes there, then open a new PR.
- When a social preview appears broken, first distinguish "metadata tag missing" from "image asset unsuitable": fetch the live HTML with crawler user agents and inspect `og:image`, `twitter:image`, dimensions, and the image response headers.
- Avoid using SVG as a news `heroImageSrc` when that value is used for Open Graph/Twitter previews. Many social/link preview crawlers expect raster images and may ignore `image/svg+xml` even when the URL returns 200. Prefer a 1200x630 PNG/JPEG asset under `public/news/<id>/thumbnail.png` or `.jpg`, update every locale MDX for the logical item, and add/adjust tests so preview images do not regress to SVG-only assets.
- If `metadataBase` or framework behavior converts `og:image` to an absolute URL but `og:url` remains relative, treat that as a metadata quality issue to fix separately; it is not the same root cause as a crawler ignoring an SVG image.
