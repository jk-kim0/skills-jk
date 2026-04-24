---
name: corp-web-v2-blog-mdx-migration
description: Migrate blog MDX content from corp-web-contents into corp-web-v2, including required public assets and legacy link rewrites, then verify with tests and PR workflow.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# corp-web-v2 blog MDX migration

Use when the task is to move blog content from `../corp-web-contents/` into `corp-web-v2`.

## When this skill applies

- Source repo: `../corp-web-contents`
- Target repo: `corp-web-v2`
- Target content path: `src/content/mdx/blog/`
- Content already exists in authored metadata under `src/content/documentation/blogs/**/meta.json`, and the missing piece is MDX bodies/assets

## Key findings

1. Blog source files live at:
   - `../corp-web-contents/pages/features/documentation/blog/<id>/<slug>/<locale>/content.mdx`
2. Existing `corp-web-v2` blog MDX files are stored as:
   - `src/content/mdx/blog/<id>/<locale>.mdx`
3. Public listing/detail pages are driven by authored content metadata under:
   - `src/content/documentation/blogs/**/meta.json`
   - so this migration usually does **not** require editing content-state or authored meta files if the entries already exist.
4. Migrated MDX often references assets outside `public/blog`, especially some Japanese posts using `public/news/news-20.png` and `public/news/news-21.png`.
5. Legacy internal links in source MDX may point to:
   - `/features/documentation/blog/<id>/<slug>`
   - malformed variants like `/features/documentation/<id>/<slug>`
   These should be rewritten to locale-specific MDX routes:
   - `/<locale>/blog/<id>`
6. For long-term asset hygiene, blog assets can be reorganized from flat `public/blog/*` into per-post directories:
   - `public/blog/<id>/thumbnail.<ext>` for the post thumbnail
   - `public/blog/<id>/<image-name>.<ext>` for inline images
7. Most generic inline names like `blogNN-image-1.png` are inherited from `corp-web-contents/public/blog`, not invented during migration. Before renaming them semantically, extract evidence from:
   - image `alt`
   - image `caption`
   - nearby MDX headings/paragraphs
   - and only rename high-confidence cases first
8. Some posts have enough evidence for semantic renames (for example captioned UI screenshots), while others only have weak generic alt text like `Demonstration` or `QueryPie PM`; keep those generic until stronger evidence exists.

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
- authored blog entries already present in `src/content/documentation/blogs`

Useful checks:

```bash
git status -sb
env -u GITHUB_TOKEN gh pr list --state open --limit 20
find src/content/documentation/blogs -name meta.json
```

### 3. Copy MDX files from source to target layout

For each source file:
- source: `../corp-web-contents/pages/features/documentation/blog/<id>/<slug>/<locale>/content.mdx`
- target: `src/content/mdx/blog/<id>/<locale>.mdx`

Important:
- preserve only locales that actually exist in source
- do not invent missing locale files
- ensure files end with a trailing newline

### 4. Rewrite legacy internal blog links

Rewrite these patterns inside migrated MDX:

- `/<locale>/features/documentation/blog/<id>/<slug>` -> `/<locale>/blog/<id>`
- `/features/documentation/blog/<id>/<slug>` -> `/<file-locale>/blog/<id>`
- `/features/documentation/<id>/<slug>` -> `/<file-locale>/blog/<id>`

Reason:
- source MDX links use old documentation URLs
- target MDX route is the locale-specific `/blog/[id]` route

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
- no remaining `/features/documentation/blog/` or `/features/documentation/` legacy links in migrated MDX
- no missing `public/...` asset refs used by migrated MDX
- no stale flat `public/blog/b-thumb-*` refs after reorganizing assets
- only intended files changed
- survey document exists if semantic renaming was performed

### 8. Run project verification

From the worktree:

```bash
npm install   # if node_modules absent
npm run test:run
npm run typecheck
```

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
