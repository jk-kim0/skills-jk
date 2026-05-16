---
name: corp-web-app-static-page-route-local-migration
description: Migrate or maintain corp-web-app static/semistatic pages as route-local App Router pages, preserving legacy source provenance, locale-specific authoring, route-aligned assets, and existing PR workflow.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-app, nextjs, app-router, static-page, route-local-authoring, migration, provenance]
---

# corp-web-app Static Page Route-Local Migration

Use this skill when migrating, relocating, or maintaining a static/semistatic corp-web-app marketing page as route-local App Router files, especially pages that came from legacy `corp-web-contents` / historical `contents/**` sources.

## Triggers

- User asks to migrate a static page into `src/app/**` route-local files.
- User asks to change the public route of an already migrated static page.
- User asks to move page-specific `public/**` assets into a route-aligned location.
- User asks to document migration source/provenance for a migrated page.
- User asks to add a lightweight index/list page for migrated static routes, such as `/archived` or locale-prefixed archived pages.
- Existing PR follow-up for a route-local static page in corp-web-app.

For follow-up work on an open PR, also load `existing-pr-followup-worktree`.
If the referenced PR is already merged or closed, do not revive its branch; start a new branch and PR from latest `origin/main`.

## Core workflow

1. Confirm repository and PR state.
   - Run `pwd`, `git rev-parse --show-toplevel`, `git status --short --branch`.
   - If this is PR follow-up, check `gh pr view <number> --json state,headRefName,headRefOid,baseRefName`.
   - Use a fresh worktree or an isolated detached worktree at the PR branch head when the branch is already checked out elsewhere.
2. Locate legacy source provenance before editing.
   - Search current tree first.
   - If source is no longer present, search historical paths:
     `git log --all --name-only --pretty=format: | sed '/^$/d' | sort -u | grep -Ei '<page-slug>|<asset-name>'`
   - Inspect candidate historical files with `git show <rev>:<path>`.
3. Implement route-local authoring.
   - Keep `page.tsx` thin: metadata handoff, locale selection/fallback, wrapper call.
   - Put real locale copy and section order in `page.en.tsx`, `page.ko.tsx`, and `page.ja.tsx` when those locales exist.
   - Use small route-local adapters or `src/components/**` only for UI/rendering details, not hidden page copy registries.
4. Align public assets with the route.
   - Move page-specific images under a route-aligned root such as `public/<route-family>/<page>/...` or the exact path requested by the user.
   - Preserve subfolders that have meaning, e.g. `benefits/`.
   - Do not accidentally move shared form/UI assets such as `public/partners/form/*` unless explicitly requested.
5. Update metadata and tests.
   - Update canonical URLs, Open Graph/Twitter image URLs, and alternate locale URLs to match the final public route.
   - Update/import tests to target the route-local files after relocation.
   - Prefer targeted Vitest checks for the changed route.
6. Rebase and push.
   - Before updating the PR branch, rebase onto latest `origin/main` when the PR branch is behind.
   - Use `--force-with-lease` for rewritten PR follow-up branches.
   - Verify remote head with `git ls-remote origin refs/heads/<branch>` and report CI status without long passive waits.

## Locale dynamic route relocation

When consolidating explicit locale directories such as `src/app/en/**`, `src/app/ko/**`, and `src/app/ja/**` into a dynamic `src/app/[locale]/**` route, preserve the unprefixed default public route as a thin EN wrapper unless the user explicitly asks to change public URL policy. Move the real authored pages to `page.en.tsx`, `page.ko.tsx`, and `page.ja.tsx` under the `[locale]` route and add a thin locale dispatcher at `page.tsx`.

Important pitfall: do not leave the old explicit locale route files in place if the goal is a real relocation. In Next.js App Router, explicit static segments can continue to handle `/en/...`, `/ko/...`, and `/ja/...` instead of the new `[locale]` route. See `references/locale-dynamic-route-relocation.md` for the contact-us review pattern and verification notes.

## Migration README requirement

When a static page migration may need future corrections, add a colocated `README.md` next to `page.en.tsx` / `page.ko.tsx` / `page.ja.tsx`.

The README should include:

- current public route(s), including localized routes;
- current implementation files and responsibilities;
- original migration source paths for each locale;
- historical asset source paths;
- useful commit(s) for `git show <rev>:<path>` inspection;
- concise migration method, including component-name substitutions or adapter usage;
- asset mapping from old public paths to new route-aligned public paths;
- explicit exclusions for similarly named shared assets that were not moved;
- follow-up checklist for future edits.

See `references/become-a-partner-archived-route-readme.md` for a concrete pattern from PR 671.

## Pitfalls

- Lightweight index/list pages still need explicit route-local styling. In corp-web-app, the root layout already wraps children in `src/components/layout/main`; adding another `<main>` inside a route-local index can become a flex child that shrinks to content width. Also, global CSS resets plain `a` and `ul` styles, so plain links/lists can look like unclickable text unless styled. See `references/archived-index-route.md`.
- Do not infer that all similarly named assets are page-specific. Verify whether assets are shared by unrelated form/layout flows before moving them.
- Do not silently normalize a user-specified route spelling. If the user asks for `/archived/become-a-parter`, preserve that spelling unless they correct it.
- Do not leave old imports, canonical URLs, or OG image URLs pointing at the pre-migration route or asset path.
- Do not use `python` blindly on macOS; this user's environment may only have `python3`.
- When a PR branch is already checked out in another worktree, a detached fresh worktree at `origin/<branch>` is acceptable for follow-up work; push `HEAD:<branch>` with force-with-lease after rebase.

## Verification

Minimum checks:

- `git status --short --branch`
- search for old route and asset references after relocation
- targeted test, e.g. `npm run test:run -- src/__tests__/app/<route-test>.test.tsx`
- `git ls-remote origin refs/heads/<branch>` after push
- `gh pr view <number> --json statusCheckRollup,headRefOid,mergeStateStatus`
