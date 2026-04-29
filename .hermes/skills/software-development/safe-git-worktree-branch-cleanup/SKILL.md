---
name: safe-git-worktree-branch-cleanup
description: Safely update local main and clean stale local git branches/worktrees without deleting dirty or still-attached work.
version: 1.0.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, worktree, branch, cleanup, maintenance, safety]
---

# Safe git worktree/branch cleanup

Use when the user asks to:
- update `main`
- clean stale local branches
- clean stale worktrees
- prune local git state safely

This workflow is for repositories that may have many old worktrees, detached review trees, and branches whose upstream refs were pruned.

## Goals

1. Update local `main` to match `origin/main`
2. Remove only clearly safe stale worktrees
3. Remove only clearly safe stale local branches
4. Preserve dirty worktrees, active work, and unmerged branches

## Safety rules

- Never delete the current branch.
- Never delete a dirty worktree automatically.
- Never delete a branch still attached to any worktree.
- Never delete a branch that is not merged into `origin/main` unless the user explicitly asks for aggressive cleanup.
- If the starting directory is not a git repo, first identify the target repo instead of guessing silently.
- If multiple repos exist under a workspace, ask which repo to target when possible.
- If the user does not answer and you must proceed, state the default repo choice explicitly.

## Procedure

### 1. Confirm repo context

Run:

```bash
pwd
git rev-parse --show-toplevel
```

If not a repo, discover likely repositories or worktrees under the workspace using repository-aware search tools before proceeding.

### 2. Inspect current repo state

Run:

```bash
git branch --show-current
git status --short --branch
git remote -v
git worktree list --porcelain
git for-each-ref --format='%(refname:short)|%(upstream:short)|%(committerdate:iso8601)|%(subject)' refs/heads
```

This reveals:
- current branch
- dirty root repo state
- all linked worktrees
- branch/upstream relationships

### 3. Refresh remote refs

Run:

```bash
git fetch origin --prune
```

Then check:

```bash
git rev-parse main
git rev-parse origin/main
git branch --merged origin/main
```

Also identify branches whose upstream ref was removed:

```bash
for b in $(git for-each-ref --format='%(refname:short)' refs/heads); do
  u=$(git for-each-ref --format='%(upstream:short)' refs/heads/$b)
  if [ -n "$u" ] && ! git show-ref --verify --quiet refs/remotes/$u; then
    echo "$b|$u"
  fi
done
```

## 4. Classify worktrees

For each worktree, collect:
- path
- branch or detached state
- whether it is dirty
- a short status preview

Only treat a worktree as immediately removable when all are true:
- detached HEAD
- clean working tree
- not the primary active worktree

Do not remove:
- any dirty worktree
- any branch-attached worktree unless the branch is explicitly being retired and the tree is clean

## 5. Cross-check open PR reality before deciding what to keep

In repositories that use many temporary worktrees for PR follow-up, a branch-attached worktree is often still stale even though it is not detached.

Before preserving branch-backed worktrees, query actual open PRs and compare them to local branch/worktree state.

If GitHub CLI is available:

```bash
gh pr list --state open --json number,title,headRefName,isDraft,url
```

Then classify each branch-backed worktree using this stricter order:

1. keep the current repo worktree
2. keep any truly dirty worktree with real user changes
3. keep a worktree whose branch matches an open PR head branch
4. remove a clean worktree whose branch has no open PR and is clearly old/stale

Strong stale signals for branch-backed worktrees:
- no open PR for the branch
- upstream ref is gone after `git fetch --prune`
- `gh pr list --state all --head <branch>` shows the PR was already merged/closed
- the branch tip is already equivalent to `origin/main`
- the worktree only exists for an old review/rebase/squash/follow-up context

Important practical lesson:
- Do not assume every branch-backed worktree should be preserved.
- In PR-heavy repos, the real source of truth is the set of currently open PR head branches, not merely whether a branch is attached to a worktree.

## 6. Classify branches

For each local branch, determine:
- merged into `origin/main` or not
- attached to a worktree or not
- protected/current branch or not
- whether upstream still exists
- ahead count vs `origin/main`
- whether it corresponds to an open PR head branch
- whether any PR for that branch is already merged/closed

A local branch is safe to delete only when all are true:
- not current branch
- not `main`
- not needed by any open PR
- not attached to any worktree that must be kept
- either merged into `origin/main`, or confirmed as stale residue from an already merged/closed PR that no longer needs local preservation

Notes:
- Upstream being gone is not enough to delete by itself.
- A branch may have a stale or mismatched upstream; merge status, PR state, and worktree attachment matter more.
- `git cherry origin/main <branch>` is useful when a squash/rebase merge means the branch is not a direct ancestor of `origin/main` even though its PR is already merged.

## 7. Dirty-worktree false positives to check before preserving

Some worktrees look dirty only because of transient helper files created during agent workflows.

Check for small obviously disposable artifacts such as:
- `.tmp-pr-body.md`
- temporary comment/body markdown files
- other one-off helper files clearly unrelated to source changes

If such a file is the only dirty item, remove it, re-check `git status --porcelain`, and then treat the worktree according to normal stale rules.

Do not delete dirty worktrees automatically if the remaining changes are real project files.

## 8. Update local main safely

If `main` is not checked out in any worktree, update it directly:

```bash
git branch -f main origin/main
```

This is faster and safer than checking out `main` in a busy multi-worktree repo.

Verify:

```bash
git rev-parse main
git rev-parse origin/main
```

They should match.

## 7. Apply cleanup

### Remove safe detached clean worktrees

```bash
git worktree remove <path>
```

After batch removal:

```bash
git worktree prune
```

### Delete safe local branches

Use non-force delete:

```bash
git branch -d <branch>
```

If `-d` refuses, keep the branch unless the user explicitly requested aggressive cleanup.

## 8. Final verification

Run:

```bash
git rev-parse main
git rev-parse origin/main
git branch --show-current
git worktree list
```

Also report remaining dirty worktrees explicitly so the user can decide on follow-up cleanup.

## Recommended reporting format

Report:
- target repo used
- whether `main` now matches `origin/main`
- number of worktrees removed
- branches deleted
- remaining dirty worktrees
- anything preserved intentionally for safety

## Practical lessons

- In a large multi-worktree repo, most safe wins come from removing clean detached review/rebase/squash worktrees first.
- Dirty worktrees often contain half-finished or forgotten work; preserve them by default.
- `git fetch --prune` can make many upstreams appear "gone"; do not treat that alone as permission to delete local branches.
- If the workspace root is not a repo, repository discovery is a prerequisite, not an optional convenience.
