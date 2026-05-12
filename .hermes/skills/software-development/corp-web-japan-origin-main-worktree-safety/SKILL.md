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

Follow the common `repo-root-worktree-path-policy` skill for worktree location and naming.

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
- recreate the worktree under the repo-root `.worktrees/` directory with a short flat name such as `.worktrees/<topic>`
- repeat the branch/base checks and the filesystem sanity check before editing

This is safer than trying to salvage a half-populated checkout whose path name happens to match the intended worktree.

5.2 Prefer repo-root `.worktrees/<flat-name>` paths, even when recovering from a broken worktree.

Practical fallback pattern:

```bash
git worktree add .worktrees/<topic> -b <branch-name> origin/main
```

Then verify with:

```bash
test -d .worktrees/<topic> && echo exists
git -C .worktrees/<topic> branch --show-current
git -C .worktrees/<topic> rev-parse --show-toplevel
find .worktrees/<topic> -maxdepth 2 | sed -n '1,30p'
```

Important extra lesson:
- do not trust the `git worktree add` success message by itself
- in practice, a worktree creation can appear to succeed yet leave no usable directory at the requested path
- explicitly verify that the target directory now exists before any `read_file`, `patch`, or follow-up shell command
- when scripting the target path, avoid accidentally passing a literal shell variable segment or branch path with slashes into the directory name; prefer a short flat `.worktrees/<topic>` path and verify the final path with `pwd` / `realpath` / `rev-parse --show-toplevel`
- if the directory is missing or the checkout landed under an unintended nested path, remove that bad worktree, prune if needed, and recreate it under `.worktrees/<flat-topic>`

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

## PR granularity for repeated small cleanup work

When many routes need the same tiny cleanup pattern, do **not** default to one PR per page.

Prefer one combined PR when all of the following are true:
- the change is mechanically identical or nearly identical across files
- the risk is low and localized
- the review question is the same for every file
- the user did not explicitly request page-by-page PR splitting

Typical examples:
- removing `Preview` from default export names across multiple `/t/*` route files
- removing preview-only wording from metadata descriptions across a small set of related pages
- aligning a repeated test assertion pattern after a small naming cleanup

Why:
- splitting trivial cleanup into many PRs increases branch/CI/review overhead without improving clarity
- for this user, over-splitting small homogeneous cleanup work is considered a mistake even when each PR is technically correct

Practical rule:
- before creating PRs, classify the work as either:
  1. one repeated cleanup pattern across many files, or
  2. genuinely independent fixes with different reasoning/risk
- choose one PR for case (1)
- only choose separate PRs for case (2), or when the user explicitly asks for separation

Counterexample where splitting is still correct:
- different pages require different implementation strategies, different test repairs, or different production-risk judgments
- the user explicitly wants one worktree/PR per page for rollout or review sequencing

## Multiple remaining issue follow-ups: split into one PR per scope item

When a corp-web-japan issue has already been narrowed to a small set of remaining tasks and the user asks to "proceed with the remaining work" as separate PRs:

1. Treat each remaining issue bullet as its own independent branch/worktree/PR.
2. Create one fresh worktree from latest `main` per item; do not bundle multiple follow-ups into one branch just because they came from the same issue.
3. Keep each PR title/body scoped to the single remaining item, not to the broader historical issue.
4. Before deleting a leftover route-adjacent content file, search not only runtime imports but also:
   - source-based tests under `tests/**`
   - helper aggregators such as `tests/helpers/*`
   - repo docs that intentionally show old anti-pattern examples
5. If the leftover file is only referenced by tests/helpers/docs examples, update those references in the same PR that removes the file.
6. Prefer a source-level verification pass for this cleanup class:
   - targeted `node --test` runs for affected source-based tests
   - diff/stat review to confirm the PR stays limited to the intended route/doc/test surfaces

Practical lesson from issue #128 follow-up:
- A docs-sync follow-up and an AI Crew residue cleanup follow-up looked related conceptually, but the user explicitly wanted separate PRs.
- The correct execution was two worktrees from latest `main`:
  - one doc-only PR updating `docs/code-location-conventions.md`
  - one code cleanup PR removing `src/content/home.ts`, moving the remaining AI Crew constants into `src/app/solutions/ai-crew/page.tsx`, and updating source-based tests/helpers accordingly
- When removing route-adjacent residue like `src/content/home.ts`, the main hidden dependencies were test/helper files (`tests/helpers/static-marketing-page-sources.mjs`, `tests/ai-crew-*.test.mjs`, `tests/launch-readiness-coverage.test.mjs`) rather than runtime imports elsewhere.

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
git worktree add .worktrees/docs-<topic> -b docs/<topic> origin/main
cp /path/to/dirty-main/<file> .worktrees/docs-<topic>/<file>
git -C .worktrees/docs-<topic> diff --stat -- <file>
```

If you later create the PR from a different currently checked out branch (for example from root `main` after cleaning it up), pass the head branch explicitly:

```bash
env -u GITHUB_TOKEN gh pr create \
  --head docs/<topic> \
  --base main \
  --title "docs: ..." \
  --body-file /tmp/pr-body.md
```

Otherwise `gh pr create` can infer the current checkout as the head and fail with `head branch "main" is the same as base branch "main"` even though the intended backup/docs branch was already pushed.

Important rule:
- do not branch directly from the dirty local `main` just because the uncommitted file already exists there
- do not mix unrelated stale local-main state into the PR branch
- treat the dirty local file as a patch source, and the fresh latest-main worktree as the only PR-authoring checkout

### Extra rule for repo-local skills / docs rescued from dirty main

When the preserved change is a repo-local skill or guidance doc under paths such as `.agents/skills/**`, do not assume the backed-up text is still correct verbatim.

Use this validation flow before opening the PR:

1. copy the candidate file(s) into the fresh latest-main worktree
2. inspect the latest implementation/tests that define the documented contract
3. compare the rescued text against the current repo truth
4. keep the useful new guidance, but rewrite any stale route/path/contract details to match latest main before commit

Typical example:
- a rescued skill still says a whitepaper gate flow is `/download`
- latest main has already canonicalized that flow to `/pdf`
- the correct action is not to discard the whole rescued skill update, and not to merge the stale wording unchanged
- instead, salvage the useful behavioral guidance and rewrite the stale contract references to the latest-main truth before creating the PR

Practical rule:
- for rescued skill/doc PRs, validate against current source files and the smallest relevant tests, not just against the old diff alone
- this is especially important for route names, canonical paths, gating flows, helper module paths, and other repo contracts that can drift while local main was stale

## Pre-push rule

Before pushing or updating a PR branch:

```bash
git fetch origin main --quiet
git rebase origin/main
```

Use the latest `main` again as the final integration baseline. Do not skip this just because the branch originally started from latest `main`.

Practical same-session nuance learned from `/t/events` preview work:
- `origin/main` can advance between worktree creation and your first push, even during a short task.
- If a final `git fetch` shows `HEAD`, `origin/main`, and `merge-base` no longer match, rebase **before the first push**, not after opening the PR.
- If that rebase conflicts in a touched route because latest `main` already landed a helper-path cleanup (for example `@/lib/publications/event-publication-records` -> `@/lib/publications/events/records`), keep the latest-main helper/import path and reapply only your intended UI/behavior change on top.
- Heuristic: preserve latest-main structural/path cleanups first, then layer the requested route behavior onto that file. Do not resolve the conflict by reviving the old helper path just because your branch started before the cleanup merged.

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
- If the user wants to avoid a fresh worktree-local install and the parent repo checkout already has a usable `node_modules`, a temporary symlink from the worktree `node_modules` to the parent checkout can be enough to run `npm run test:ci` / `eslint` / `tsc` for verification.
- Important limitation: Next.js Turbopack local builds can reject that symlink with `Symlink [project]/node_modules is invalid, it points out of the filesystem root`. In that case, do not treat the symlink itself as a product bug. For local verification from that symlinked worktree, prefer `next build --webpack` instead of the default Turbopack build path.
- If build shows a Next.js warning about multiple lockfiles because of the worktree, that is not itself a build failure.
- Distinguish PR-caused build failures from existing baseline failures on latest `origin/main`. If `next build --webpack` fails on the known corp-web-japan baseline CSS Modules issue in `src/components/layout/site-header.module.css` (`:root` selector is not pure), record it as an unrelated baseline rather than as a regression from the current PR.
- What matters is whether the build succeeds or, if a known baseline issue blocks it, whether the rewritten PR introduced any new failure beyond that baseline and whether the generated routes/tests still match the intended public surface.

## Pitfalls

- Planning from memory or repo policy summaries before checking the latest `main` implementation and recent commits
- Treating `branch created from origin/main` as sufficient, without also reading the latest-main files that define the current behavior
- Reading local `main`, then editing a separate worktree without re-reading files there
- Forgetting that a new worktree may not have dependencies installed yet, which can make `npm run test:ci` fail early with `sh: eslint: command not found`
- When multiple sibling worktrees exist, stale `.next` build output under another worktree can confuse repo-wide ESLint/test runs and produce unexpected `ENOENT` reads against files that no longer exist in that sibling checkout. If `npm run test:ci` fails with an ESLint file-open error pointing into `.worktrees/<other-branch>/.next/...`, remove stale `.next` directories under the affected worktrees and rerun.
- If the repo standardizes on repo-root linked worktrees under `.worktrees/`, repo-wide ESLint must explicitly ignore `.worktrees/**`. Otherwise `npm run lint` / `npm run test:ci` can scan nested sibling checkouts and fail on stray merge-conflict markers or other residue inside those worktrees even when the active checkout is healthy. In this repo, the correct fix is to add `.worktrees/**` to `globalIgnores()` in `eslint.config.mjs`.
- Accidentally replacing finalized page titles while adding canonical metadata
- Hardcoding outdated route names into sitemap/canonical
- Including routes in sitemap that currently return `notFound()`

## Done criteria

- All edits are based on latest `origin/main`
- Recent merged title/copy changes remain intact
- canonical/robots/sitemap are internally consistent
- regression test passes
- `npm run test:ci` and `npm run build` pass
