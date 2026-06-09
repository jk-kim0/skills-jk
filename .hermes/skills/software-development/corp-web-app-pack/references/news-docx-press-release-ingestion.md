# News DOCX press-release ingestion

Use this reference when adding a `src/content/news/**` press-release MDX record from a source `.docx` file, especially Korean launch/announcement copy that should match an existing repo news pattern such as `26-lingo-launch.ko.mdx`.

## Workflow

1. Load `.agents/skills/mdx-publication-operations/SKILL.md` and `.agents/skills/news-posting/SKILL.md`, then inspect a nearby same-family example before writing the new MDX.
   - For product launch press releases, `src/content/news/26-lingo-launch.ko.mdx` is a useful current shape: frontmatter, centered italic subtitle deck, body copy, optional `<ArticleFileImage>`, then the standard `docs/news.md` company/media-contact block.
2. Extract DOCX text from `word/document.xml`, preserving paragraph order and line breaks. Use the source prose, but normalize press-release markdown shape:
   - frontmatter with `newsType: press-release`, `author: querypie`, `hidden: false`, `redirectUrl: null`, `gated: false`, `noindex: false`;
   - a centered `<Box center>` subtitle deck for the source subheadline bullets;
   - `## QueryPie 회사소개` / `## 미디어 문의` copied from `docs/news.md`, not hand-rewritten from the DOCX footer.
3. Extract images from `word/media/*` and inspect `word/_rels/document.xml.rels` plus `word/document.xml` image references in document order.
   - A first image before the title is often a document header/logo and should not automatically become a news asset.
   - A 1280×720 image immediately after title/subtitle is a good `hero-<locale>.png` candidate.
   - Later in-body screenshots should be copied as descriptive filenames such as `notepie-screenshot.png` and inserted with `<ArticleFileImage filepath="public/news/<id>/<file>.png" alt="..." />` at the corresponding body location.
   - For review follow-up, prove image provenance with deterministic metadata rather than visual memory: extract candidate DOCX images to `/tmp`, compare SHA-256, dimensions, and byte size against `public/news/<id>/hero-<locale>.png`, and report which `word/media/imageN.*` matches exactly.
4. Use the next numeric news id from `src/content/news`. For a source available only in Korean, add only `<id>-<slug>.ko.mdx` unless translation is explicitly requested.
5. Place assets under `public/news/<id>/`. Keep `heroImageSrc` pointing at an existing preview-compatible raster path such as `/news/<id>/hero-ko.png`.
6. Update `src/lib/resources/__tests__/news-migration.test.ts` counts:
   - unique id count;
   - total record count;
   - locale-specific list count for the locale added.


## Localization pattern

When the DOCX source is Korean but the task asks for all public locales:

- keep the same id and slug across `ko`, `en`, and `ja` MDX siblings;
- translate the press-release body while keeping product names and frontmatter contracts stable;
- use language-specific company/about and media-contact boilerplate from `docs/news.md`;
- if localized raster assets are not provided, sharing the same hero/body screenshot across locale MDX files is acceptable as long as every referenced path exists and alt text is localized;
- update unique-id, total-record, and locale-list counts according to the actual locale files added.

CI/source-contract pitfall: publication CI can fail in unrelated source-shape tests after a push. Read the exact failing assertion before changing product code. If a source-contract test looks for a marker in a route `page.tsx` but the implementation has legitimately moved the marked JSX into a split component file, update the test to inspect the component that owns the marker rather than reverting the component split.

## Verification

Prefer fast source-level checks unless the user explicitly asks for local build/test:

- enumerate `src/content/news/*.mdx` to verify file count, unique id count, and max id;
- assert the new MDX contains required frontmatter, `newsType: press-release`, `heroImageSrc`, standard company/media-contact headings, and `EmailLink`;
- assert every referenced asset exists under `public/news/<id>/` and has non-zero size;
- run `git diff --check` before commit.

## Pitfalls

- Do not expose the internal file format term `MDX` in customer-facing press-release copy.
- Do not blindly use every DOCX image. Map image placement to document semantics first.
- Do not copy the DOCX footer company/media-contact text verbatim when `docs/news.md` provides the current canonical block.
- If automated patch tooling runs broad TypeScript checks and reports pre-existing dependency/type-resolution errors, do not treat that as content verification failure; continue with targeted source-level validation unless the change actually introduced the error.