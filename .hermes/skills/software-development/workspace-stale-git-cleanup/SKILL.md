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

## Conservative stale classification

### Worktree candidates

Mark as removable only when one of these is true:
- `prunable` in `git worktree list --porcelain`
- detached worktree with clean `git status --porcelain`

Keep if:
- detached but dirty
- branch-backed worktree
- main/top-level repo even if detached

### Branch candidates

Mark as removable only when one of these is true:
- local branch has upstream `[gone]` in `git branch -vv` and is not checked out anywhere
- local branch is fully merged into the repo default branch and is not checked out anywhere

Exclude by default:
- current branch
- any branch present in any worktree
- `main`, `master`, `develop`, `release`, `alpha`

## Important command pitfall

When removing a worktree, run the command from the owning repo context:

```bash
git -C /path/to/main/repo worktree remove --force /path/to/worktree
```

Do not run plain `git worktree remove ...` from an arbitrary non-repo directory. That can fail with `fatal: not a git repository`.

## Recommended execution order

1. Report what is being checked.
2. Discover repos and candidates.
3. Remove only clearly safe stale worktrees first.
4. Run `git -C <repo> worktree prune` after removals.
5. Delete clearly stale local branches.
6. Re-run `git worktree list --porcelain` and `git branch -vv` to verify the result.
7. Summarize what was deleted and what was intentionally left alone.

## Good final-report format

- Deleted stale worktrees
- Deleted stale branches
- Verification result
- Intentionally preserved items and why

## Example preserved items

- detached worktree with untracked temp files
- generic local branch names with possible policy meaning
- top-level repo in detached HEAD state
