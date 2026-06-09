# corp-web-japan news publication addition notes

Use this reference when adding a new local `src/content/news/*.mdx` record.

## Observed workflow

1. Start from latest `main` in a repo-root `.worktrees/<branch>` worktree.
2. Load repo-local publication skills when present:
   - `.agents/skills/mdx-publication-operations/SKILL.md`
   - `.agents/skills/news-posting/SKILL.md`
3. Put the article source at `src/content/news/<id>-<slug>.mdx`.
4. Put all post-specific assets under `public/news/<id>/...`.
5. Use `heroImageSrc: "/news/<id>/thumbnail.png"` and keep a real thumbnail file at `public/news/<id>/thumbnail.png`.
6. When porting a news item from `../corp-web-app`, check whether the source frontmatter separates an SVG hero (`heroImageSrc`) from a PNG Open Graph image (`openGraphImageSrc`). The current `corp-web-japan` news loader does not parse `openGraphImageSrc`; use the prepared PNG as the effective `heroImageSrc` so list cards and metadata previews stay raster-safe. Copying the SVG alongside the PNG is optional for source/reference parity, but do not author unsupported `openGraphImageSrc` unless the local loader contract changes.
7. When adding a new numeric news id, update `tests/news/imported-corpus.test.mjs` `expectedIds` so the local corpus guard includes the new record.
8. Run the lightest relevant verification: `npm run test -- tests/news-seo-and-sitemap.test.mjs`.

## Pitfalls

- The news corpus test can fail even when the article renders correctly if the new id is not added to `expectedIds`. Treat that as a content-corpus contract update, not as an implementation bug.
- `npm run test -- tests/news-seo-and-sitemap.test.mjs` is routed through `scripts/ci/run-node-tests.mjs` and may execute broader grouped publication/form/routing/static/assets/cross-cutting tests, not only the named file. If adjacent grouped tests fail because they encode the news corpus contract, treat them as relevant to the content addition.
