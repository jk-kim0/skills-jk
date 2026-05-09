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
