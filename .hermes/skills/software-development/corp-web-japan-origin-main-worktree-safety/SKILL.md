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

Follow the common `repo-root-worktree-path-policy` skill for worktree location and naming.

```bash
git fetch origin main --quiet
git checkout main
git pull --ff-only origin main
git worktree add .worktrees/<branch-name> -b <branch-name> origin/main
```

If local `main` is intentionally left untouched for some exceptional reason, explicitly tell the user and still branch from the fetched latest `origin/main`.

Example:

```bash
git checkout main
git pull --ff-only origin main
git worktree add .worktrees/fix-issue-62-seo-baseline -b fix/issue-62-seo-baseline origin/main
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

Practical fallback pattern from the repository root:

```bash
git worktree add .worktrees/<topic> -b <branch-name> origin/main
```

If your current shell is already inside another linked worktree, do not use a relative `.worktrees/<topic>` path. That will create a nested worktree under the current worktree, not under the repository root. Either `cd` to the main repository root first, or use absolute paths with `git -C <repo-root>`:

```bash
git -C /path/to/corp-web-japan worktree add /path/to/corp-web-japan/.worktrees/<topic> -b <branch-name> origin/main
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
- In live-parity or migration-goal follow-up work, do not automatically treat live/corp-web-contents wording as authoritative over latest-main product-copy decisions. If the user says a PR is reverting an intentional latest-main title, hero lead, or metadata description change, update the governing goal/plan/skill doc to mark that wording as an intentional parity exception rather than changing the route back.
- For bilingual goal documents, mirror the exception in both language sections so future agents reading either half avoid the same revert.

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

### Issue-authored PR plan execution rule

A recurring pattern in this repo is that the issue body itself already contains an execution split such as:
- `PR 1`
- `PR 2`
- `PR 3`
- `PR 4`

Treat that as an implementation contract, not just background prose, when all of the following are true:
- the user asks to implement those PRs directly
- each PR scope is already described in the issue body
- the scopes are independent enough to land from `main` without depending on each other

Preferred execution pattern:
1. re-check the latest `origin/main`
2. create one fresh worktree and one fresh branch per planned PR scope
3. implement each PR against `main` unless there is a real code dependency requiring a stack
4. run the lightest source-level verification that matches each PR's moved files / route imports / path-based tests
5. push each branch and open each PR separately
6. comment on the parent issue with the resulting PR numbers/URLs so the issue remains the navigation hub

Important distinction from the stacked-PR guidance above:
- if the issue's `PR 1..N` plan describes independent cleanup batches, do **not** restack them by default just because they were numbered sequentially
- use stacked PRs only when later branches truly depend on earlier branch-only changes
- otherwise, open all planned PRs directly against `main`

## Staged issue implementation: prefer a small stacked PR chain when later steps depend on earlier ones

A recurring safe pattern in this repo is a staged CI / workflow / infra change where the user wants the plan implemented step by step as separate PRs, but later steps build directly on earlier ones.

Use a stacked PR chain when all of the following are true:
- the user explicitly wants separate PRs by stage
- stage N+1 depends on files introduced or reorganized in stage N
- keeping each PR small and reviewable matters more than making every PR independently landable from `main`

Typical examples:
- PR 1: add docs-only CI skip
- PR 2: split monolithic CI into smoke + scoped test jobs
- PR 3: add changed-files gating on top of the new scoped jobs
- PR 1: introduce a shared UI/layout primitive plus its contract test
- PR 2: migrate existing pages/routes to that primitive and remove the now-redundant page-specific wrappers

Recommended workflow:
1. Fast-forward local `main` to latest `origin/main` first.
2. Create PR 1 from `main`.
3. Before starting PR 2, re-check PR 1's actual state with `gh pr view <parent> --json state,mergedAt,headRefName,mergeCommit` and `git fetch origin --prune`.
   - If PR 1 has already merged and its branch was deleted, do not create PR 2 from the stale local PR 1 worktree/branch.
   - Fast-forward local `main` to the merge commit and create PR 2 as an independent latest-main branch.
   - Only keep PR 2 stacked when PR 1 is still open and PR 2 truly depends on branch-only files.
4. Create PR 2 from the PR 1 branch only if PR 2 truly depends on PR 1 and PR 1 has not merged yet.
5. Create PR 3 from the PR 2 branch only if PR 3 truly depends on PR 2.
6. For each staged PR, set the GitHub base branch explicitly to the immediate parent branch, not to `main`.
7. In each PR body, state clearly that it is a stacked PR and name the parent base branch. If the parent already merged, state it as a prior PR instead of a stacked base.
8. Keep each PR scope limited to exactly one stage of the issue plan; do not leak later-stage optimization logic into earlier PRs.
9. For child PRs that depend on a new parent primitive/module, run both the child page tests and the parent primitive/module contract test from the child worktree so the stack is verified as reviewers will see it.
10. After opening the child PR, verify both the actual remote branch refs with `git ls-remote` and the PR base branch with `gh pr view`; do not rely only on the PR creation URL.

Scope discipline for this pattern:
- Stage 1 should usually be the smallest safe behavior change with minimal surface area.
- Stage 2 may introduce structure or helper scripts without yet narrowing execution scope.
- Stage 3 may add selective execution / gating on top of the stage-2 structure.
- If a later PR needs to touch files from an earlier stage, that is acceptable in the child PR; do not broaden the earlier parent PR just to avoid stacked diffs.

Verification discipline:
- For stage-1 workflow-only changes, validate YAML parsing and diff hygiene at minimum.
- For stage-2 script/test-sharding changes, run the new contract/assignment verification plus at least a few representative shards, not necessarily every shard locally.
- For stage-3 gating changes, validate YAML parsing and changed-scope logic carefully; keep the diff mostly inside the workflow file unless the gating design truly requires helper changes.

Common pitfall:
- Opening all stage PRs directly against `main` even though later stages depend on earlier branch-only files. That creates noisy diffs and can make review impossible.
- The correct fix is to stack the dependent PRs and use explicit `gh pr create --base <parent-branch> --head <child-branch>`.

Post-merge child PR cleanup:
- If the parent PR in a stacked chain is squash-merged and its branch is deleted, a child PR can automatically appear based on `main` while its head still contains the parent branch's original unsquashed commit.
- Symptom: `gh pr view <child> --json baseRefName,commits` shows `baseRefName: main`, but `git rev-list origin/main..origin/<child-branch>` includes both the old parent commit and the child commit.
- Fix the child PR by rebasing only the child commit onto the new `origin/main` tip:
  ```bash
  git fetch origin --prune
  git -C .worktrees/<child> rebase --onto origin/main <old-parent-commit-sha> <child-branch>
  git -C .worktrees/<child> push --force-with-lease origin HEAD:refs/heads/<child-branch>
  ```
- After this rewrite, update the child PR body to remove stale stacked-parent wording, then verify the real remote branch and PR commit list:
  ```bash
  git ls-remote origin refs/heads/<child-branch>
  env -u GITHUB_TOKEN gh pr view <child-pr> --json baseRefName,headRefOid,commits,files,statusCheckRollup
  ```
- Do not treat `mergeStateStatus=BLOCKED` immediately after this push as a conflict if the PR now contains the expected single commit; it usually means fresh required checks are pending.

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

## Copy-candidate review PR pattern

When the user asks for several copy candidates and also asks to open the PR before choosing the final copy:
- do not select a single final sentence on their behalf
- render all requested candidates in the affected page or review surface so the Preview Deployment can be used for comparison
- include the exact candidate text in the PR body for review without needing to inspect the diff
- keep the implementation deliberately temporary/review-oriented, and note in the PR body that a follow-up should reduce the page to the selected final copy
- if external corporate-site examples were checked for wording style, summarize the reference pattern in the PR body without over-quoting or making the page copy sound like sourced legal text

## Visual/layout validation commit pattern

When the user wants to personally verify whether a UI/layout exception is still necessary, it is acceptable to push an explicit validation commit to the existing PR rather than only discussing the tradeoff.

Use this pattern when all of the following are true:
- the PR already exists and is meant for review/preview inspection
- the user explicitly asks to remove an exception or apply a common setting so they can check the visual result
- the change is reversible and scoped to the same UI/layout question

Execution rules:
1. Keep the commit separate from the original cleanup commit so reviewers can compare intent.
2. Make the commit message state that it is a validation/test commit, not a final visual policy decision.
   - Example subject: `test: validate shared about-us section spacing`
   - Example body: `Remove section-specific vertical spacing from the about-us route so the PR can verify whether a single shared AboutUsSection spacing contract is sufficient.`
3. Update narrow source-based tests so they describe the temporary validation contract accurately.
4. Push to the same PR branch and verify the remote branch SHA and PR `headRefOid`.
5. Report that CI/Preview Deploy has restarted; do not wait passively unless the user asks.

This is different from a normal refactor PR: the purpose is to make a reviewable preview state for human visual judgment, so do not squash it immediately into the original commit unless the user later chooses that result as final.

## Small preview-route copy edit pattern

When the user requests a narrow copy change on an existing corp-web-japan `/t/**` preview route, keep the implementation deliberately small rather than reopening the whole page-parity workflow.

Recommended pattern:
1. Start from latest `origin/main` in a fresh non-main worktree as usual.
2. Edit the visible route copy in `src/app/**/page.tsx` and update matching page metadata (`metadata.title` / `metadata.description`) when the changed hero title or lead is also the browser/SEO preview text.
3. Preserve the user's exact Japanese copy when they provide it; do not paraphrase or expand it into new marketing claims.
4. Add or update the mirrored source-level route test so it asserts the new copy is present and any explicitly replaced old wording is absent.
5. For copy-only changes, use the narrow source test first and rely on CI/Preview Deploy after push; do not start a local dev server or broaden into visual/browser parity unless the user asked for visual validation.

Example shape from `/t/platforms/acp` hero-copy work:
- update `src/app/t/platforms/acp/page.tsx` hero title/lead and metadata together
- update `tests/src/app/t/platforms/acp/page.test.mjs` with positive assertions for the new title/description and negative assertions for the removed old title/extra explanatory sentence

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

Practical post-PR-creation nuance learned from issue #449 PR 1:
- `origin/main` can also advance in the short window after `gh pr create`, causing the newly opened PR to immediately show `mergeStateStatus: BEHIND` even though the branch was latest-main-based when pushed.
- Do not report the PR as done just because it opened successfully. After creation, verify the actual remote head SHA and PR metadata:

Practical existing-PR copy/metadata follow-up nuance:
- If the user asks for a specific alignment such as "make `metadata.description` match `AcpHeroLead`", first inspect the existing PR branch. The requested condition may already be true even if the PR body or review context sounds stale.
- Do not fabricate a no-op code change. If the file already matches, say so, then handle any real remaining PR hygiene such as rebasing a BEHIND branch, re-checking the exact lines after rebase, updating the PR body to describe the alignment, and pushing the rebased branch.
- Verify with the narrowest relevant source test plus remote head SHA / PR `headRefOid` before reporting completion.

Practical post-PR-creation verification command pattern:
  ```bash
  git ls-remote origin refs/heads/<branch>
  env -u GITHUB_TOKEN gh pr view <pr-number> --json headRefOid,mergeStateStatus,statusCheckRollup
  ```
- If the PR is already behind, fetch/rebase onto the new `origin/main`, rerun the narrow targeted tests touched by the PR, and push with `--force-with-lease`:
  ```bash
  git fetch origin --prune
  git rebase origin/main
  node --test <targeted-tests>
  git push --force-with-lease origin HEAD:refs/heads/<branch>
  ```
- Re-verify that local HEAD, the remote branch ref, and PR `headRefOid` all match, and that `merge-base HEAD origin/main` equals the latest `origin/main`. Fresh check runs may briefly show an empty `statusCheckRollup`; use `gh run list --branch <branch>` to confirm new runs attached to the rewritten head SHA.

Practical follow-up nuance:
- If you are on a fresh latest-main worktree branch with uncommitted changes, `git rebase origin/main` will fail with `cannot rebase: You have unstaged changes`.
- In that situation, do not stash reflexively.
- First verify whether the branch is still exactly based on the current remote main tip:

Existing PR rebase nuance:
- If an existing PR is CI-green but `gh pr view` reports `mergeStateStatus: DIRTY`, treat it as a latest-main rebase/conflict task rather than a test-failure task.
- Rebase the existing PR branch onto `origin/main`, resolve conflicts while preserving latest-main changes, rerun the narrow affected checks, and push with `git push --force-with-lease`.
- After resolving conflicts, run `GIT_EDITOR=true git rebase --continue` in non-interactive agent sessions so Git does not open Vim and hang the turn.
- When latest `main` promoted or renamed public routes while the PR branch still contains older preview-route assumptions (for example `/t/about-us` -> `/about-us`, or `/t/certifications` -> `/certifications`), resolve conflicts in favor of latest-main canonical route files and tests. Reapply only the PR's intended structural or contract change on top; do not resurrect old preview paths in route tests just because they appear in the branch side of the conflict.
- When a just-merged PR refactored the same area as the open PR, inspect that merged PR first with `gh pr view <merged-pr> --json body,files,commits,mergeCommit,title` and summarize its intent/scope before resolving conflicts. Preserve the merged PR's new vocabulary/structure/tests, then reapply only the open PR's intended delta on top. Example pattern: if a merged legal refactor introduces `LegalDocumentSection` / `LegalDocumentIntro` / `LegalDocumentLead` / `LegalDocumentLayout` and keeps `legalDocumentBodyClassName` as the styling primitive, keep those vocabulary assertions and apply typography changes only inside `legalDocumentBodyClassName` plus matching tests.
- After such refactor conflicts, update the open PR body so it explains that it is now rebased on the merged refactor and names the final remaining contract rather than the pre-rebase implementation history.
- After such route-promotion or same-area refactor conflicts, run narrow source checks that prove both sides of the contract: affected route tests, any path/CI assignment assertions such as `node scripts/ci/assert-test-groups.mjs`, and lightweight TypeScript/ESLint checks for touched helper scripts when available.


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

## Static finite variant routes in `/t/**` preview work

When a preview/static marketing surface has a small finite set of variants (for example plans AIP/ACP), prefer explicit sibling App Router routes over a dynamic segment unless the user explicitly asks for a dynamic catch-all.

Recommended shape:
- root route keeps the default behavior without changing the URI, for example `/t/plans` renders the AIP view without redirecting
- finite variants use explicit route files such as `src/app/t/plans/aip/page.tsx` and `src/app/t/plans/acp/page.tsx`, not `src/app/t/plans/[product]/page.tsx`
- keep those route files thin: route metadata + a call into a route-local shared content module such as `src/app/t/plans/plans-page-content.tsx`
- put the duplicated pricing/table/page composition in the route-local shared module, not in each product route
- when tab links need to work both before and after `/t` prefix removal, derive destinations from the current pathname or a route-local base rather than hardcoding `/t/plans/...` inside the reusable tab component
- keep source-inspection tests aligned with the explicit files and assert that product routes do not duplicate heavy composition such as `<PricingRoot>`, `<PlanCard>`, or `<CompareTable>`

Pitfall: a dynamic `[product]` route looks compact, but for this user's static preview pages it hides the intended file structure and is harder to align with route-local authoring. If the user points this out, replace it with explicit sibling routes while keeping the shared route-local content module to avoid real duplication.

## Page-copy / metadata alignment pitfalls

When aligning `metadata.description` with visible route copy such as a hero lead, first verify the intended visible copy is correct and complete. Do not make the metadata match a previously mistaken shortened lead just because the current branch already contains that shortened text.

Safe pattern:
1. Re-read the user request and compare it against the pre-change/original copy if the user mentions preserving, shortening, or changing only part of a sentence.
2. If the requested change is "first sentence only" or similar, preserve the remaining sentences and JSX structure such as `<br />` unless the user explicitly asks to remove them.
3. Make `metadata.description` match the final intended visible text, usually by joining the same sentences without JSX tags.
4. Update source-based tests so they assert the preserved sentences are present; avoid negative assertions that incorrectly forbid intentionally preserved text.
5. In the PR body, describe the preservation explicitly (for example: "keeps the two-sentence hero lead; only rewrites the first sentence and aligns metadata with the full lead").

Pitfall observed in PR follow-up work: if a user asks to align meta description with `AcpHeroLead`, that is not permission to keep an accidentally shortened `AcpHeroLead`. First repair the hero lead to the user's intended full copy, then align the metadata.

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

## Legacy route-removal pattern: remove the whole `/posts` compatibility bundle, not only the visible route file

When latest `corp-web-japan` still contains a legacy route family that the user explicitly says is only a temporary implementation artifact and should be removed entirely, do not stop after deleting the route entrypoint.

For the `/posts` legacy family, the real cleanup bundle can include all of the following:
- the App Router entry file such as `src/app/posts/[category]/[slug]/page.tsx`
- route-only parser/loader helpers such as `src/lib/resource-posts.ts`
- route-only UI such as `src/components/sections/resource-post-download-page.tsx`
- temporary source corpora such as `content/source-posts/**/*.html`
- source-reading tests that still assert the route file exists
- README / AGENTS guidance that still describes `/posts` as a supported compatibility surface

Recommended audit sequence before deleting:
1. search the repo for `/posts/`, `src/app/posts/[category]/[slug]/page.tsx`, `content/source-posts`, and route-only helper names such as `getResourcePost`, `listEventPostParams`, or `getResourceDownloadPost`
2. separate runtime usage from test/doc mentions
3. verify whether the remaining content corpus under `content/source-posts` is only legacy data rather than an input to current canonical `/events` routes
4. delete the entire compatibility bundle in one PR when the user has confirmed it is no longer used
5. update tests and repo guidance in the same change so no file still documents `/posts` as a valid remaining exception

Important user-specific rule for this repo:
- if the user says `/posts` endpoints were only temporary implementation artifacts and are no longer used, do not preserve even event-only compatibility by default
- treat that as authorization to remove the route, its helper/parser layer, the temporary HTML corpus, and the related guidance/tests together

## Source-inspection-only section component survivor follow-up

When a corp-web-japan tracking issue identifies section components that are only kept alive by source-inspection tests, do not jump directly to deletion. First classify whether the component has a visual/interaction contract worth preserving as an internal demo reference.

Safe pattern for reusable section/UI primitives that are not currently on a canonical route:
1. Search runtime imports and source-based tests for the component path/export.
2. If the component is a visual primitive or client interaction surface and deletion is not clearly intended, reconnect it to an existing noindex internal demo route such as `/internal/demo-sections` rather than leaving it as test-only residue.
3. Render a compact example that exercises the meaningful props/states, and include route-visible copy explaining the current decision: not deleted, not canonical-route reconnected yet, preserved for internal demo/contract review.
4. Update the route's mirrored source-inspection test so the internal route explicitly imports/renders the survivor components and asserts the rationale text. This converts the old "test-only survivor" into an intentional internal-demo contract.
5. Keep `src/app/internal/<route>/` reserved for route entry files unless the user explicitly asks for route-adjacent component files. For `/internal/demo-sections`, `src/app/internal/demo-sections/` should contain `page.tsx` only; put internal-demo-only widgets under `src/components/sections/internal-demo/**` and import them with the `@/components/sections/internal-demo/...` alias.
6. Keep authored copy and CTA wiring in `page.tsx` when route-local authoring is requested. For client widgets, keep the client component focused on interaction/rendering (for example accordion state), and pass route-authored items/labels/URLs from `page.tsx`.
7. Update source-inspection tests to assert both sides of the contract: the internal demo route imports/renders the components, the old orphan source paths are absent, and `src/app/internal/<route>/` does not accumulate non-page component files. Search and update older tests that read the old paths directly (for example asset-path, launch-readiness, and link-integrity tests).
8. Keep the PR narrow: internal demo route + internal-demo section components + directly affected source tests. Avoid promoting to canonical routes or changing public navigation unless the user explicitly asks for that route decision.

Example from issue #395:
- `src/components/sections/ai-crew/avatar.tsx` and `src/components/sections/ai-dashi/faq.tsx` were only referenced by tests.
- The first safe follow-up was to import/render `AICrewAvatar` and `AIDashiFaq` on `src/app/internal/demo-sections/page.tsx`, then extend `tests/src/app/internal/demo-sections/page.test.mjs` to pin that preservation contract.
- When the user corrected the route-local placement, the better final shape was to keep `src/app/internal/demo-sections/` to `page.tsx` only, move internal-only demo widgets to `src/components/sections/internal-demo/{ai-crew-avatar,ai-dashi-faq,role-slides,use-case-showcase}.tsx`, update `page.tsx` to use `@/components/sections/internal-demo/...` imports, keep FAQ copy/CTA in `page.tsx`, and assert both the old orphan paths and route-adjacent component files are gone.

- For client/interactive survivor components that contain copy or CTA targets, keep the real authored copy/CTA ownership in `page.tsx`; make the internal-demo client component own only interaction/rendering mechanics and accept items/CTA props from the route.
- Search all source-based tests for the old paths and update their assertions to the new route-local contract. Typical hidden references include asset-path tests, launch-readiness/link-integrity tests, and mirrored route tests.

Example from issue #395:
- `src/components/sections/ai-crew/avatar.tsx` and `src/components/sections/ai-dashi/faq.tsx` were only referenced by tests.
- The first safe follow-up was to render them on `src/app/internal/demo-sections/page.tsx` and extend the mirrored route test to pin that preservation contract.
- The corrected follow-up keeps `src/app/internal/demo-sections/` to `page.tsx` only, moves avatar/FAQ/role-slider/showcase implementation files to `src/components/sections/internal-demo/**`, keeps FAQ items and `aiDashiConsultUrl` in `page.tsx`, and updates tests to assert both the old orphan paths and route-adjacent component files no longer exist.

## New test file assignment safety

When adding any new `tests/**/*.test.mjs` file in `corp-web-japan`, update `scripts/ci/test-groups.mjs` in the same PR unless the file already matches an existing group matcher.

Verification:

```bash
node scripts/ci/assert-test-groups.mjs
```

Failure signature if missed:

```text
AssertionError [ERR_ASSERTION]: Unassigned test files:
tests/<new-test>.test.mjs
```

Practical rule:
- run the new targeted test first
- run `node scripts/ci/assert-test-groups.mjs` before push
- if it fails, add the narrowest regex to the appropriate group, usually `staticPages` for route/static-page structure tests

## CI workflow / ruleset safety for docs-only PRs and final status checks

When changing `corp-web-japan` GitHub Actions workflows, do not inspect workflow triggers in isolation. Also inspect the active repository ruleset / required status checks.

Practical repo-specific lessons:
- `main` may be protected by a ruleset whose required status check includes an early CI job such as `Detect changed scope`
- that check is emitted by `.github/workflows/ci.yml`
- if `ci.yml` uses workflow-level `pull_request.paths-ignore` for docs-only files such as `README.md`, a docs-only PR can end up with the required check missing entirely
- GitHub then treats the PR as blocked by a missing required check, even though the omission came from workflow trigger filtering rather than a test failure
- requiring an early job such as `Detect changed scope` is also insufficient as a final CI-complete signal: branch protection can pass as soon as scope detection succeeds, before smoke/scoped tests/build have finished

Safe fix pattern for missing required checks on docs-only PRs:
1. keep the required scope-detection check always creatable on PRs by avoiding workflow-level `pull_request.paths-ignore` for docs-only changes on `ci.yml`
2. if you remove that trigger-level ignore, do **not** automatically run the full CI stack on every docs-only PR
3. instead, keep the lightweight `changes` job always running, and gate heavier jobs (`Smoke`, scoped tests, build) with `needs.changes.outputs.*` so docs-only PRs emit the required check but skip expensive work
4. preserve `push.paths-ignore` separately if main-branch docs-only pushes should still avoid CI cost

Safe fix pattern for final CI-complete required checks:
1. add a final aggregate job after all CI jobs, for example `ci-result` with name `CI result`
2. set `if: ${{ always() }}` on the aggregate job so it runs even when dependencies fail or are skipped
3. include every relevant upstream CI job in `needs`, including scope detection, smoke, scoped test shards, and build
4. in the aggregate step, treat only `success` and `skipped` dependency results as pass states
5. treat `failure`, `cancelled`, and any other result as failure
6. after merging, update the repository required status check from the early job (`Detect changed scope`) to the aggregate job (`CI result`)

Minimal aggregate-job shell pattern:

```yaml
  ci-result:
    name: CI result
    runs-on: ubuntu-latest
    needs:
      - changes
      - smoke
      - test-publications
      - test-forms
      - test-routing-seo
      - test-static-pages
      - test-assets-shell
      - test-cross-cutting
      - build
    if: ${{ always() }}
    steps:
      - name: Verify CI dependency results
        env:
          CHANGES_RESULT: ${{ needs.changes.result }}
          SMOKE_RESULT: ${{ needs.smoke.result }}
          TEST_PUBLICATIONS_RESULT: ${{ needs.test-publications.result }}
          TEST_FORMS_RESULT: ${{ needs.test-forms.result }}
          TEST_ROUTING_SEO_RESULT: ${{ needs.test-routing-seo.result }}
          TEST_STATIC_PAGES_RESULT: ${{ needs.test-static-pages.result }}
          TEST_ASSETS_SHELL_RESULT: ${{ needs.test-assets-shell.result }}
          TEST_CROSS_CUTTING_RESULT: ${{ needs.test-cross-cutting.result }}
          BUILD_RESULT: ${{ needs.build.result }}
        run: |
          failed=0

          check_result() {
            local name="$1"
            local result="$2"

            case "$result" in
              success|skipped)
                printf '%s: %s\n' "$name" "$result"
                ;;
              *)
                printf '%s: %s\n' "$name" "$result"
                failed=1
                ;;
            esac
          }

          check_result 'Detect changed scope' "$CHANGES_RESULT"
          check_result 'Smoke' "$SMOKE_RESULT"
          check_result 'Test publications' "$TEST_PUBLICATIONS_RESULT"
          check_result 'Test forms' "$TEST_FORMS_RESULT"
          check_result 'Test routing and SEO' "$TEST_ROUTING_SEO_RESULT"
          check_result 'Test static pages' "$TEST_STATIC_PAGES_RESULT"
          check_result 'Test assets and shell' "$TEST_ASSETS_SHELL_RESULT"
          check_result 'Test cross-cutting contracts' "$TEST_CROSS_CUTTING_RESULT"
          check_result 'Build' "$BUILD_RESULT"

          exit "$failed"
```

Verification checklist for this class of change:
- inspect the repo ruleset with `gh api repos/<owner>/<repo>/rulesets` and the specific ruleset details
- confirm which check context is actually required
- read `.github/workflows/ci.yml` and verify the required check's job still exists under all intended PR paths
- run `actionlint .github/workflows/ci.yml`
- run a YAML parse check such as `ruby -e 'require "yaml"; YAML.load_file(".github/workflows/ci.yml")'`
- after pushing, verify the new PR head actually shows the workflow/checks in `gh pr view --json statusCheckRollup`
- also verify the remote branch SHA with `git ls-remote origin refs/heads/<branch>` before trusting laggy PR metadata

This avoids two subtle mismatches:
- `required check exists in branch protection` + `workflow trigger skips the job entirely`
- `required check is green` + `later CI jobs are still running or have failed`

## External-to-local content link replacement

Use this pattern when the user provides `querypie.com/ja/features/documentation/**` or similar external QueryPie content URLs and asks to replace them with local website content paths.

1. Keep the work in one ongoing PR when the user says they will continue providing links, unless they explicitly request separate PRs.
2. Search the runtime source first (`src/**`), not only the line numbers the user provided. If the same legacy URL appears in a shared runtime constant such as `src/content/*-links.ts`, update that too. Do not edit docs/example files unless the user asked for documentation cleanup.
3. Map legacy documentation families to current local canonical routes:
   - AIP introduction deck legacy URL -> `/introduction-deck/1/querypie-aip`.
   - Whitepaper legacy detail URLs -> canonical gated PDF route `/whitepapers/<id>/<slug>/pdf` for CTA/download actions.
   - Remember `/whitepapers/<id>/<slug>/download` is compatibility only; use `/pdf` for new internal CTA targets.
4. Verify the local target exists by reading the relevant MDX frontmatter under `src/content/introduction-deck/*.mdx` or `src/content/whitepapers/*.mdx`. Use the frontmatter `slug` as the route slug; do not copy legacy typos such as `ai-tranformation-japan` when the local slug is corrected.
5. Add or update source-inspection tests near the touched route/family:
   - homepage route contracts belong in `tests/src/app/page.test.mjs`
   - AI Dashi shared link constants can be pinned from `tests/src/app/solutions/ai-dashi/page.test.mjs`
   - assert both the intended local route and absence of `https://www.querypie.com/ja/features/documentation` in touched runtime sources.
6. Run the narrow node tests and a source grep for the legacy URLs under `src/` before committing.

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

- For corp-web-japan internal-link cleanup, verify the local canonical detail route from the repo-local publication skill/content records before replacing legacy `querypie.com/ja` URLs. In particular, use-case detail pages are `/use-cases/:id/:slug` while the use-case list route remains `/demo/use-cases`; do not convert detail CTAs to `/demo/use-cases/:id/:slug`.
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
