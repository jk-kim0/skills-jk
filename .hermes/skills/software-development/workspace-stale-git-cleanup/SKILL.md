---
name: workspace-stale-git-cleanup
description: Safely clean stale git branches and worktrees across many repositories under a workspace root, using conservative rules and explicit verification.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Workspace stale git cleanup

Use when the user asks to clean stale branches/worktrees from the current workspace root rather than from a single repository.

## When this skill applies

- Current directory is a workspace folder like `~/workspace`, not a git repo itself.
- There may be many sibling repos, some with linked worktrees.
- The user wants safe cleanup, not aggressive pruning.

Do not use this as the default just because the user's wording contains `workspace`.
For this user, if `pwd` is already inside a git repository and they simply say `workspace 정리해줘`, the default interpretation is repo-local cleanup for the current repository, not a sweep across sibling repos.
In that case, switch to `safe-git-worktree-branch-cleanup` and begin with live `pwd` / repo-root verification.

## Scope interpretation rule

Distinguish carefully between these two user intents:

1. `workspace 정리해줘` or similar, when the user clearly means the whole local workspace root
   - interpret as cross-repository cleanup under `~/workspace`
2. `이 repo 의 workspace 정리` / `this repo's workspace cleanup`
   - interpret as repo-local cleanup only
   - clean only the current repository's worktrees, local branches, and obvious temp leftovers
   - do **not** scan or modify sibling repositories

If the user is currently inside a repo and the phrasing mentions `this repo`, prefer repo-local interpretation even if the word `workspace` appears.

## Safety rules

1. Do not delete the current checked-out branch.
2. Do not delete any branch currently checked out by any worktree.
3. Do not delete detached worktrees if they have uncommitted or untracked files.
4. Do not auto-delete generic local branches like `main`, `master`, `develop`, `release`, or `alpha` unless the user explicitly asks.
5. Treat top-level repos in detached HEAD state as special; do not assume they are stale worktrees.

## Discovery steps

1. Confirm the current directory is not itself a git repo:
   - `git rev-parse --show-toplevel`
2. Enumerate sibling repos under the workspace root by checking for `.git`.
3. Deduplicate repos by `git rev-parse --git-common-dir` so secondary linked worktrees are not processed twice as if they were separate repositories.
4. For each unique repo, collect:
   - `git worktree list --porcelain`
   - `git branch -vv`
   - default branch via `git symbolic-ref refs/remotes/origin/HEAD` (fallback to current branch if needed)

## Default interpretation for "workspace cleanup"

In this user's setup, a request like `workspace 정리` means:

1. refresh remote refs
2. move each repo root checkout back to its default branch (`main`, `develop`, etc.) when the root worktree is clean
3. update that default branch to the latest remote HEAD with a safe fast-forward when possible
4. remove clearly stale local worktrees and branches
5. preserve any dirty root repo or dirty worktree instead of forcing cleanup

User-specific requirement:
- include default-branch update as a standard part of workspace cleanup, not an optional extra
- for `main`-based repos, this normally means aligning local `main` to the latest `origin/main`
- if the root worktree is dirty, do not switch branches or fast-forward automatically; report it as intentionally preserved
- if the update is not a clean fast-forward, stop and report rather than forcing history changes

## Conservative stale classification

### Worktree candidates

Mark as removable only when one of these is true:
- `prunable` in `git worktree list --porcelain`
- detached worktree with clean `git status --porcelain`
- branch-backed worktree whose head branch has no open PR and only closed/merged PR history, indicating it is a post-merge leftover

Keep if:
- detached but dirty
- branch-backed worktree with an open PR or active unpublished purpose
- main/top-level repo even if detached

### Escalation rule for repeated repo-local cleanup requests

If the user repeatedly asks to clean "this repo's workspace" after conservative cleanup already removed the obvious clean/prunable items, treat that as permission to escalate one level further.

Important practical nuance:
- do not assume the previous cleanup result is still current
- in PR-heavy repos, another fetch or a little time passing can turn formerly active PR worktrees into stale residue because their PRs just merged and upstream refs become `[gone]`
- on each repeated cleanup request, re-run the full discovery pass (`git fetch --prune`, `git worktree list --porcelain`, `git branch -vv`, open-PR query) before deciding there is nothing left to do
- expect cleanup to happen in waves: one pass removes the already-stale items, the next pass may reveal newly stale merged-PR worktrees and branches

Then escalate one level further:

Important practical nuance:
- do not assume the previous cleanup result is still current
- in PR-heavy repos, another fetch or a little time passing can turn formerly active PR worktrees into stale residue because their PRs just merged and upstream refs become `[gone]`
- on each repeated cleanup request, re-run the full discovery pass (`git fetch --prune`, `git worktree list --porcelain`, `git branch -vv`, open-PR query) before deciding there is nothing left to do
- expect cleanup to happen in waves: one pass removes the already-stale items, the next pass may reveal newly stale merged-PR worktrees and branches

Then escalate one level further:

- preserve root worktrees with real local modifications
- preserve normal branch-backed worktrees that correspond to open PR head branches
- preserve open-PR local branches even if their detached helper worktrees are removed
- remove detached helper worktrees used only for rebase/conflict/follow-up scratch state, even when they are dirty, if all of the following are true:
  - they are not the primary/root worktree
  - they are detached rather than branch-backed
  - they are clearly helper names like `pr157-rebase`, `pr158-rebase-latest`, `pr157-followup`, `pr158-mainrewrite2`, etc.
  - the meaningful open-PR branch or kept branch-backed worktree remains elsewhere

This matches the practical user expectation that repeated cleanup requests mean "stop preserving conflict scratchpads and helper clones; keep only real active worktrees."
### Branch candidates

Mark as removable only when one of these is true:
- local branch has upstream `[gone]` in `git branch -vv` and is not checked out anywhere
- local branch is fully merged into the repo default branch and is not checked out anywhere
- local branch has no open PR and only closed/merged PR history, and is not checked out anywhere

Exclude by default:
- current branch
- any branch present in any worktree
- `main`, `master`, `develop`, `release`, `alpha`

## GitHub PR cross-check for branch-backed worktrees

When a worktree is branch-backed, do not rely only on `git merge-base --is-ancestor` or ahead/behind counts.
Squash merges often leave the original branch commit graph appearing unmerged even though the PR was already merged.

User-specific stale-candidate default learned from repo cleanup work:
- if a local branch/worktree is not connected to any currently open PR head branch, treat it as a stale candidate by default
- but do not delete it immediately; first validate whether it still contains meaningful local work relative to the latest `origin/main`
- this is stricter than the older heuristic of preserving most branch-backed worktrees automatically

Important interpretation rule for the validation step:
- prefer `git diff --stat origin/main..branch` and `git diff --name-only origin/main..branch` to compare the candidate tip tree directly against the latest main tree
- do not treat `origin/main...branch` diff or only `git rev-list --left-right --count` as sufficient proof of meaningful remaining work
- triple-dot and left/right history counts are still useful to understand ancestry drift, but they can dramatically overstate residual scope after squash merges or after main absorbed later sibling work
- the direct question for stale cleanup is usually: "what does this branch/worktree tip still change compared with latest main right now?"

Special evaluation case: stale branch history with a meaningful dirty patch on top

A branch/worktree can be stale in its commit history while still containing a meaningful last local modification in the working tree.
This showed up in a repo-local cleanup where:
- the branch was not tied to any open PR
- the associated old PR was closed or merged elsewhere
- rebasing the branch history onto latest `origin/main` produced immediate large conflicts
- but the current dirty worktree contained a narrow 2-file UI/component refactor that was still useful

Recommended handling:
1. evaluate the branch history separately from the dirty patch
2. if the branch history is stale, do not preserve the whole branch just because the worktree is dirty
3. extract the dirty patch with:
   ```bash
   git -C <worktree> diff -- <paths...> > /tmp/<name>.patch
   ```
4. create a fresh latest-main review branch/worktree
5. apply only that dirty patch there
6. verify with targeted lint/typecheck
7. preserve or hand off the fresh review branch, then treat the old branch as stale

This is especially appropriate when the branch's older commits drag in broad outdated route/content/test structure, but the final uncommitted patch is small and clearly intentional.

Preferred check:

```bash
repo=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh pr list --repo "$repo" --head <branch> --state open --json number,state,isDraft,url,title
gh pr list --repo "$repo" --head <branch> --state closed --json number,state,mergedAt,closedAt,url,title
```

Interpretation:
- open PR exists -> not stale by default
- no open PR and closed PR is `MERGED` -> usually stale if the worktree is just leftover cleanup
- closed PR without merge -> inspect before deleting

Important practical follow-up:
- after removing a merged PR's leftover worktree, `git branch -d` may still refuse deletion because squash/rebase merges are not direct ancestors
- when the PR is confirmed merged and the branch is no longer attached anywhere, it is acceptable to delete the branch with `git branch -D <branch>`
- do not use `-D` based only on `upstream: gone`; require merged-PR evidence first
- another safe stale case is a branch-backed worktree whose branch has no PR, is clean, and its tip is already exactly `origin/main` (or tracks `origin/main` with no unique commits); in that case both the worktree and local branch are just redundant local clones of main and can be removed

Additional practical root-cleanup case:
- sometimes the only thing preventing a safe fast-forward of `main` is unpublished local repo-maintenance work under paths like `.agents/skills/**`
- do **not** assume stash is the best preservation method; many users consider stash-based preservation lower value than keeping an inspectable worktree/branch
- preferred order:
  1. keep the work on a branch/worktree when preservation meaningfully matters
  2. only use a narrowly-scoped stash when the user clearly prioritizes finishing cleanup over keeping that work visible in git state, or when the same work is already preserved elsewhere
- this avoids turning meaningful local work into easy-to-forget stash entries just to make cleanup appear complete
- another safe stale case is a branch-backed worktree whose branch has no PR, is clean, and its tip is already exactly `origin/main` (or tracks `origin/main` with no unique commits); in that case both the worktree and local branch are just redundant local clones of main and can be removed

Important counter-case for root checkouts:
- a clean root checkout sitting on a non-default branch is **not** automatically a safe candidate to switch back to `main`/`develop`
- before restoring the root checkout to the default branch, require at least one strong stale signal such as:
  - merged/closed PR evidence for that exact branch, or
  - empty/absorbed diff versus the default branch, or
  - exact/no-op alias equivalence to the default branch tip
- if the clean root branch still has unique diff versus latest default and a disposable rebase onto the latest default conflicts broadly, preserve it even if there is no open PR
- practical interpretation: `clean + non-default + no open PR` is not enough by itself; a root checkout can still represent unpublished local work and should remain parked there until the user chooses a more destructive cleanup path

Additional practical root-cleanup case:
- sometimes the only thing preventing a safe fast-forward of `main` is unpublished local repo-maintenance work under paths like `.agents/skills/**`
- do **not** assume stash is the best preservation method; many users consider stash-based preservation lower value than keeping an inspectable worktree/branch
- preferred order:
  1. keep the work on a branch/worktree when preservation meaningfully matters
  2. only use a narrowly-scoped stash when the user clearly prioritizes finishing cleanup over keeping that work visible in git state, or when the same work is already preserved elsewhere
- this avoids turning meaningful local work into easy-to-forget stash entries just to make cleanup appear complete
- in PR-heavy repos this can happen repeatedly during one cleanup session because `origin/main` keeps advancing while the user continues asking for cleanup; each new root-local skill tweak should be stashed before the next fast-forward so `main` can return to a clean synced state

Worktree-local variant:
- a merged stale worktree can also contain small local-only skill/doc tweaks under `.agents/skills/**`
- if the worktree is otherwise stale and removable, stash those edits from inside that worktree first, then remove the worktree
- this avoids preserving the whole stale worktree just for a tiny local procedural note

Disposable scratch-file variant:
- active or still-kept worktrees can accumulate untracked helper files such as `.tmp_pr_body.md` or `.tmp_pr_body_<name>.md`
- if these are clearly PR-body scratch files and the user asked for workspace cleanup, delete them even in otherwise-kept worktrees so they do not keep the worktree looking dirty
- do not treat these files as meaningful project work unless their contents or path clearly indicate something more substantial than a temporary PR description draft

Redundant branch-backed clone-of-main variant:
- sometimes a branch-backed worktree is neither detached nor tied to an open PR, but its branch tip is exactly the current `origin/main`
- if that worktree is clean and the branch has no open PR, it is just a redundant local clone of `main` with a leftover feature-ish branch name
- in that case it is safe to remove both the worktree and the local branch on repeated cleanup passes
- verify by checking all of the following:
  - no open PR for the branch
  - branch/worktree clean
  - `git rev-parse <branch>` equals `git rev-parse origin/main` (or no unique commits relative to `origin/main`)
  - branch is not the current branch and not attached to another worktree you intend to keep

Important counter-case:
- do **not** delete the worktree just because the branch currently equals `origin/main` if the worktree itself is dirty
- a clone-of-main helper worktree can accumulate real unpublished local edits and then cease to be redundant, even if its branch started as an exact alias of `origin/main`
- in that situation, preserve the worktree and treat it as active local work until the dirt is explicitly resolved or discarded
- after stashing or otherwise changing root-local cleanup residue, re-check the helper worktree again; its branch head or classification may no longer match the earlier snapshot

Worktree-local variant:
- a merged stale worktree can also contain small local-only skill/doc tweaks under `.agents/skills/**`
- if the worktree is otherwise stale and removable, stash those edits from inside that worktree first, then remove the worktree
- this avoids preserving the whole stale worktree just for a tiny local procedural note

## Temporary PR-body files inside stale worktrees

Files like `.tmp-pr-body.md` are often PR-process leftovers rather than meaningful work product.
If the branch has no open PR and only merged PR history, an untracked temp PR-body file should not by itself block stale-worktree deletion.
Inspect the file briefly, but if it is clearly a PR draft/body scratch file, treat it as disposable cleanup state.

## Standalone stale clone that also owns nested linked worktrees

A directory that looks like a stale standalone clone can still be the owning repo for nested linked worktrees inside paths like:

- `.worktrees/<name>`
- repo-local helper worktree containers under the clone itself

Practical implication:
- do **not** `rm -rf` the parent clone immediately just because the parent checkout itself is stale and clean
- first inspect `git worktree list --porcelain` from that clone
- if nested linked worktrees exist, classify and remove those stale child worktrees first
- delete any corresponding stale local branches next
- only then remove the parent stale clone directory itself

Typical safe sequence:
1. `git -C <stale-clone> worktree list --porcelain`
2. for each stale child worktree:
   - `git -C <child-worktree> status --short --branch`
   - `git -C <stale-clone> worktree remove <child-worktree>`
3. `git -C <stale-clone> worktree prune`
4. delete confirmed-stale local branches from the parent clone
5. if the parent clone is now just an outdated duplicate checkout, remove the parent directory

Why this matters:
- the parent clone may be stale as a working checkout while still being the Git owner of linked worktrees
- removing the directory first skips normal git cleanup and makes later verification noisier than necessary
- cleaning the child worktrees first gives a safer and more auditable cleanup result

## Important command pitfalls

When removing a worktree, run the command from the owning repo context:

```bash
git -C /path/to/main/repo worktree remove --force /path/to/worktree
```

Do not run plain `git worktree remove ...` from an arbitrary non-repo directory. That can fail with `fatal: not a git repository`.

If the main repo itself is dirty and you need to switch the root worktree back to `main`, be careful with nested linked worktrees stored under the repo directory such as `.claude/worktrees/...`.

Observed behavior:
- `git stash -u` does not absorb nested linked worktrees
- Git can print lines like `Ignoring path .claude/worktrees/<name>/`
- after switching branches, the parent repo may still show `?? .claude/worktrees/`

Interpretation:
- this does not by itself mean the root repo is unsafe or that the child worktrees are stale
- do not delete nested worktree directories just to make `git status` look clean
- treat them as active linked worktrees and inspect `git worktree list` first

## Recommended execution order

1. Report what is being checked.
2. Discover repos and candidates.
3. Remove only clearly safe stale worktrees first.
4. Run `git -C <repo> worktree prune` after removals.
5. Delete clearly stale local branches.
6. Re-run `git worktree list --porcelain` and `git branch -vv` to verify the result.
7. If a `git worktree remove --force <path>` attempt fails, do not assume the worktree is still present. Re-check both:
   - whether the filesystem path still exists
   - whether `git worktree list --porcelain` still tracks that path
   In practice, some "failed" removals are already effectively cleaned up, especially after prune or when the path disappeared earlier.
8. Summarize what was deleted and what was intentionally left alone.

## Practical execution lesson: prefer incremental cleanup over giant batch commands

In a repo with many nested worktrees, giant shell loops or monolithic cleanup scripts can hit tool timeouts even when Git is making progress.

Preferred pattern:
- remove safe worktrees in smaller batches or one-by-one
- after any timeout, immediately re-query `git worktree list --porcelain` and `git branch -vv`
- treat the refreshed Git state as source of truth rather than assuming the timed-out command failed completely
- only then continue with the remaining candidates
- expect another cleanup wave after updating `main`; newly merged PRs or helper clones can become obviously stale only after remote refs and root `main` advance

Why this matters:
- cleanup often partially succeeds before the tool timeout fires
- retrying the same full batch blindly wastes time and can misclassify already-removed items
- a path reported later as `is not a working tree` usually means the earlier cleanup already succeeded and only verification remained

## Practical execution lesson: fast-forward main only after confirming root is truly clean

When workspace cleanup includes bringing root `main` to `origin/main`, verify the root checkout again after stale worktree/branch cleanup.

Helpful sequence:
- `git status --short --branch`
- if root is clean, run `git pull --ff-only origin main`
- if root contains local-only helper or skill work, stash just that scoped path before the fast-forward

This is especially useful when the root dirt came from untracked repo-local agent skill files. Preserve them with a narrowly-scoped stash instead of leaving `main` behind remote.

## Practical execution lesson: repeated cleanup passes can reveal new sibling helper worktrees

In PR-heavy repos, a later cleanup pass can surface new worktrees that were not present in the previous pass, especially after:
- a fast-forward of `main`
- another local agent session creating scratch worktrees
- a related PR merging and leaving behind comparison/revert/fix helper trees

Common examples are sibling worktrees outside the repo root such as:
- `<repo>-platform-first-followup`
- `<repo>-platform-first-revert`
- `<repo>-platform-first-xfix`
- `<repo>-pr219-followup`
- `<repo>-pr219-ci-fix`

Practical rule:
- after each cleanup wave, re-run `git worktree list --porcelain`
- do not assume the candidate set is stable across passes
- if these late-appearing worktrees are detached and clean, treat them as stale helper clones and remove them
- if they are branch-backed but tied to a branch whose PR is already merged and whose upstream is gone, treat them as stale unless they contain real unpublished work

Additional important workspace-root variant:
- the workspace's immediate child directories can themselves be linked worktree checkouts, not just standalone clones or repo-internal `.worktrees/*` paths
- these top-level sibling worktrees usually have a `.git` file, their own checkout path, and share the owning repository's `git common-dir`
- if you only clean the owner repo's internal `.worktrees/*` paths and stop, you can miss stale top-level linked worktrees such as `<repo>-pr319-tos`

Recommended verification after each cleanup wave:
1. re-scan immediate child directories under the workspace root for entries with `.git`
2. group them again by `git rev-parse --git-common-dir`
3. compare the grouped result with `git worktree list --porcelain` from each owning repo
4. if a top-level sibling directory is just a clean detached linked worktree sharing the same common-dir, remove it too with `git -C <owner-repo> worktree remove <path>`

Why this matters:
- owner-repo cleanup and workspace-root directory cleanup are not the same thing
- a linked worktree can survive as a sibling directory even after obvious repo-internal stale worktrees were removed
- a final immediate-child re-scan is the easiest way to catch these leftovers before reporting cleanup complete

## Practical stopping rule: leave the final unpublished local branch alone unless the user clearly wants destructive cleanup

After aggressive-but-safe cleanup, you may reach a point where only one or a few local branches remain that:
- are clean
- have no open or closed PR metadata
- are still attached to a worktree
- carry unique commits relative to `origin/main`

Example pattern: a branch like `pr205-rewrite` that looks old, but still has unique local commits and no authoritative PR history proving it is disposable.

At that point:
- stop deleting automatically
- report that this is now an unpublished-local-work judgment call, not ordinary stale cleanup
- only remove it if the user explicitly wants destructive cleanup of the remaining unpublished branch

## Good final-report format

- Deleted stale worktrees
- Deleted stale branches
- Verification result
- Intentionally preserved items and why

## Audit-only mode: named directory stale check without deletion

When the user asks only whether specific workspace directories are stale, do an audit pass without deleting anything.

Recommended checks for each named directory:
1. verify the path exists and whether it is:
   - a standalone git repo/clone
   - a linked worktree
   - not a git repo at all
2. inspect:
   - `git branch --show-current`
   - `git status --short --branch`
   - last commit via `git log -1 --format='%h %ci %s'`
   - upstream / gone state
   - `git worktree list --porcelain`
3. if it is a branch-backed worktree, cross-check PR state with `gh pr list --head <branch> --state open|closed`
4. compare against the canonical sibling repo if one exists (same `origin` URL but a separate newer checkout)

Useful classification heuristics for audit-only stale reporting:
- standalone clean clone on `main` that is far behind `origin/main`, while another sibling checkout of the same repo already exists and is more current -> strong stale candidate
- clean linked worktree whose branch upstream is gone and whose PR is already merged -> stale
- empty non-git directory used as a former worktree container -> stale leftover

Important parent-container caveat:
- a standalone clone can itself host nested linked worktrees under directories like `.worktrees/*`
- if the parent clone looks stale but still owns nested worktrees, do not report it as a simple "safe to delete individually" case
- instead report it as a stale bundle / grouped cleanup candidate: remove or review the nested worktrees first, then remove the parent clone
- this is especially important when the nested worktrees are themselves clean leftovers from already merged PRs

## Practical stale-clone classification lessons from named workspace directories

### Duplicate standalone clone on `main` with canonical sibling

A top-level directory can be a stale standalone clone even when it is not a linked worktree.
Strong safe-delete signals:
- same `origin` as another canonical sibling checkout already present in the workspace
- current branch is `main`
- working tree is clean
- `HEAD` exactly equals `origin/main`, or it is only behind `origin/main`
- the sibling canonical checkout is at least as current or newer

Example pattern:
- `skills-jk-private-1` vs canonical sibling `skills-jk-private`
- both point at the same `origin`
- the duplicate clone is clean and `HEAD == origin/main`

In that case, the duplicate clone is just redundant local residue and can be removed directly.

### Duplicate standalone clone with only disposable local dirt

If a duplicate standalone clone looks stale but is technically dirty, inspect whether the dirt is only machine-local editor residue such as:
- `.idea/`
- similar IDE metadata directories

If all of the following are true:
- same `origin` as a canonical sibling checkout
- no unique commits worth preserving relative to the canonical remote branch
- root checkout is otherwise stale or behind remote
- the only dirt is disposable local IDE/editor metadata

then treat it as safely removable duplicate residue rather than preserving it just because `git status` is non-clean.

Example pattern:
- `skills-jk-private-2`
- behind `origin/main`
- only `?? .idea/`
- canonical sibling checkout already exists

### Old standalone PR-review clone

A top-level clone named like a review helper (for example `*-pr130-review`) is often a stale standalone clone rather than a linked worktree.
Do not rely only on the local branch name in that clone, because it may be something generic like `pr-130` rather than the real GitHub head branch name.

Recommended check:
1. identify the intended PR number from the directory name or user context
2. run `gh pr view <number> --repo <owner/repo> --json state,mergedAt,closedAt,headRefName,...`
3. if the PR is already merged/closed, the clone is clean, and there is no unique local work, remove the whole review clone directly

This is useful when the clone is not attached to any current worktree graph and exists only as an old review snapshot.

### Preserve uncertain standalone clones with local-only unique commits

Do not auto-delete a standalone clone just because:
- a canonical sibling checkout exists, and
- the branch looks old or experimental

If the clone has a local-only branch with no upstream and at least one unique local commit relative to the canonical default branch, preserve it by default unless the user explicitly wants destructive cleanup.

Useful check:
```bash
git diff --stat origin/<default>..<branch>
git log --oneline --decorate origin/<default>..<branch>
```

If this shows real unique local work, classify it as `stale-possible but uncertain` and leave it alone.

## Example preserved items

- detached worktree with untracked temp files
- generic local branch names with possible policy meaning
- top-level repo in detached HEAD state
- standalone clone with local-only unique commits and no clear PR/merge proof that it is disposable

## Additional safe cleanup win: empty worktree namespace directories

In large workspaces, after `git worktree prune` there may be no real removable worktrees left, but empty namespace directories can remain under containers like:

- `.worktrees/<group>`
- `.claude/worktrees/<name>/.claude`

These are not worktrees themselves; they are just leftover empty directories.

Safe rule:
- only remove them if the directory is completely empty
- do not remove non-empty grouping directories just because they are not registered worktrees
- do not recurse into populated worktree trees looking for arbitrary empty subdirectories; limit cleanup to obvious top-level namespace shells or clearly empty helper dirs

Recommended sequence:
1. run `git worktree prune`
2. verify there are no prune candidates with `git worktree prune --dry-run --verbose`
3. optionally delete only clearly empty namespace/helper directories

This is a good conservative fallback when the user wants the workspace "cleaned up" but branch/worktree deletion is not clearly safe.
