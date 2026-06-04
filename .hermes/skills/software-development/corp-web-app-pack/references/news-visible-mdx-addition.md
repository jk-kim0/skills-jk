# Visible news MDX addition pattern

Use this when adding a new `src/content/news/*.mdx` entry in `corp-web-app` and the user explicitly asks for it to appear in the news list.

## Pattern

1. Start from latest `origin/main` in a branch-isolated worktree under repo-root `.worktrees/`.
2. Load repo-local `.agents/skills/mdx-publication-operations/SKILL.md` and `.agents/skills/news-posting/SKILL.md` before editing.
3. Inspect the current max numeric news id on latest main and allocate the next id. Re-check if main advanced before final push.
4. Use the collection-flat path:
   - `src/content/news/<id>-<slug>.<locale>.mdx`
   - `public/news/<id>/...` for any assets.
5. If the user supplies only one locale, add only that locale unless they explicitly request translation/localization coverage.
6. For list visibility, set frontmatter explicitly:
   - `newsType: press-release` for press releases
   - `hidden: false`
   - `redirectUrl: null`
   - `gated: false`
   - `noindex: false`
7. If no official thumbnail asset is supplied, create a simple route-aligned SVG under `public/news/<id>/thumbnail.svg` and reference it with `heroImageSrc: /news/<id>/thumbnail.svg`; do not place new post assets under `public/assets/**`.
8. Keep customer-facing article body free of internal file-format terms such as `MDX`.
9. Run lightweight source-level checks only unless the user requested local build/test: verify file existence, frontmatter fields, `hidden: false`, and the hero image path. Then commit, rebase onto latest `origin/main`, push, open PR, and check PR mergeability/check-rollup briefly.

## Pitfalls

- Do not leave a visible news item with `hidden: true`; some existing press-release drafts are hidden, but a user request for list exposure requires `hidden: false`.
- Do not translate a Korean-only news request into EN/JA by default. Locale coverage is a separate scope.
- If rebase is attempted while changes are staged/uncommitted, Git will refuse. Commit first, then fetch/rebase before push.
- Do not run a full local build/test for routine content-only news additions when this user has asked to prefer commit/push first and CI monitoring.