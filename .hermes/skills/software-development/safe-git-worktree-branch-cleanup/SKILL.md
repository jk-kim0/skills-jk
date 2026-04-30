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

Counter-signal that should usually preserve a branch-backed worktree even with no PR:
- the worktree has real tracked modifications or meaningful untracked source files
- the branch appears to be an active local exploratory/refactor branch not yet published
- the local branch tracks a differently named upstream branch, indicating temporary local branch reshaping rather than stale residue

Important practical lessons:
- Do not assume every branch-backed worktree should be preserved.
- But also do not assume "no open PR" means removable; a dirty branch-backed worktree may be active unpublished work.
- In PR-heavy repos, the real source of truth is the combination of open PR head branches plus actual local worktree dirtiness, not merely whether a branch is attached to a worktree.

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

Check for obviously disposable artifacts such as:
- `.tmp-pr-body.md`
- temporary comment/body markdown files
- untracked agent runtime directories like `.hermes/` when they are clearly local tool state rather than repo source
- other one-off helper files clearly unrelated to source changes

Practical rule:
- if the only dirt is disposable untracked helper state, remove it or classify it separately and re-check `git status --porcelain`
- if the remaining dirt is real project files (for example tracked deletions like `D postcss.config.mjs`), preserve the worktree

Be especially careful with `.hermes/`-style directories:
- they are often safe to ignore for stale classification, but confirm they are untracked local runtime artifacts before deleting
- if you are not confident they are disposable, preserve the worktree and report it
- if `.hermes/` is the only remaining dirt and the associated remote branch/PR is already merged, treat the worktree as stale and remove it with `git worktree remove --force ...` if needed

Do not delete dirty worktrees automatically if the remaining changes are real project files.

## 7a. Detached worktrees may need verification beyond `git status`

A detached worktree can look clean in a simple `git status --short --branch` snapshot, yet `git worktree remove <path>` may still refuse with:

```bash
contains modified or untracked files, use --force to delete it
```

When this happens, do not immediately force-remove blindly. First inspect inside the worktree:

```bash
git -C <path> status --short --branch
git -C <path> diff --stat || true
git -C <path> ls-files --others --exclude-standard || true
```

Interpretation:
- if `diff --stat` is empty and `ls-files --others` is empty, the refusal is just conservative Git behavior and `git worktree remove --force <path>` is acceptable
- if tracked diffs or untracked files exist, preserve the worktree unless those files are clearly disposable temp artifacts

This case showed up with detached PR follow-up worktrees that were effectively clean but still required `--force` to remove.

## 7b. Root-worktree dirty files may actually be residue from another kept worktree

In PR-heavy repos, the primary/root worktree on `main` can accumulate tracked-file edits that are not true `main` work. They may be accidental spillover from an open-PR worktree or another local worktree.

Before deciding that root tracked-file changes must be preserved, compare them against relevant kept worktrees:

```bash
git diff --name-only
```

For each dirty tracked file, compare the root file against the corresponding file in likely source worktrees, especially open-PR worktrees:

```bash
git diff --no-index -- path/in/root path/in/other/worktree || true
```

Interpretation:
- if files are identical, the root change is very likely residue copied from that worktree
- if the diff is very small and clearly the same direction of change, treat it as likely residue/intermediate state and inspect before preserving
- if the file differs materially from every kept worktree, treat it as genuine root-local work and preserve it

This check is especially important before restoring dirty tracked files in `main` so that `main` can be fast-forwarded to `origin/main` safely.

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

If a stale entry is already marked `prunable` and its linked `.git`/gitdir is broken or missing, `git worktree remove` may fail validation instead of cleaning it up. In that case, do not force repeated removal attempts; rely on prune from the owning repo:

```bash
git worktree prune
```

After batch removal:

```bash
git worktree prune
```

### Delete safe local branches

Use non-force delete first:

```bash
git branch -d <branch>
```

If `-d` refuses, do not immediately keep the branch by default. First verify whether all of the following are true:
- the branch is no longer attached to any kept worktree
- `gh pr list --state all --head <branch>` confirms the PR is already merged or closed
- the upstream ref is already gone or otherwise no longer authoritative
- `git cherry origin/main <branch>` shows the branch is only carrying squash/rebase residue rather than active unpublished work

When those checks confirm the branch is just post-merge local residue, force-delete is appropriate:

```bash
git branch -D <branch>
```

Only preserve the branch when those checks do not clearly prove it is stale.

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
