---
name: corp-web-japan-origin-main-worktree-safety
description: Safely implement corp-web-japan changes from the latest origin/main when local main is dirty or behind, and avoid accidentally reverting recently merged metadata/title updates.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [corp-web-japan, git, worktree, safety, metadata, seo]
    related_skills: [github-pr-workflow, test-driven-development]
---

# corp-web-japan: safe worktree workflow from origin/main

Use this when working in `corp-web-japan`, especially for page metadata / SEO / route work where a stale local branch can silently overwrite recent merged changes.

## Why this skill exists

In this repo, local `main` may be:
- behind `origin/main`
- carrying unrelated untracked files
- different from the latest merged PR state

If you inspect files on local `main` first and then patch a fresh worktree later, you can accidentally revert recent merged changes such as finalized page titles.

## When to use

Use this workflow when:
- the user asks for implementation work in `corp-web-japan`
- local `main` is dirty or behind origin
- the task touches metadata, SEO, routing, titles, canonical tags, robots, sitemap, or page-level copy that may have changed in recent PRs

## Safe workflow

1. Check current repo state first.

```bash
git branch --show-current
git status -sb
git worktree list
gh pr list --state open --limit 30
```

2. If local `main` is dirty or behind, do NOT edit there.

3. Fetch and create a fresh worktree from `origin/main`.

```bash
git fetch origin main --quiet
git worktree add .worktrees/<branch-name> -b <branch-name> origin/main
```

Example:

```bash
git worktree add .worktrees/fix-issue-62-seo-baseline -b fix/issue-62-seo-baseline origin/main
```

4. Re-read the actual files from the new worktree before patching.
- Do not rely on earlier reads from local `main`.
- This is mandatory if recent PRs may have touched the same files.

5. Preserve latest merged content exactly unless the user asked to change it.
- Titles and branding labels are especially easy to regress.
- If a recent PR finalized labels/titles, keep them untouched while adding new metadata fields.

6. For metadata / SEO work, add a failing test first.
- Prefer a small repository-level regression test that checks file contents or metadata patterns.
- Then implement the minimum code to satisfy the test.

## Recommended test approach for SEO baseline work

Add a small node test under `tests/` that verifies:
- `layout.tsx` defines `metadataBase`
- `robots.ts` includes sitemap and host
- page files contain canonical paths for intended public routes
- `sitemap.ts` includes only real public routes
- routes that currently `notFound()` are excluded from the sitemap

This catches path drift such as `/whitepaper` vs `/whitepapers` and prevents accidental sitemap entries for non-live pages.

## Practical lessons from issue #62 work

- The correct public whitepaper index path is `/whitepapers`, not `/whitepaper`.
- If `/events` currently renders `notFound()`, exclude it from sitemap until the route is actually live.
- Use a shared site URL helper so `metadataBase`, canonical generation, robots, and sitemap stay aligned.

## Verification

Run:

```bash
npm install
node --test tests/<new-seo-test>.test.mjs
npm run test:ci
npm run build
```

Notes:
- In a freshly created worktree, install dependencies before relying on `npm run test:ci`. If `eslint` is missing or `node_modules/.bin/eslint` does not exist, run `npm install` in that worktree first.
- If build shows a Next.js warning about multiple lockfiles because of the worktree, that is not itself a build failure.
- What matters is whether the build succeeds and the generated routes match the intended public surface.

## Pitfalls

- Reading local `main`, then editing a separate worktree without re-reading files there
- Forgetting that a new worktree may not have dependencies installed yet, which can make `npm run test:ci` fail early with `sh: eslint: command not found`
- Accidentally replacing finalized page titles while adding canonical metadata
- Hardcoding outdated route names into sitemap/canonical
- Including routes in sitemap that currently return `notFound()`

## Done criteria

- All edits are based on latest `origin/main`
- Recent merged title/copy changes remain intact
- canonical/robots/sitemap are internally consistent
- regression test passes
- `npm run test:ci` and `npm run build` pass
