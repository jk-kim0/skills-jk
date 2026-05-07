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

Critical default for this user:
- Do not merely branch from `origin/main` while leaving local `main` stale without calling that out.
- Before starting new repo work, update from the latest `main` baseline explicitly.
## Safe workflow

0. Treat latest-main discovery as mandatory, not optional.
- Do not plan changes from memory, stale local files, or older worktrees.
- Before proposing an implementation approach, first inspect the latest `main` code and recent commits relevant to the feature area.
- `Starting from origin/main` is not enough by itself; you must also understand what changed on latest `main`.

1. Check current repo state first.

```bash
git branch --show-current
git status -sb
git worktree list
env -u GITHUB_TOKEN gh pr list --state open --limit 30
```

2. Inspect latest `main` before planning.

```bash
git fetch origin main --quiet
git rev-parse origin/main
git log --oneline --decorate -n 20 origin/main
```

Then inspect the actual latest-main versions of the relevant files before deciding the plan, for example:

```bash
git show origin/main:src/app/blog/page.tsx | sed -n '1,220p'
git show origin/main:src/app/blog/[id]/[slug]/page.tsx | sed -n '1,260p'
```

This step is mandatory in fast-moving repos: codebase assumptions can become stale even within a few days.

3. If local `main` is dirty or behind, do NOT edit there.

4. Fetch, re-check the remote tip, and create a fresh worktree from `origin/main`.
4. Fetch and create a fresh worktree from latest `main`.

```bash
git fetch origin main --quiet
git checkout main
git pull --ff-only origin main
git worktree add .worktrees/<branch-name> -b <branch-name> main
```

If local `main` is intentionally left untouched for some exceptional reason, explicitly tell the user and still branch from the fetched latest `origin/main`.

Example:

```bash
git checkout main
git pull --ff-only origin main
git worktree add .worktrees/fix-issue-62-seo-baseline -b fix/issue-62-seo-baseline main
```

4.1 Validate that the new worktree is a real linked checkout before editing.

Do not assume any directory under `.worktrees/` is a valid Git worktree just because it exists. Confirm all of the following:

```bash
git worktree list --porcelain
git -C .worktrees/<branch-name> branch --show-current
git -C .worktrees/<branch-name> rev-parse --show-toplevel
ls -la .worktrees/<branch-name> | sed -n '1,20p'
```

Expected signs of a valid linked worktree:
- it appears in `git worktree list --porcelain`
- `git -C <worktree> branch --show-current` returns the expected branch name
- the directory contains a `.git` file that points to the linked worktree metadata
- `rev-parse --show-toplevel` resolves through the linked checkout normally

If the directory exists but is not registered as a worktree, do not edit there. Remove the stray directory and recreate the worktree properly.

5. Re-read the actual files from the new worktree before patching.

- Keep the worktree directory name flat even if the branch name contains slashes. Use a path like `.worktrees/fix-blog-28-toc-highlight` for branch `fix/blog-28-toc-highlight`.
- Do not derive the worktree directory path mechanically from the branch name with slashes, or you can end up with confusing nested paths like `.worktrees/fix/...` that are easy to misread and mis-target in later tool calls.

5. Re-read the actual files from the new worktree before patching.
- Do not rely on earlier reads from local `main`.
- Do not rely on a high-level memory of repo policy if the latest code shows the implementation has already evolved.
- This is mandatory if recent PRs may have touched the same files.
- Also verify the new worktree really points at the expected base:

```bash
git -C .worktrees/<flat-worktree-name> rev-parse HEAD
git -C .worktrees/<flat-worktree-name> rev-parse origin/main
git -C .worktrees/<flat-worktree-name> merge-base HEAD origin/main
```

For a fresh branch with no new commits yet, these should all match.

5.1 Verify that the checkout is materially complete, not just logically registered.

A practical failure mode in this repo: a path under `.worktrees/` can appear to succeed during `git worktree add`, and `git worktree list --porcelain` can still show the entry, but the actual directory can end up containing only a tiny partial subtree instead of a real checkout.

Minimum filesystem sanity check before editing:

```bash
find .worktrees/<flat-worktree-name> -maxdepth 2 | sed -n '1,30p'
```

You should see a normal repository root shape such as `src/`, `tests/`, `public/`, `package.json`, and the linked `.git` file. If you only see a sparse fragment such as one nested directory or a handful of files, do **not** trust that worktree.

Recovery rule:
- delete that broken directory
- run `git worktree prune`
- recreate the worktree at a clean, flat path outside the repo root when needed, for example `~/workspace/<repo>-<topic>`
- repeat the branch/base checks and the filesystem sanity check before editing

This is safer than trying to salvage a half-populated checkout whose path name happens to match the intended worktree.

5.2 Prefer repo-external flat worktree paths when repo-local `.worktrees/` paths behave strangely.

Practical fallback pattern:

```bash
git worktree add -b <branch-name> ~/workspace/<repo>-<topic> origin/main
```

Then verify with:

```bash
git -C ~/workspace/<repo>-<topic> branch --show-current
git -C ~/workspace/<repo>-<topic> rev-parse --show-toplevel
find ~/workspace/<repo>-<topic> -maxdepth 2 | sed -n '1,30p'
```

Only start editing after those checks pass.

5.3 After recreating a worktree because of this failure mode, discard the bad path entirely.
- Do not keep mixing reads or edits between the broken repo-local path and the replacement worktree.
- Treat the replacement worktree as the only authoritative checkout for the task.

5.4 Also verify the new worktree really points at the expected base:

```bash
git -C .worktrees/<flat-worktree-name> rev-parse HEAD
git -C .worktrees/<flat-worktree-name> rev-parse origin/main
git -C .worktrees/<flat-worktree-name> merge-base HEAD origin/main
```

For a fresh branch with no new commits yet, these should all match.

6. Preserve latest merged content exactly unless the user asked to change it.
- Titles and branding labels are especially easy to regress.
- If a recent PR finalized labels/titles, keep them untouched while adding new metadata fields.

6. For metadata / SEO work, add a failing test first.
- Prefer a small repository-level regression test that checks file contents or metadata patterns.
- Then implement the minimum code to satisfy the test.

## Turning a meaningful dirty root-local change into its own PR

A common cleanup follow-up in this repo is:
- local `main` is behind `origin/main`
- local `main` has one meaningful uncommitted file change
- the user wants that exact change turned into a PR without carrying the stale local `main` state forward

Safe pattern:

1. identify the exact changed file(s) on dirty local `main`
2. create a fresh worktree from latest `origin/main`
3. copy only those file(s) into the fresh worktree
4. verify the diff is limited to the intended file set
5. commit, push, and open the PR from that fresh branch

Example use case:
- a repo-local skill file under `.agents/skills/**` was edited during investigation on dirty local `main`
- the user later wants that skill update submitted as its own PR

Recommended command flow:

```bash
git fetch origin --prune
git worktree add -b docs/<topic> ~/workspace/<repo>-<topic> origin/main
cp /path/to/dirty-main/<file> ~/workspace/<repo>-<topic>/<file>
git -C ~/workspace/<repo>-<topic> diff --stat -- <file>
```

Important rule:
- do not branch directly from the dirty local `main` just because the uncommitted file already exists there
- do not mix unrelated stale local-main state into the PR branch
- treat the dirty local file as a patch source, and the fresh latest-main worktree as the only PR-authoring checkout

## Pre-push rule

Before pushing or updating a PR branch:

```bash
git fetch origin main --quiet
git rebase origin/main
```

Use the latest `main` again as the final integration baseline. Do not skip this just because the branch originally started from latest `main`.

Practical follow-up nuance:
- If you are on a fresh latest-main worktree branch with uncommitted changes, `git rebase origin/main` will fail with `cannot rebase: You have unstaged changes`.
- In that situation, do not stash reflexively.
- First verify whether the branch is still exactly based on the current remote main tip:

Additional PR-head rewrite nuance:
- After a rebase plus squash/soft-reset rewrite, `gh pr view` can briefly lag and still show the old commit list.
- Before assuming the force-push failed, verify the actual remote branch tip directly:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/<pr-branch>
```

- If those SHAs match, the rewritten PR head is already on GitHub even if `gh pr view` has not caught up yet.
- Only rewrite history again if the remote SHA really differs.

```bash
git fetch origin --prune
printf 'HEAD '; git rev-parse HEAD
printf 'origin/main '; git rev-parse origin/main
printf 'merge-base '; git merge-base HEAD origin/main
```

- If all three SHAs match, your branch has not diverged from latest `origin/main`; it is safe to commit the local change directly without doing a redundant pre-commit rebase.
- Then commit, push, and let the normal PR workflow continue.
- Only perform an actual rebase after committing if `origin/main` advanced or those SHAs differ.

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

- Planning from memory or repo policy summaries before checking the latest `main` implementation and recent commits
- Treating `branch created from origin/main` as sufficient, without also reading the latest-main files that define the current behavior
- Reading local `main`, then editing a separate worktree without re-reading files there
- Forgetting that a new worktree may not have dependencies installed yet, which can make `npm run test:ci` fail early with `sh: eslint: command not found`
- When multiple sibling worktrees exist, stale `.next` build output under another worktree can confuse repo-wide ESLint/test runs and produce unexpected `ENOENT` reads against files that no longer exist in that sibling checkout. If `npm run test:ci` fails with an ESLint file-open error pointing into `.worktrees/<other-branch>/.next/...`, remove stale `.next` directories under the affected worktrees and rerun.
- Accidentally replacing finalized page titles while adding canonical metadata
- Hardcoding outdated route names into sitemap/canonical
- Including routes in sitemap that currently return `notFound()`

## Done criteria

- All edits are based on latest `origin/main`
- Recent merged title/copy changes remain intact
- canonical/robots/sitemap are internally consistent
- regression test passes
- `npm run test:ci` and `npm run build` pass
