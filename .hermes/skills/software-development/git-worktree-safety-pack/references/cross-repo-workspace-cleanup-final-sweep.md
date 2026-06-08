# Cross-repo workspace cleanup final sweep

Use this reference when the user asks to clean every repository under a workspace root such as `/Users/jk/workspace`, not just the current repo.

## Durable workflow

1. Deduplicate immediate child directories by `git rev-parse --git-common-dir` so linked worktrees are not processed as independent owner repos.
2. For each owner repo, fetch/prune, detect the remote default branch, and fast-forward the root checkout only when the root worktree is clean.
3. Remove only conservative stale residue automatically:
   - clean worktrees whose branch has merged PR evidence;
   - clean detached/prunable worktrees;
   - unattached local branches with merged/no-op/ancestor evidence;
   - clean branch-backed worktrees whose branch exactly equals the remote default and has no open PR.
4. Preserve dirty roots and dirty worktrees until their payload is classified. Do not delete or reset them just to make the sweep look complete.

## Dirty root with stale baseline after recently merged preservation PRs

In a cross-repo sweep, a root checkout can be cleanly on `main` but behind `origin/main` while also dirty with authored skill/docs changes. After related preservation PRs merge, `git diff origin/main` from the stale root can show broad deletion hunks for files that are already present on latest main.

Handling pattern:

1. Compare the dirty root against both `HEAD` and `origin/main`.
2. Treat broad `D` hunks and formatter/script churn from the stale baseline as suspicious until proven meaningful.
3. Select only authored payload that still exists in the dirty root and is not already represented on latest `origin/main` or an open preservation PR.
4. Create a fresh latest-`origin/main` worktree/branch.
5. Copy or patch only the selected authored files into that fresh worktree, then inspect `git diff --stat`, `git diff --name-status`, and `git diff --check` before committing.
6. Push and create/update the review PR using the repo’s normal PR mechanism.
7. Verify the PR head SHA and payload file list.
8. Only then reset/clean the root duplicate copy and fast-forward root `main`.

## Final duplicate-origin standalone clone sweep

Do not stop after owner-repo worktree/branch pruning. Re-scan immediate child directories under the workspace root and group them by `git remote get-url origin`.

A sibling directory is safe to remove as redundant local residue only when all are true:

- another canonical sibling checkout with the same origin remains;
- the candidate is a standalone clone, not a registered linked worktree with nested children;
- the candidate is on the remote default branch;
- `git status --porcelain` is clean;
- `HEAD` equals the remote default head;
- `git worktree list --porcelain` from the candidate shows no additional linked worktrees.

If any of those checks fail, preserve the directory and report why.

## Final verification

Before reporting completion, run a final workspace-level scan that reports:

- total immediate-child repos scanned;
- any repo whose root is dirty;
- any repo not on its remote default branch;
- any repo whose local default branch does not equal the remote default head;
- remaining duplicate-origin sibling groups;
- intentional open-PR worktrees that remain.

If the sweep preserved dirty root/worktree payload by creating or updating a PR, do not reuse an earlier scan as the final result. First verify the PR branch/head SHA and payload file list, then reset/clean the duplicate root copy, then rerun the workspace-level scan and duplicate-origin grouping. The final report should distinguish deleted stale residue from intentionally retained PR worktrees.

A clean final state means all owner repo roots are clean and aligned with their remote defaults, duplicate standalone clones have been removed or explicitly preserved, and remaining worktrees correspond to open PRs or meaningful unpublished work.