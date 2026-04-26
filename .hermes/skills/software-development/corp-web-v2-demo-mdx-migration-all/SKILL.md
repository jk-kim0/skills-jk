---
name: corp-web-v2-demo-mdx-migration-all
description: Migrate remaining corp-web-v2 demo categories from corp-web-contents into MDX-backed short routes, normalize per-entry assets, preserve CMS-managed list/admin flows where needed, and finish with PR + wiki updates.
---

# When to use

Use this when the user wants `corp-web-v2` demo detail content migrated from `corp-web-contents/pages/features/demo/**` into MDX-backed public routes for categories beyond ACP, especially when they want:

1. short canonical routes like `/demo/aip/:id/:slug`, `/demo/use-cases/:id/:slug`, `/webinars/:id/:slug`
2. rendering similar to blog / white-paper
3. normalized inline image / OG image asset paths under `public/demo/<segment>/<id>/...`
4. `/features/demo` list, homepage demo links, and sitemap aligned with the new MDX catalog
5. the migration comparison wiki updated after implementation

Important: treat redirect requirements as optional and explicitly scope-checked. In follow-up work on this migration, the user chose to keep canonical short routes but remove newly added legacy redirect behavior from the PR. Do not assume redirects belong in the same PR as the MDX migration unless the user explicitly wants them.

# Preconditions

1. Start from fresh latest `origin/main` in a fresh worktree / branch.
2. Read repo guidance and current patterns first:
   - `README.md`
   - `next.config.ts`
   - `src/features/content/config.ts`
   - `src/constants/navigation.ts`
3. Inspect existing MDX rendering patterns:
   - `src/app/[locale]/blog/[id]/[[...rest]]/page.tsx`
   - `src/app/[locale]/white-paper/[id]/[[...rest]]/page.tsx`
   - `src/features/mdx/loader.ts`
   - `src/features/mdx/types.ts`
4. Inspect the current demo entry points:
   - `src/app/[locale]/features/demo/page.tsx`
   - `src/app/[locale]/features/demo/[slug]/page.tsx`
   - `src/app/sitemap.ts`
5. In this repo, worktree-local dependencies matter. If build errors look suspicious, run `npm install` inside the worktree before trusting them.

# Key findings from the successful migration

1. For full demo MDX migration, do not keep AIP/use-case/webinar as managed detail pages. Instead, treat them like blog/white-paper-style authored MDX detail content.
2. Keep existing CMS-managed demo admin/list infrastructure intact if the task is only about public detail rendering. Do not modify CMS-connected pages such as `src/app/[locale]/features/demo/page.tsx` or `src/app/[locale]/features/demo/[slug]/page.tsx` unless the user explicitly approves changing managed demo list/detail behavior. Public MDX routes should be added alongside that flow, not by silently replacing it.
3. A single shared demo catalog/helper layer is better than one helper per category once multiple categories are MDX-backed.
4. inline/OG asset normalization is critical. The reliable pattern is `public/demo/<segment>/<id>/...`.
5. Thumbnail asset names should also be normalized during migration or follow-up cleanup:
   - locale-agnostic thumbnail: `thumbnail.<ext>`
   - locale-specific thumbnails: `thumbnail-en.<ext>`, `thumbnail-ko.<ext>`, `thumbnail-ja.<ext>`
   - if multiple locales intentionally share the same underlying image, keep the shared asset on the owning locale filename (for example `en` + `ja` both using `thumbnail-en.png`) rather than fabricating a duplicate locale file.
6. Source analysis must be content-reference-based, not just file-name search. Legacy MDX uses mixed patterns like markdown images, raw `<img>`, `ArticleFileImage`, and `public/...` references.
7. Source availability may be incomplete. In this migration, `webinars` source existed only for ids `1..26`, so `27` had to remain unmapped and documented in the wiki.
8. Information architecture and migration scope are separate decisions. Earlier migration work kept webinars under `/demo/webinar/:id/:slug` as a pragmatic intermediate choice, but the follow-up implementation settled the canonical public webinar detail route on `/webinars/:id/:slug`. Treat `/demo/webinar/:id/:slug` as legacy redirect-only if present, and keep any larger IA move beyond that out of scope unless the user explicitly asks for it.
9. Use-case canonical public detail routes ultimately settled on plural `/demo/use-cases/:id/:slug`, not singular `/demo/use-case/:id/:slug`. Keep list/detail prefix naming aligned on the public site.

# Implementation pattern

## 1) Audit source availability and reference patterns first

Inspect source under:

- `~/workspace/corp-web-contents/pages/features/demo/aip-features/**`
- `~/workspace/corp-web-contents/pages/features/demo/use-cases/**`
- `~/workspace/corp-web-contents/pages/features/demo/webinars/**`
- `~/workspace/corp-web-contents/public/**`

Check for:

- frontmatter fields (`title`, `description`, `ogImage`, `relatedPosts`, etc.)
- locale availability per id
- image reference styles:
  - markdown `![]()`
  - raw `<img>`
  - `ArticleFileImage`
  - `public/demo/...`, `public/customer-success-cases/...`, `public/webinar/...`, `public/tutorial/...`
- slug uniqueness assumptions

Do not assume every legacy numbered item has source content. Generate an explicit availability table first.

## 2) Build a shared demo catalog instead of category-specific ad hoc helpers

Create a shared file such as:

- `src/features/demo/catalog.ts`

Recommended responsibilities:

- define all MDX-backed demo entries across `acp`, `aip`, `use-case`, `webinar`
- store `{ segment, legacyCategory, id, slug, locales, sourcePath, canonicalHref }`
- expose helpers like:
  - `getDemoMdxEntry(segment, id)`
  - `getDemoMdxEntryByCategoryAndId(legacyCategory, id)`
  - `getDemoMdxHref(locale, segment, id)`
  - `getDemoMdxHrefByCategoryAndId(locale, legacyCategory, id)`
  - `getVisibleDemoMdxEntries(locale)`
  - `getLatestPublicDemoEntry(locale, legacyCategory)`

Why this matters:

- it avoids repeating logic for AIP/use-case/webinar/ACP
- it centralizes locale visibility, canonical href generation, and redirect behavior
- it makes list page, homepage card, sitemap, and wiki counts consistent

## 3) Add a shared page renderer; add redirect helpers only if the user explicitly wants them

Create helpers such as:

- `src/features/demo/page.tsx`
- optional: `src/features/demo/legacyRedirect.ts`

The shared page renderer should:

1. validate locale
2. resolve entry from catalog by segment + id
3. load `demo` MDX source from `src/content/mdx/demo/<segment>/<id>/<locale>.mdx`
4. fall back through the existing demo MDX loader locale logic when needed
5. render with the standard MDX render pipeline and `BlogLayout`
6. emit metadata canonical to the short route

Important follow-up lesson:

- Do not automatically redirect slug-missing or slug-mismatched requests just because you can compute a canonical URL. In the successful follow-up, the user explicitly removed page-level canonical redirect behavior from the PR even after it had been implemented.
- Keep route resolution able to compute canonical info, but gate actual redirect behavior behind explicit product scope.

If redirect behavior is explicitly in scope, the shared legacy redirect helper should:

- map legacy category + id to the canonical short route
- return 404 for unknown ids
- use `NextResponse.redirect(new URL(href, request.url))`

## 4) Add one canonical page route per segment

Create:

- `src/app/[locale]/demo/acp/[id]/[[...rest]]/page.tsx`
- `src/app/[locale]/demo/aip/[id]/[[...rest]]/page.tsx`
- `src/app/[locale]/demo/use-cases/[id]/[[...rest]]/page.tsx`
- `src/app/[locale]/webinars/[id]/[[...rest]]/page.tsx`

Each can be a thin wrapper around the shared page helper.

Important route-design lessons:

- use-case detail routes use plural `/demo/use-cases/:id/:slug` so list/detail prefixes stay aligned on the public site
- webinar detail routes use the top-level plural prefix `/webinars/:id/:slug` to align list/detail naming
- only add `/:id` -> `/:id/:slug` redirect behavior when the user explicitly includes canonical redirect scope in the PR
- `en` locale should remain prefixless, consistent with the repo’s route behavior

## 5) Add legacy numbered redirects as route handlers only when redirect scope is approved

If the user explicitly wants redirect coverage in the same PR, create redirect-only `route.ts` files for:

- `src/app/[locale]/features/demo/acp-features/[id]/[[...rest]]/route.ts`
- `src/app/[locale]/features/demo/aip-features/[id]/[[...rest]]/route.ts`
- `src/app/[locale]/features/demo/use-cases/[id]/[[...rest]]/route.ts`
- `src/app/[locale]/features/demo/webinars/[id]/[[...rest]]/route.ts`

Do not use `page.tsx` for a route that only redirects.

If the user later narrows scope and excludes redirect work, remove any newly added redirect helpers/routes from the branch rather than keeping them as “nice to have” behavior.

## 6) Generate MDX and normalized assets programmatically

For large migrations, script the conversion instead of hand-editing dozens of entries.

Target content layout:

- `src/content/mdx/demo/acp/<id>/<locale>.mdx`
- `src/content/mdx/demo/aip/<id>/<locale>.mdx`
- `src/content/mdx/demo/use-cases/<id>/<locale>.mdx`
- `src/content/mdx/demo/webinars/<id>/<locale>.mdx`

Important follow-up lesson:

- keep MDX source directory naming aligned with the actual app URI naming and catalog `mdxSlug`
- do not leave singular internal source folders like `use-case` or `webinar` once the public route has settled on plural `use-cases` or `webinars`
- after any route naming change, update the MDX directory names, catalog `segment`, catalog `mdxSlug`, and loader tests together

Target asset layout:

- `public/demo/acp/<id>/...`
- `public/demo/aip/<id>/...`
- `public/demo/use-cases/<id>/...`
- `public/demo/webinar/<id>/...`

Recommended generated frontmatter fields:

- `layout: "Article"`
- `category: "demo"`
- `title`
- `description`
- `date`
- `ogImage`
- `hideHeroImage: true`
- preserve any safe, actually-used fields supported by the repo MDX pipeline

Conversion rules learned from this migration:

- rewrite legacy asset refs into normalized per-entry public paths
- rewrite legacy `/features/demo/...` related links into short canonical routes
- verify there are no leftover legacy paths inside migrated MDX after generation
- if locale source is missing, do not invent it; let loader fallback behavior or catalog visibility handle it explicitly

## 7) Switch public consumers carefully; do not silently replace CMS-managed pages

Safe update targets:

- `src/app/[locale]/page.tsx`
- `src/app/sitemap.ts`
- public-only helper files such as `src/features/demo/public.ts`

Recommended behavior:

- homepage latest use-case card may come from the new MDX catalog if the user wants homepage links aligned to canonical routes
- sitemap should emit demo entries from the MDX catalog directly
- do not rely on old managed `readContentState("demo")` detail URLs for migrated categories where public canonical routes are now MDX-backed

Important scope guardrails:

- do not modify `src/app/[locale]/features/demo/page.tsx` unless the user explicitly approves changing the managed `/features/demo` list behavior
- do not modify `src/app/[locale]/features/demo/[slug]/page.tsx` or admin demo pages for this migration
- if you temporarily changed any CMS-managed list/detail file while experimenting, revert it before finalizing the PR

## 8) Tests and verification

Add focused tests around the shared catalog/helpers, for example:

- `src/features/demo/catalog.test.ts`
- keep/update `src/features/demo/acp.test.ts` if ACP remains as compatibility coverage
- `src/features/mdx/loader.test.ts` for demo category loading and fallback

Useful checks:

- mapping lookup by segment and legacy category
- canonical href generation
- locale visibility filtering, especially entries missing `en`
- old legacy `/features/demo/...` links removed from migrated MDX
- if redirects are in scope, cover slug-missing or slug-wrong redirect behavior with tests; if redirects are out of scope, assert canonical info without redirect side effects

Run at least:

- `npm run test:run -- src/features/demo/catalog.test.ts src/features/demo/acp.test.ts src/features/mdx/loader.test.ts`
- `npm run build`

If build fails due to missing worktree-local dependencies, run `npm install` inside the worktree and retry before diagnosing code.

## 9) PR workflow

1. stage only intended files
2. commit with a focused message such as:
   - `feat: demo 콘텐츠를 MDX short route로 이관`
3. push branch
4. create Draft PR
5. prefer `gh pr create --body-file ...` over inline `--body` when route literals/backticks are present
6. monitor CI until all checks pass

In this repo, final completion should include a reviewable PR URL and green CI.

## 10) Wiki update workflow

After PR is pushed, update the wiki comparison page:

- `querypie-com-Demo-Content-Migration-Comparison-Table`

Update:

1. top summary counts
2. per-category completion counts
3. each row’s new-site path to the canonical short route
4. notes explaining redirect status only if redirect behavior is actually part of the approved PR scope
5. any genuinely missing source item, with explicit explanation rather than guessing

When the user explicitly excludes redirect work from the PR, the wiki and PR description should say that canonical routes were introduced without new legacy redirect coverage in this batch.

Use the wiki git repo as the write target, commit, and push there separately.

# Pitfalls

- Do not assume webinar/use-case legacy numbering or locale coverage is complete.
- Do not trust worktree build failures until you confirm local dependencies are installed in that worktree.
- Do not leave migrated MDX with stale `/features/demo/...` links or raw `public/...` references.
- Do not keep route-only redirects as `page.tsx`; use `route.ts`.
- Do not overcouple this migration to CMS-managed detail rendering if the user asked for MDX-backed public detail pages.
- When editing many wiki rows, script the replacements; manual edits are error-prone.

# Verification checklist

- `/demo/aip/1/google-oauth-demo` renders
- `/demo/use-cases/1/allganize-changsu-lee` renders
- `/webinars/17/findy-querypie-mcp-webinar` renders
- if redirects are in scope: `/demo/aip/1` redirects to the canonical slug path and legacy numbered paths redirect to the short canonical route
- if redirects are out of scope: no newly introduced redirect-only routes/helpers remain in the branch, and slug-missing access does not perform unintended auto-redirects
- `/features/demo` list page uses migrated MDX-backed entries
- homepage latest use-case card points to `/demo/use-cases/...`
- sitemap emits short demo routes
- no migrated MDX files still contain `/features/demo/` links
- targeted tests pass
- `npm run build` passes
- PR is open and CI is green
- wiki summary and row paths reflect the migrated state
