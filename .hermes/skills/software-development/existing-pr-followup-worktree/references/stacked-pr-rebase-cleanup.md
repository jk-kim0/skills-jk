# Stacked PR follow-up after parent/base work lands

Use this when an open PR was originally stacked on another PR or foundation branch, and that parent has since merged into `main`.

## Goal

Make the existing PR show only its own remaining work against the latest `origin/main`, without accidentally carrying the already-merged parent diff.

## Procedure

1. Confirm the PR is still open and identify its head branch and base branch with `gh pr view <number> --json state,headRefName,baseRefName,mergeStateStatus,commits`.
2. Fetch and fast-forward local `main`/`origin/main` before rewriting the PR branch.
3. In a fresh worktree for the existing PR branch, inspect the current diff:
   - `git diff --stat origin/main...HEAD`
   - `git diff --name-status origin/main...HEAD`
   - `git log --oneline --decorate --graph origin/main..HEAD`
4. If parent/foundation commits are still present after the parent PR merged, rebuild the PR branch on latest `origin/main` so only the child PR's intended patch remains. Prefer a controlled reset/cherry-pick or reapply from saved patch rather than merging main into the branch.
5. Verify the rewritten branch is cleanly based on latest main:
   - `git merge-base HEAD origin/main` should equal `origin/main`.
   - `git rev-list --left-right --count origin/main...HEAD` should show `0 N` where `N` is the intended number of PR commits.
6. Re-check the diff paths and content against the PR's requested scope before push.
7. Force-push with lease to the existing PR branch, not a new branch.
8. Update the PR body if it still describes stacked/base dependencies that are no longer true.
9. After push, verify the remote branch tip directly with `git ls-remote origin refs/heads/<branch>` if GitHub UI/API appears stale. Treat `BLOCKED` as possibly just pending required checks; inspect check status before assuming a conflict.

## Pitfalls

- Do not use current `origin/main` as a soft-reset point for a branch whose child work was based on an older parent unless you have first isolated the child patch; otherwise unrelated main-only changes can enter the PR.
- Do not open a replacement PR just because the PR was stacked. If it is open, keep the same PR branch unless the user explicitly asks otherwise.
- Do not leave parent PR language in the child PR description after the parent has landed; reviewers should see the current standalone scope.
