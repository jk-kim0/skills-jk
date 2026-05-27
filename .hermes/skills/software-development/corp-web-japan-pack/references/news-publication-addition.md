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
6. When adding a new numeric news id, update `tests/news/imported-corpus.test.mjs` `expectedIds` so the local corpus guard includes the new record.
7. Run the lightest relevant verification: `npm run test -- tests/news-seo-and-sitemap.test.mjs`.

## Pitfall

The news corpus test can fail even when the article renders correctly if the new id is not added to `expectedIds`. Treat that as a content-corpus contract update, not as an implementation bug.
