---
name: corp-web-v2-blog-mdx-migration
description: Migrate blog or white-paper MDX content from corp-web-contents into corp-web-v2, first verifying what is already on main so you only copy missing content or fix residual migration issues, then verify with tests and PR workflow.
version: 1.1.0
author: Hermes Agent
license: MIT
---

# corp-web-v2 blog/white-paper MDX migration

Use when the task is to move blog or white-paper content from `../corp-web-contents/` into `corp-web-v2`, or to verify whether that migration is already effectively present on `origin/main`.

## When this skill applies

- Source repo: `../corp-web-contents`
- Target repo: `corp-web-v2`
- Target content paths:
  - `src/content/mdx/blog/`
  - `src/content/mdx/white-paper/`
- Content often already exists in authored metadata under:
  - `src/content/documentation/blogs/**/meta.json`
  - `src/content/documentation/white-papers/**/meta.json`
- The remaining work may be either:
  - missing MDX bodies/assets
  - or residual migration defects such as broken internal links in already-migrated MDX

## Key findings

1. Blog source files live at:
   - `../corp-web-contents/pages/features/documentation/blog/<id>/<slug>/<locale>/content.mdx`
2. White-paper source files live at:
   - `../corp-web-contents/pages/features/documentation/white-paper/<id>/<slug>/<locale>/content.mdx`
3. Existing `corp-web-v2` MDX files are stored as:
   - `src/content/mdx/blog/<id>/<locale>.mdx`
   - `src/content/mdx/white-papers/<id>/<locale>.mdx`
4. The original `corp-web-contents` path slug should be preserved explicitly in each migrated MDX frontmatter as `slug: "..."`, shared across EN/KO/JA files for the same content ID.
5. Public listing/detail pages are driven by authored content metadata under:
   - `src/content/documentation/blogs/**/meta.json`
   - `src/content/documentation/white-papers/**/meta.json`
   - so this migration often does **not** require editing content-state or authored meta files if the entries already exist.
5. Before copying anything, compare source/target counts and inspect current target files. In at least one real case, `origin/main` already contained the full blog and white-paper MDX set by count, so the correct action was not a bulk migration but a small repair PR for residual bad links.
6. Migrated MDX may reference assets outside `public/blog`, especially some Japanese posts using `public/news/news-20.png` and `public/news/news-21.png`.
7. Legacy internal links in source or previously migrated MDX may point to:
   - `/features/documentation/blog/<id>/<slug>`
   - `/features/documentation/white-paper/<id>/<slug>`
   - malformed variants such as duplicated locale prefixes like `/ja/ja/...`
   - malformed download/listing links such as `white-paper/<id>download` or category typos like `white-paperss`
8. These links should be rewritten to locale-specific routes supported by the current app, for example:
   - `/<locale>/blog/<id>`
   - `/<locale>/white-paper/<id>`
9. For long-term asset hygiene, blog assets can be reorganized from flat `public/blog/*` into per-post directories:
   - `public/blog/<id>/thumbnail.<ext>` for the post thumbnail
   - `public/blog/<id>/<image-name>.<ext>` for inline images
10. Most generic inline names like `blogNN-image-1.png` are inherited from `corp-web-contents/public/blog`, not invented during migration. Before renaming them semantically, extract evidence from:
   - image `alt`
   - image `caption`
   - nearby MDX headings/paragraphs
   - and only rename high-confidence cases first
11. Some posts have enough evidence for semantic renames (for example captioned UI screenshots), while others only have weak generic alt text like `Demonstration` or `QueryPie PM`; keep those generic until stronger evidence exists.

## Recommended workflow

### 1. Start in a worktree

Follow the repo-local worktree + PR workflow.

- Base from `origin/main`
- Use a dedicated branch like `feat/blog-mdx-migration`
- Create the PR through `.github/workflows/create-pr.yml`, not `gh pr create`

### 2. Verify current repo state before changing files

Check:
- open PRs
- current branch cleanliness
- existing worktrees
- authored blog/white-paper entries already present in `src/content/documentation/**`
- source/target MDX counts before copying any files

Useful checks:

```bash
git status -sb
env -u GITHUB_TOKEN gh pr list --state open --limit 20
find src/content/documentation/blogs -name meta.json
find src/content/documentation/white-papers -name meta.json
find ../corp-web-contents/pages/features/documentation/blog -name content.mdx | wc -l
find ../corp-web-contents/pages/features/documentation/white-paper -name content.mdx | wc -l
find src/content/mdx/blog -name '*.mdx' | wc -l
find src/content/mdx/white-paper -name '*.mdx' | wc -l
```

If counts already match, do not assume the request still requires bulk copying. Inspect a few target files and search for residual bad patterns first; the correct deliverable may be a narrow fix-only PR.

### 3. Copy MDX files from source to target layout when content is actually missing

For each source file:
- blog source: `../corp-web-contents/pages/features/documentation/blog/<id>/<slug>/<locale>/content.mdx`
- blog target: `src/content/mdx/blog/<id>/<locale>.mdx`
- white-paper source: `../corp-web-contents/pages/features/documentation/white-paper/<id>/<slug>/<locale>/content.mdx`
- white-paper target: `src/content/mdx/white-paper/<id>/<locale>.mdx`

Important:
- preserve only locales that actually exist in source
- do not invent missing locale files
- ensure files end with a trailing newline

### 4. Rewrite legacy or malformed internal links

Rewrite these patterns inside migrated MDX when they appear:

Blog examples:
- `/<locale>/features/documentation/blog/<id>/<slug>` -> `/<locale>/blog/<id>`
- `/features/documentation/blog/<id>/<slug>` -> `/<file-locale>/blog/<id>`
- `/features/documentation/<id>/<slug>` -> `/<file-locale>/blog/<id>`

White-paper examples:
- `/<locale>/features/documentation/white-paper/<id>/<slug>` -> `/<locale>/white-paper/<id>`
- `/features/documentation/white-paper/<id>/<slug>` -> `/<file-locale>/white-paper/<id>`
- duplicated locale prefixes like `/ja/ja/features/documentation?...` -> single locale prefix
- malformed download/list links such as `white-paper/<id>download` -> correct route for the intended page or CTA
- category typos like `white-paperss` -> `white-papers`

Reason:
- source MDX links use old documentation URLs
- previously migrated MDX can also contain bad generated link strings
- target MDX routes are the locale-specific `/blog/[id]` and `/white-paper/[id]` routes

### 5. Copy all referenced assets, not just blog images blindly

Scan migrated MDX for `public/...` references and copy the referenced files into `corp-web-v2/public/...`.

At minimum, expect:
- many assets from `../corp-web-contents/public/blog/`
- possibly assets from `../corp-web-contents/public/news/`

Do not assume all assets are under `public/blog`.

### 6. Optional asset reorganization and semantic renaming

If the task includes cleaning up blog assets after migration:

1. Reorganize assets per post:
   - move thumbnail assets to `public/blog/<id>/thumbnail.<ext>`
   - move inline assets to `public/blog/<id>/...`
2. Rewrite all MDX references to the new asset paths.
3. Build a survey before semantic inline-image renaming.
   - Save a markdown reference file under `docs/reference/` containing:
     - current file
     - recommended filename
     - confidence (`high` / `low`)
     - evidence from `alt`, `caption`, and surrounding text
4. Rename only the `high` confidence inline images first.
   - Good examples are captioned diagrams, reports, and UI screenshots where the meaning is explicit.
   - Leave ambiguous images generic for now.

### 7. Verify migrated content integrity

Run checks for:
- no remaining `/features/documentation/blog/` or `/features/documentation/white-paper/` legacy links in migrated MDX
- no malformed doubled locale prefixes like `/ja/ja/`
- no malformed category strings like `white-paperss`
- no missing `public/...` asset refs used by migrated MDX
- no stale flat `public/blog/b-thumb-*` refs after reorganizing assets
- only intended files changed
- survey document exists if semantic renaming was performed
- if the task turned into a fix-only PR, confirm the changed files are restricted to the repaired MDX files

### 8. Run project verification

From the worktree:

```bash
npm install   # if node_modules absent
npm run test:run
npm run typecheck
```

If these fail on a fresh branch in the same way they fail on latest `origin/main`, record them explicitly as pre-existing baseline failures instead of expanding scope automatically. In one real migration/fix PR, both commands failed because of an existing `mermaid` module/type-resolution problem unrelated to the edited MDX files.

### 8. Commit, push, and create PR

- Stage only migrated MDX/assets
- Commit with a focused message, e.g. `feat: migrate blog MDX content from corp-web-contents`
- Push branch
- Trigger PR creation with:

```bash
env -u GITHUB_TOKEN gh workflow run create-pr.yml ...
```

## Verification checklist

- [ ] Worktree branch created from `origin/main`
- [ ] Source blog MDX files copied to `src/content/mdx/blog/<id>/<locale>.mdx`
- [ ] Missing locales were not fabricated
- [ ] Legacy internal blog links rewritten to `/<locale>/blog/<id>`
- [ ] Referenced assets copied from `public/blog` and any other referenced public directories like `public/news`
- [ ] No missing `public/...` references remain in migrated MDX
- [ ] If asset reorganization was requested, assets now live under `public/blog/<id>/...`
- [ ] If thumbnail normalization was requested, thumbnails use `public/blog/<id>/thumbnail.<ext>`
- [ ] If semantic rename work was requested, a survey doc was produced and only high-confidence image names were changed
- [ ] `npm run test:run` passes
- [ ] `npm run typecheck` passes
- [ ] Scope gate checked before PR creation
- [ ] PR opened through repo workflow, not direct `gh pr create`

## Pitfalls

- Do not assume `src/content/state/content-state.json` is the source of truth for these blog entries; this repo reads authored content from `src/content/**/meta.json` through `authored.server.ts`.
- Do not forget non-blog assets referenced by migrated MDX.
- Do not leave old `/features/documentation/blog/...` links inside article bodies.
- Do not semantically rename weak-evidence images just because they are generic; many original assets really are named `blogNN-image-N.png` upstream.
- `gh pr checks` may show no checks while Actions runs are being created; inspect `gh run list` immediately after PR creation.
- In this repo, PR Actions can end in `action_required` with zero jobs; treat that as a workflow/platform state, not automatically as a code failure.
