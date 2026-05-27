# Route-Local Authoring Wiki and i18n Status Docs

Use when updating corp-web-app GitHub wiki pages such as `Route-Local-Authoring` and `Route-Local-Authoring-i18n`.

## Source-of-truth order

1. Refresh the main checkout to latest `origin/main` before scanning.
2. Pull the wiki repo separately (`corp-web-app.wiki.git`), but do not edit wiki files in the product repo.
3. Read `Route-Local-Authoring.md` first; `Route-Local-Authoring-i18n.md` must use that page's endpoint list as its baseline.
4. Scan current code, not stale wiki prose:
   - `git ls-files 'src/app/**/page.tsx' 'src/app/**/route.ts'`
   - `src/middleware.ts` for default English rewrites
   - `src/lib/preview-navigation.ts` for preview route mappings
   - `src/content/**` for document/publication records such as privacy policy

## Route-Local-Authoring updates

Keep the document concise and Korean by default for corp-web-app wiki.

Capture:
- latest `origin/main` SHA, commit time, commit title;
- public/locale route-local pages;
- archived static routes;
- `/[locale]/t/*` preview/rollout candidates;
- explicit exclusions: publication/detail families, API, internal demo routes, dynamic fallback, search, redirect/proxy-only handlers;
- recent main changes that affect the status.

Important learned examples:
- After PR #777, public `src/app/[locale]/key-values/**` is removed; remaining `key-values` is internal-only and should not appear as public backlog.
- After PR #778, unprefixed `src/app/archived/**` wrappers are removed; `/archived/**` survives via middleware default-English rewrite, not wrapper pages.
- After PR #779, `src/app/[locale]/pricing/route.ts` is redirect-only to `/[locale]/plans`; do not document it as a route-local content page.

Do not create or modify `_Sidebar.md` unless the user explicitly asks for a custom sidebar. A custom sidebar suppresses GitHub wiki's automatic page list.

## Route-Local-Authoring-i18n updates

Purpose: check whether each endpoint listed in `Route-Local-Authoring` has real English, Korean, and Japanese content.

Required table shape:

```md
| Endpoint | English | Korean | Japanese |
| --- | --- | --- | --- |
```

Do not add `성격`, `범위`, or other status taxonomy columns unless the user asks.

Status labels:
- `✅ 준비됨`: locale file/content record exists and actual text is primarily that language.
- `⚠️ 부분/혼재`: file exists but English/other-language text remains significant, or some records are missing.
- `❌ 미준비(영문 중심)`: file exists but actual visible text is English-centered.
- `❌ 파일 없음`: expected locale file/content record is absent.
- `— 해당 없음`: redirect-only endpoint or other route with no page content.

Do not trust file existence alone. Inspect actual visible text in `page.en.tsx`, `page.ko.tsx`, and `page.ja.tsx`. If Korean/Japanese pages mostly reuse English copy, mark them not ready or mixed.

For privacy policy preview routes, judge content records under `src/content/privacy-policy/*.mdx`, not the preview route file alone. Latest version can be complete while historical version routes are mixed if a version such as `2024-09-30` exists only for Korean.

## Practical text-language heuristic

A quick audit script can extract quoted strings and JSX text from locale files and compare character classes:
- English: `[A-Za-z]`
- Korean: `[가-힣]`
- Japanese: kana `[ぁ-んァ-ン]` plus CJK only when kana is present

Use the heuristic as a first pass, then sanity-check edge cases manually. Product names, component names, CSS tokens, and metadata fields inflate English counts, so statuses near the boundary should be reviewed by sample text.

## Commit/push

Commit directly in the wiki repo and push `master`. Verify with:

```bash
git status --short --branch
git log -1 --oneline
git ls-remote origin refs/heads/master
```
