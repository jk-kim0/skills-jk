# News MDX localized translation additions and count-test updates

Use this when adding missing EN/JA/KO MDX translation files for an existing `src/content/news/<id>-<slug>.<locale>.mdx` record in `corp-web-app`.

## Pattern

1. Start from latest `origin/main` in a branch-isolated worktree.
2. Load the repo-local `.agents/skills/mdx-publication-operations/SKILL.md` and `.agents/skills/news-posting/SKILL.md` before editing.
3. Copy the existing source-locale frontmatter contract exactly unless the content model intentionally changes:
   - same `id`, `slug`, `date`, `heroImageSrc`, `author`, `newsType`, `relatedIds`, `hidden`, `redirectUrl`, `gated`, `noindex`
   - only localize `title`, `description`, and body copy unless explicitly requested otherwise
4. Add collection-flat files directly under `src/content/news/`:
   - `src/content/news/<id>-<slug>.en.mdx`
   - `src/content/news/<id>-<slug>.ja.mdx`
   - or the requested missing locale(s)
5. Preserve MDX components and route-aligned asset references exactly unless the user asks for asset work:
   - keep `<ArticleFileImage filepath="public/news/<id>/..." />`, `<EmailLink />`, `<Box />`, inline JSX, and relative article links structurally valid
   - translate human-facing headings, body copy, alt text, captions, and locale-specific article links
6. If the added records are visible (`hidden: false`), update `src/lib/resources/__tests__/news-migration.test.ts` count expectations:
   - `newsPublicationRepository.records` total increases by the number of added MDX files
   - locale-specific `list({ locale })` counts increase only for added visible locale files
   - distinct ID count normally stays unchanged when adding translations for an existing ID
7. If tests currently assert the requested locale detail is `not-found`, change it to `found` and add translated body marker assertions for major sections. For Korean press-release translations, durable markers include `## 추천사`, `## 회사 개요`, `## 문의처`, `## QueryPie AI 대표 코멘트`, and preserved components such as `Email: <EmailLink email="pr@querypie.com" />`.
8. Run `git diff --check` and a lightweight source-level count/frontmatter check before committing. A simple Python scan over `src/content/news/*.mdx` can verify total records, distinct IDs, per-locale file counts, and per-locale visible counts.
9. For this user’s repo-work preference, do not run local build/test unless explicitly requested; commit/push and rely on PR CI after source-level verification.

## Pitfalls

- Do not rebase with unstaged changes; either commit first and then `git fetch origin main && git rebase origin/main`, or stash only if preservation by branch/worktree is not appropriate.
- Do not change public routes, navigation, sitemap, canonical behavior, or redirects when the request is only to add localized news MDX.
- Do not use customer-facing copy that mentions internal file-format terms such as `MDX`.
- Do not leave locale-specific detail tests at `not-found` after adding the corresponding locale file; this hides exposure regressions even when list counts are updated.
- Do not translate only plain prose and forget MDX-adjacent human-facing strings such as image `alt`, image `caption`, right-aligned attribution labels, and same-site article links.
