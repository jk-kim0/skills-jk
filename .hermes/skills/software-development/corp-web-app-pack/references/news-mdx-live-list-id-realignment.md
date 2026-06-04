# News MDX live-list id realignment

Use this reference when migrating or correcting `src/content/news` records in `corp-web-app` from the live `querypie.com/{ko,en,ja}/company/news` lists.

## Durable lessons

1. Treat news `id` as the default ordering contract unless the task explicitly asks for a custom sort.
   - `createResourceCollectionRepository` defaults to `Number(right.id) - Number(left.id)`.
   - If live/date order and id order differ, prefer reassigning news IDs/assets/routes so id-desc order equals date-desc order.
   - Do not leave a compensating date sort in `src/lib/resources/news.ts` when the requested outcome is id realignment.

2. Preserve article identity across locales, but do not force a locale file when the live list does not expose that article.
   - Example shape from the live-list audit: KO can have 20 visible records while EN/JA have 14.
   - Translation/internal availability pages should represent missing locale entries as missing, not fabricate or fallback them.

3. Scope automated replacements narrowly.
   - Only rewrite `src/content/news/**`, news-specific tests, news route samples, and explicitly related blog redirect files.
   - Avoid broad `src/**` replacements for `/news/<id>/...`; they can corrupt unrelated blog/events/whitepaper/demo route tests, UI snippets, or content examples that happen to contain `/news/`.

4. When moving IDs, move all three contracts together:
   - filename prefix: `src/content/news/<id>-<slug>.<locale>.mdx`
   - frontmatter: `id`, `heroImageSrc`, `relatedIds`, and any inline `/news/<id>/<slug>` links
   - assets: `public/news/<id>/thumbnail.png` and any inline article images such as `image-1.png`

5. Verify before committing:
   - locale counts match live lists (for the audited state: KO 20, EN 14, JA 14)
   - no duplicate `(id, locale)` pairs
   - every `heroImageSrc` exists under `public/`
   - for every locale, `id` descending order equals parsed date descending order
   - no placeholder artifacts remain (for example `__IDMAP`, `__tmp`, `21__`)
   - targeted Vitest suite passes for news migration, blog redirect migration, news public route, internal translations/news, middleware, and internal tailwind sample URLs

## Safe implementation pattern

Use a constrained script or manual patches that operate only on known files. If scripting:

- Build an explicit `id_map`.
- Move public asset directories through a temporary directory to avoid overwriting collisions.
- Move MDX files through temporary filenames before writing final filenames.
- Use single-pass regex replacement functions; avoid iterative replacement that cascades `10 -> 11 -> 12`.
- Keep a fixed allowlist for non-news files, such as:
  - `src/content/blog/23-querypie-payroll-partnership.*.mdx`
  - `src/content/blog/25-terrasky-mitoco-buddy.*.mdx`
  - `src/content/blog/26-mitoco-buddy-release.*.mdx`
  - `src/lib/resources/__tests__/news-migration.test.ts`
  - `src/lib/resources/__tests__/blog-migration.test.ts`
  - `src/__tests__/app/[locale]/news-public-route.test.tsx`
  - `src/__tests__/app/[locale]/internal/translations/news/page.test.tsx`
  - `src/__tests__/middleware.test.ts`
  - `src/app/(tailwind)/[locale]/internal/tailwind/tailwind-pages.ts`
  - `src/__tests__/app/[locale]/internal/tailwind/page.test.tsx`

## Pitfalls seen in practice

- Broad `/news/<id>/` replacement across `src/**` can mutate unrelated tests and components.
- Placeholder-based mapping can leave artifacts like `21__` if placeholders are not fully normalized.
- Inline article images can move to the wrong ID directory if old IDs are reused for a different record. Re-check `ArticleFileImage filepath="public/news/<id>/image-*.png"` references separately.
- Blog migration tests may contain blog IDs and news redirect URLs in the same file; update only the news redirect URLs, not blog detail IDs.
