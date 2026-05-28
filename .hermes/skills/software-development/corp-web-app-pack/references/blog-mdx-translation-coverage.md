# Blog MDX translation coverage recovery

Use this reference for `corp-web-app` tasks that ask to find and fill missing blog MDX locale files, especially when using historical `corp-web-contents` material.

## Proven workflow

1. Work from latest `origin/main` in a separate worktree/branch; do not edit the root checkout.
2. Load repo-local publication skills first when available:
   - `.agents/skills/mdx-publication-operations/SKILL.md`
   - `.agents/skills/blog-posting/SKILL.md`
3. Build a locale coverage scan over `src/content/blog/*.mdx` grouped by numeric blog id and expected locales (`en`, `ko`, `ja`). Report the exact missing id/locale pairs before editing.
4. Search historical sources before translating:
   - `docs/inventories/corp-web-contents-document-locale-inventory.md`
   - historical `corp-web-contents` MDX file paths from git history
   - related canonical content families such as `src/content/news/**` when the blog record is a hidden redirect/shadow record.
5. If the user says not to translate manually, leave unfound locale content unfixed and report it as not found. If the user explicitly asks for direct translation after source recovery fails, add translations but keep them scoped to the missing locale files.
6. Preserve frontmatter contract and route-aligned assets:
   - keep `id`, `slug`, `title`, `description`, `date`, `heroImageSrc`, `relatedIds`, and `keywords` shape aligned with sibling locales.
   - use `public/blog/<id>/...` asset paths; do not introduce legacy `public/blog/<filename>` paths.
   - for shadow redirect records, preserve `hidden: true` and `redirectUrl` exactly so they stay out of public lists and redirect to the canonical record.
7. When generating or normalizing translated MDX, protect Markdown links, HTML/JSX tags, and inline hrefs with placeholders before machine-assisted translation. Reinsert placeholders after translation and scan for malformed `<a ...>`, `href=`, or broken Markdown link syntax.
8. Update the publication/resource migration tests to reflect the new record count and locale coverage. On newer `main`, expect the blog migration tests under `src/lib/resources/__tests__/blog-migration.test.ts` rather than the older `src/lib/repo-content/__tests__/...` path.

## Verification pattern

Run the lightest focused checks:

```bash
npx vitest run src/lib/resources/__tests__/blog-migration.test.ts
git diff --check
```

Also run a source scan that verifies:

- every blog id has all expected locales.
- YAML frontmatter parses.
- locale counts match expected EN/KO/JA parity.
- no malformed anchor/href candidates were introduced.
- no legacy `public/blog/<filename>` asset paths exist.

## PR notes

In the PR body, list:

- exact missing locale pairs filled.
- which entries were historical-source recovery versus direct translation, if both occurred.
- any hidden redirect contracts preserved.
- focused verification command results.

Do not close or auto-close related issues from the PR body unless the user explicitly asks.