# News MDX live company-news parity

Use this when converting or reconciling `src/content/news/*.mdx` against the live `/<locale>/company/news` pages in `corp-web-app`.

## Durable workflow

1. Treat the live company-news pages as locale-specific editorial surfaces, not as a guaranteed 1:1 translated collection.
   - KO may expose more items than EN/JA.
   - Some EN/JA items may intentionally have no KO equivalent.
   - KO can contain two separate cards for the same external announcement/topic, for example a Korean media article plus an English wire item.
2. Extract live cards structurally from rendered HTML when possible:
   - `<li data-testid="company-news-item">`
   - card `href`
   - first `<p>` as display date
   - `<h2>` as title
   - second `<p>` as description
   - image `src` such as `/_next/image?url=%2Fnews%2Fnews-20.png...`
3. Do not assign ids solely from visible image numbers when that would make different articles share the same `id` across locales.
   - `id` must identify the same logical article record across available locales.
   - If a locale has a different article occupying a live image-number slot, allocate a distinct id rather than reusing the EN/JA id.
4. Keep list ordering based on article date, then id as a tie-breaker, when ids are reconciled semantically rather than monotonically matching live image numbers.
5. For missing locale variants, let internal translation/coverage tooling show `Missing`; do not force placeholder translated MDX just to keep all locales at the same count.
6. Preserve or update redirect contracts from legacy blog records when moving news ids:
   - hidden blog MDX `redirectUrl` values pointing at `/news/<id>/<slug>` must follow the final news id.
   - inline links inside related blog/news MDX should also be updated.
7. Keep route-aligned assets under `public/news/<id>/thumbnail.png` for MDX detail/list rendering. Copy existing `public/news/news-N.png` live-card assets into id directories when reconciling with live cards.
8. If a news article body uses inline article images, move/copy those into the final id directory and update `ArticleFileImage filepath` references accordingly.

## Verification pattern

- Static content checks:
  - expected locale counts match live pages;
  - no duplicate `(id, locale)` pairs;
  - no missing `heroImageSrc` assets;
  - no stale `/news/<old-id>/...` references in `src/content/news` after id adjustment.
- Targeted tests usually include:
  - `src/lib/resources/__tests__/news-migration.test.ts`
  - `src/lib/resources/__tests__/blog-migration.test.ts`
  - `src/__tests__/app/[locale]/news-public-route.test.tsx`
  - `src/__tests__/app/[locale]/internal/translations/news/page.test.tsx`
  - `src/__tests__/middleware.test.ts`
  - `src/__tests__/app/[locale]/internal/tailwind/page.test.tsx`
- After pushing a PR for this work, check the GitHub rollup against the final head SHA with `gh pr view <pr> --json headRefOid,mergeStateStatus,statusCheckRollup,url`. Report each successful, skipped, or still-blocking check explicitly; do not leave the user with only a generic “CI passed” statement.
## Pitfalls

- Do not assume `id` descending equals newest-first after semantic id reconciliation; use date sorting for list and translation coverage displays.
- Do not make tests require KO content for EN/JA-only live records; assert the internal page marks that locale as missing.
- Do not blindly search-and-replace `toHaveLength(12)` in shared list/load-more tests; many resource list components intentionally render 12 cards before `Load More`.
- Do not rely only on `<a href="/company/news/...">` extraction. The live company-news list often links to external sources and may not contain internal detail URLs.
