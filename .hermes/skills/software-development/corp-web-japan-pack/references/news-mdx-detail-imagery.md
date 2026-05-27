# News MDX detail imagery notes

Use this when adding or adjusting `src/content/news/*.mdx` posts in `corp-web-japan`.

## Detail hero suppression

Although older news wrapper docs may only list `sourceLabel` as news-specific frontmatter, the shared standard publication post loader supports `hideHeroImageOnDetail: true` for standard publication posts. Add it to a news record when the list thumbnail should remain available via `heroImageSrc`, but the detail page should start directly with the MDX body instead of rendering the large 16:9 hero block.

Example:

```yaml
heroImageSrc: "/news/15/thumbnail.png"
hideHeroImageOnDetail: true
sourceLabel: "プレスリリース"
```

## Inline body image sizing and border overrides

`ArticleFileImage` images inherit global publication-body styles that add rounded corners, a light gray border, and `max-w-full`. For logo-like press-release images that should render at the source/display size instead of stretching visually, set `imageClassName` on that one MDX image rather than changing shared renderer CSS.

Example for a 450px-wide logo image from the source article:

```mdx
<Box center>
    <ArticleFileImage
        filepath="public/news/<id>/image-1.png"
        alt="Buddyロゴ"
        caption=""
        imageClassName="mx-auto h-auto w-[450px] max-w-full !border-0 !rounded-none"
    />
</Box>
```

This keeps narrow screens safe (`max-w-full`), avoids the default gray border/rounded corners, and prevents logo assets from filling the full article column.

## Verification

For content-only news changes, the light check remains:

```bash
npm run test -- tests/news-seo-and-sitemap.test.mjs
```
