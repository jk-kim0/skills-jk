---
name: branch-squash-validity-and-stale-cleanup
description: Audit each local branch by synthetic squash versus latest origin/main, test rebase portability, classify meaningful local work vs stale residue, and safely delete stale branches/worktrees.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, branch, worktree, cleanup, stale, rebase, squash, audit]
---

# Branch squash validity and stale cleanup

Use when the user asks for a stronger repo-local workspace cleanup than ordinary merged-branch pruning, especially with wording like:
- `Open PR 이 아닌 worktree, branch 는 stale 가능성이 높아`
- `각 브랜치마다 진행하고`
- `로컬 변경사항을 모두 하나의 commit 으로 squash 한 이후`
- `main branch HEAD 와 비교하고`
- `rebase onto the latest main branch 시도하면서`
- `유의미한 변경사항인지 판별해줘`
- `stale branch, worktree 를 삭제해줘`

This skill is for one repository at a time, not whole-workspace multi-repo cleanup.

## Purpose

For each local branch, especially non-open-PR branches:
1. inspect current worktree/worktree dirt, not just committed branch history
2. synthesize the branch's current net effect as one squash commit
3. compare that squash patch against latest `origin/main`
4. attempt a disposable rebase onto latest `origin/main`
5. classify the branch/worktree as one of:
   - valid branch / meaningful local work
   - stale branch history + meaningful current local patch
   - merged residue / stale helper alias / stale no-op clone
6. delete only clearly stale worktrees and branches
7. report the current remaining branch/worktree/local-change state

## Core user-specific interpretation

Default assumption:
- non-open-PR local branches and worktrees are stale candidates by default
- but they are **not** auto-deleted without checking whether they still contain meaningful local work
- the required validation method is a synthetic squash built from the branch or current worktree state, compared against latest `origin/main`, plus a disposable rebase attempt onto latest `origin/main`

Important split:
- branch history can be stale
- current dirty local work on top of that branch can still be meaningful
- judge those separately

## Safety rules

- Never delete the current branch.
- Never delete `main` automatically.
- Never delete a dirty worktree automatically unless you have separately preserved or intentionally discarded its meaningful local patch.
- Never delete an open-PR branch/worktree just because it is behind or because a detached helper exists nearby.
- Always refresh `git fetch --prune`, open PRs, and `git worktree list` immediately before destructive cleanup.
- In fast-moving repos, treat the last refreshed snapshot as authoritative.

## Required discovery

Run from the target repo:

```bash
pwd
git rev-parse --show-toplevel
git fetch origin --prune
git status --short --branch
git branch -vv --no-abbrev
git worktree list --porcelain
gh pr list --state open --json number,title,headRefName,headRefOid,isDraft,url
```

Also inspect all local heads:

```bash
git for-each-ref --format='%(refname:short)|%(objectname)|%(upstream:short)|%(committerdate:iso8601)|%(subject)' refs/heads
```

## Branch-by-branch evaluation algorithm

Evaluate every local branch, but prioritize non-open-PR branches first.

For each branch, collect:
- branch name
- SHA
- upstream
- whether it is the current branch
- whether it is attached to a worktree
- attached worktree path if any
- current worktree dirtiness and diff summary if attached
- whether it matches an open PR head branch
- whether any PR for that branch is `OPEN`, `MERGED`, or `CLOSED`

Useful checks:

```bash
gh pr list --state all --head <branch> --json number,state,title,url,headRefName,headRefOid
git rev-list --left-right --count origin/main...<branch>
git diff --stat --find-renames origin/main..<branch> --
git diff --name-status --find-renames origin/main..<branch> --
git cherry origin/main <branch> || true
```

## Synthetic squash method

### Case A: branch-backed clean worktree or no attached worktree

Use branch tree directly:

```bash
base=$(git merge-base origin/main <branch>)
tree=$(git rev-parse <branch>^{tree})
squash=$(printf 'TEMP SQUASH %s\n' <branch> | git commit-tree "$tree" -p "$base")
```

### Case B: branch-backed dirty worktree

Use the **current worktree state**, not only the branch tip:

```bash
base=$(git merge-base origin/main <branch>)
tmpidx=$(mktemp)
idxpath=$(git -C <worktree> rev-parse --git-path index)
cp "$idxpath" "$tmpidx"
GIT_INDEX_FILE="$tmpidx" git -C <worktree> add -A
worktree_tree=$(GIT_INDEX_FILE="$tmpidx" git -C <worktree> write-tree)
rm -f "$tmpidx"
squash=$(printf 'TEMP SQUASH %s\n' <label> | git commit-tree "$worktree_tree" -p "$base")
```

This captures tracked + untracked current changes as a single net patch without rewriting the real branch.

## Main comparison and rebase test

Inspect the squash patch against latest main:

```bash
git diff --stat --find-renames origin/main...$squash --
git diff --name-status --find-renames origin/main...$squash --
git cherry origin/main $squash || true
```

Then test portability in a disposable detached worktree:

```bash
tmp=$(mktemp -d)
wt="$tmp/rebase-check"
git worktree add --detach "$wt" "$squash"
git -C "$wt" rebase origin/main
```

If rebase fails, inspect conflict surface:

```bash
git -C "$wt" status --short --branch
```

Abort and remove the disposable worktree afterward.

## Classification rubric

### 1. Valid branch / meaningful local work

Typical signals:
- branch or worktree is tied to an open PR, or
- synthetic squash leaves a coherent net patch vs latest main, and
- disposable rebase onto latest main is clean or nearly clean, and
- the diff is not just a no-op alias of main or an already-merged residue

Good summary label:
- `valid branch: squash patch rebases cleanly onto latest main`

### 2. Stale branch history + meaningful current local patch

Typical signals:
- no open PR, or old PR already merged/closed
- committed branch history itself looks stale or conflicts broadly
- but the current dirty worktree contains a narrow, coherent patch
- synthetic squash built from current worktree state rebases cleanly or at least much better than the raw branch history

Handling:
- preserve the worktree or transplant the current patch onto a fresh latest-main branch
- do not delete automatically

Good summary label:
- `stale branch history + meaningful current local patch`

### 3. Merged residue / stale helper alias / stale no-op clone

Typical signals:
- no open PR
- worktree clean
- associated PR is already `MERGED`
- or local branch is merely an alias of another open PR branch or of `origin/main`
- or `git cherry origin/main <branch>` shows the work is already absorbed
- or synthetic squash is effectively empty / already absorbed / conflicts broadly as obsolete history

Common subtypes:
- `merged PR residue with clean worktree`
- `stale detached helper clone at merged PR head`
- `stale alias branch == open PR head SHA`
- `stale no-op alias: branch == origin/main`

Handling:
- delete stale worktree first
- then delete local branch

## Detached worktree rules

### Keep detached worktree if:
- it is dirty with real source/test/doc changes
- its current local patch is meaningful and not safely represented elsewhere
- it is the only place preserving meaningful local unpublished work

### Remove detached worktree if:
- it is clean and exactly matches a merged PR head commit
- it is a clean redundant helper clone of an open PR whose authoritative branch-backed worktree remains elsewhere
- it is a clean stale helper ancestor in a detached helper chain for the same PR

Useful checks:

```bash
git -C <path> rev-parse HEAD
git branch --contains <sha>
gh pr view <number> --json number,state,headRefName,headRefOid,mergeCommit,url
```

## Open PR branch rules

By default, keep open PR branches/worktrees.

But still remove redundant local aliases or helper clones when all are true:
- branch name is not the actual open PR head branch name
- local alias SHA equals the open PR `headRefOid`, or equals another preserved authoritative local branch/worktree state
- worktree is clean

Do not preserve duplicate local aliases just because they point to the PR head.

## Deletion sequence

Only after classification is complete and refreshed:

1. remove safe stale detached worktrees
2. remove safe stale branch-backed worktrees that are clean and not needed
3. run `git worktree prune`
4. delete stale local branches

Commands:

## When one backup branch is worth promoting instead of deleting

A common end-state after repo-local cleanup is:
- several `backup/*` branches were reviewed together
- one or two are clearly stale or redundant and should be deleted
- exactly one backup branch still carries a small meaningful net patch
- the user wants the repo left in a nearly-final clean state, which means the meaningful backup should become a normal reviewable branch instead of staying under `backup/*`

Recommended handling:
1. delete clearly stale sibling backup branches/worktrees first
2. rename the kept backup branch out of the `backup/` namespace to a normal branch name that matches its real purpose, for example:
   - `docs/...` for repo-local skill/docs follow-ups
   - `fix/...` or `refactor/...` for code follow-ups
3. if it has an attached worktree, rename the branch from that worktree context
4. rebase the promoted branch onto latest `origin/main`
5. push it as a new remote branch
6. create a PR immediately if the user's requested cleanup includes "promote if valuable"
7. after the promotion is safely pushed/reviewable, fast-forward root `main` to latest `origin/main` if clean

Example command pattern:

```bash
git -C <kept-worktree> branch -m docs/<descriptive-name>
git -C <kept-worktree> rebase origin/main
git -C <kept-worktree> push -u origin docs/<descriptive-name>
gh pr create --base main --head docs/<descriptive-name> ...
```

Useful summary label:
- `meaningful backup promoted to reviewable branch/PR`

Important interpretation:
- a meaningful backup branch should not be left indefinitely under `backup/*` once its value has been confirmed and the user asked for promotion
- promoting the surviving backup while deleting the weaker siblings is often the cleanest "almost final" workspace state

## Practical cleanup pitfall: disposable synthetic-rebase helper worktrees can leak if the audit script aborts mid-run

When using synthetic squash + disposable rebase-check worktrees, an interrupted script or tool error can leave behind temporary detached worktrees such as:
- `/tmp/.../rebase-check`
- other mktemp-based detached helper paths

Do not ignore these in the final report.
Before finishing, re-run `git worktree list --porcelain` and remove any leftover temporary detached helper that was created only for the audit itself.

Typical cleanup:

```bash
git worktree remove --force /tmp/.../rebase-check
git worktree prune
```

Useful summary label:
- `stale synthetic-rebase helper removed`

```bash
git worktree remove <path>
git worktree remove --force <path>
git worktree prune
git branch -d <branch>
git branch -D <branch>
```

Use `-D` only when stale status is already proven by merged/closed PR evidence, alias/no-op evidence, or already-absorbed cherry evidence.

## Refresh-before-delete rule

Before any destructive batch, refresh again:

```bash
git fetch origin --prune
gh pr list --state open --json number,headRefName,headRefOid,title,url
git branch -vv --no-abbrev
git worktree list --porcelain
```

This avoids deleting something that became the active PR head mid-session.

## Final reporting format

For each branch reviewed, report:
- branch name
- attached worktree path if any
- open PR status
- current dirty/clean state
- net squash diff summary vs latest main
- rebase result onto latest main
- classification
- action taken

Then summarize:
- deleted stale worktrees
- deleted stale branches
- remaining worktrees
- remaining local branches
- remaining dirty local changes
- whether root `main` is clean and whether it matches latest `origin/main`

## Practical lessons captured from repeated corp-web-japan cleanup

- Non-open-PR branches should be treated as stale candidates by default, not preserved by default.
- The user wants branch validity judged by **synthetic squash portability onto latest main**, not by raw branch age or raw ahead/behind alone.
- `git diff origin/main..branch` and the squash diff answer a better question than commit counts: what net change still remains right now?
- A merged branch can still contain historically meaningful work, but if there is no surviving local dirty patch and the PR is merged, that is usually stale residue and should be deleted.
- A dirty detached worktree can still be meaningful even when its related branch history is stale; preserve the patch, not the stale lineage.
- Root `main` often carries meaningful local skill/doc edits during cleanup. Preserve them intentionally rather than force-cleaning `main` blindly.
- Open PR helper aliases and detached clones should be reduced aggressively when they are clean duplicates.
- In fast-moving repos, an open PR can merge while cleanup/rebase work is still in progress. Re-fetch and re-check PR state immediately before acting on any previously-open local branch.
- A no-open-PR branch that looked like a no-op alias earlier in the session can stop being stale before deletion if another session or actor rewrites the attached worktree/branch in place. Re-run the live branch/worktree snapshot right before deletion, not just the PR snapshot.
- Additional practical case: a branch can look like a no-PR local cleanup candidate at delete time, yet appear as an open remote PR immediately afterward because another actor opened/pushed it during the cleanup window or GitHub state changed between snapshots.
- Handling rule for that case:
  - base the local deletion decision on the exact refreshed pre-delete snapshot you verified
  - refresh open PR state again after the destructive batch
  - if the just-deleted branch now shows an open PR remotely, report it explicitly as `local branch/worktree deleted, remote PR still open/now visible`
  - keep local cleanup and remote PR lifecycle as separate facts; deleting a local branch/worktree does not close the PR
- Practical stale case: if a once-open local branch's remote head disappears after fetch, `gh pr list --state all --head <branch>` now shows `MERGED`, and `git diff develop..branch` (or the repo default branch equivalent) is empty, remove both the linked worktree and local branch as merged residue.
- Practical preservation case: if a no-open-PR candidate later reappears under a different branch/worktree name with a small real diff vs latest `origin/main` and its synthetic squash rebases cleanly, reclassify it as a `meaningful unpublished branch` instead of deleting it from the earlier stale verdict.
- Additional repeated-cleanup case from active PR repos: between follow-up `workspace 정리` turns, the remaining local line can change class entirely.
  - A previously preserved non-PR dirty worktree can later become the head branch of a newly opened PR; once that happens, stop treating it as a stale candidate and preserve it as the active PR line.
  - At the same time, other local worktrees that were formerly open-PR or recently created docs/fix branches can flip to `upstream gone + clean + PR merged` and become safe stale residue.
  - Another late-appearing stale form is a clean branch-backed worktree whose branch has no PR and points at exactly the same SHA as `main` and `origin/main`; treat that as a no-op alias and delete it.
  - Therefore, on each repeated repo-local cleanup turn, do not continue from the old classification table. Re-run a full fresh pass and keep pruning until the live state reaches the minimum safe set for that moment.
  - Useful end-state label:
    - `root main + currently open PR worktrees only`
- Additional practical case from `skills-jk` cleanup: unattached `backup/*` branches should not be preserved just because they were once created to save local root edits.
  - Signal pattern:
    - no attached worktree
    - no open PR
    - synthetic squash vs latest `origin/main` still shows an old net patch, but disposable rebase onto latest `origin/main` conflicts broadly across many older skill/memory files
    - meanwhile the actually relevant live local work now exists elsewhere, such as a current dirty root worktree, a separate dirty follow-up worktree, or a newer open-PR follow-up branch
  - Recommended handling:
    1. treat the backup branch as a stale preservation artifact rather than as active work by default
    2. confirm that the meaningful current local edits are already represented in a kept live worktree or newer branch
    3. if the backup branch has no attached worktree and no unique current local patch to protect, delete the backup branch even if it once represented a meaningful preservation snapshot
  - Useful summary label:
    - `stale unattached backup residue`
- Additional practical case: when a dirty worktree on a merged/stale branch still looks meaningful, create a fresh latest-main spike worktree and transplant only the current dirty patch before deciding whether the change still matters.
  - Signal pattern:
    - the original branch/worktree has no open PR and old branch history is clearly stale or already merged
    - the live worktree still has a focused dirty patch in a small set of files
    - synthetic rebase of the whole worktree-state squash onto latest `origin/main` conflicts broadly, making it hard to tell whether the current local idea still has value
  - Recommended handling:
    1. create a fresh worktree from latest `origin/main` on a clearly temporary branch such as `spike/<topic>-latest`
    2. copy only the currently dirty tracked files plus intentional untracked source files from the stale worktree into that fresh worktree
    3. inspect the resulting residual diff against latest main
    4. classify the transplanted result separately from the original stale branch history:
       - if the residual diff is empty or trivial, the old dirty patch is mostly stale residue
       - if the residual diff still expresses a coherent design or implementation direction, it remains meaningful even though the old branch lineage should be retired
       - if some copied files become orphaned or unwired on latest main, split them from the meaningful subset before deciding what to keep
  - Useful summary labels:
    - `meaningful residual patch on fresh latest-main spike`
    - `stale branch history, residual patch still meaningful`
    - `orphan residual files after latest-main transplant`
  - Practical interpretation:
    - this latest-main transplant is not a publishing step; it is an adjudication tool for deciding whether a stale dirty branch still contains value
    - it is especially useful when the user's real question is not "can this old branch rebase cleanly?" but "does the current local idea still mean anything on today's main?"
- Practical rebase case: when rebasing a docs/content branch onto a newer base that renamed a directory, Git may stop with `CONFLICT (file location)` for files that were originally added under the old path. If there is no textual conflict and the resolution is simply to keep the files under the new renamed directory, stage those files at the new path and continue the rebase instead of aborting.
- Additional repeated-cleanup case from `skills-jk`: a local branch can be a pure no-op alias of `main` / `origin/main` while its attached worktree still contains a meaningful dirty patch.
  - Signal pattern:
    - `git rev-parse <branch>` equals `main` and `origin/main`
    - `git rev-list --left-right --count origin/main...<branch>` is `0 0`
    - no open PR exists for the branch name
    - but `git -C <worktree> status --short --branch` and `git -C <worktree> diff --stat` show a real focused local patch
  - Classification:
    - `stale branch pointer + meaningful local dirty patch`
  - Recommended handling:
    1. build the synthetic squash from the current dirty worktree state, not the branch tip
    2. if that worktree-state squash rebases cleanly onto latest `origin/main`, preserve the patch by transplanting it onto a fresh latest-main branch/worktree
    3. commit/push/open a PR from the fresh branch if the user asked for reviewable output
    4. only after the patch is safely preserved, restore/remove the original alias worktree and delete the alias branch
  - Useful summary label:
    - `stale alias branch promoted via fresh latest-main branch carrying the real dirty patch`
- Additional repeated-cleanup case from `skills-jk`: a local-only preserve branch can look broad or stale because it still carries historical deletions from older lines, while its latest-main-portable payload is actually much smaller.
  - Signal pattern:
    - no open PR
    - the preserved branch diff vs `origin/main` includes old deletions or unrelated historical files from previously merged helper lines
    - synthetic squash vs latest `origin/main` collapses to a smaller surviving payload
    - disposable rebase of that squash onto latest `origin/main` is clean
  - Recommended handling:
    1. do not open a PR directly from the old preserve branch just because it is ahead and rebases
    2. inspect the squash diff, not only the raw branch diff, to identify the surviving latest-main payload
    3. create a fresh latest-main branch/worktree and transplant only the surviving files there
    4. commit/push/open the PR from that fresh branch
    5. after the fresh branch is safely reviewable, delete the superseded preserve branch/worktree
  - Useful summary labels:
    - `preserve branch history broad, surviving latest-main payload narrow`
    - `latest-main transplant dropped stale historical deletions`
  - A useful next-step pairing is to patch the PR-creation workflow skill too, because the fresh latest-main transplant often changes how many PRs should be opened and whether an existing skill-followup PR branch should be updated instead of creating another docs PR.

## Good trigger phrases

This skill should be loaded when the user asks things like:
- `현재 worktree, branch, local changes 현황을 요약하여 보고해줘`
- `Open PR 이 아닌 worktree, branch 는 stale 가능성이 높아`
- `각 브랜치마다 진행하고`
- `main branch head 와 비교하여 stale 여부를 판별해줘`
- `로컬 변경사항을 모두 하나의 commit 으로 squash 한 이후`
- `rebase onto the latest main branch 시도하면서`
- `유의미한 변경사항인지 판별해줘`
- `stale branch, worktree 를 삭제해줘`

## Related skills

Load these when they also apply:
- `safe-git-worktree-branch-cleanup` for broader cleanup heuristics and reporting structure
- `workspace-stale-git-cleanup` only when the scope is truly many repositories under one workspace root

Overlap note:
- this skill and `safe-git-worktree-branch-cleanup` now share a large amount of repo-local cleanup guidance; if they keep growing, future consolidation may be worth considering, with this skill remaining the squash/rebase-heavy adjudication path
