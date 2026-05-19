# Stacked PR cleanup after parent/base work lands

Use this when an open child PR was originally stacked on a parent/foundation PR, and the parent has since landed on `main`.

## Current-state diagnosis

Run these before changing the branch:

```bash
gh pr view <child-pr> --json state,headRefName,baseRefName,headRefOid,mergeStateStatus,commits,files,url
git fetch origin --prune
git diff --stat origin/main...HEAD
git diff --name-status origin/main...HEAD
git log --oneline --decorate --graph origin/main..HEAD
```

Signals that the child PR still carries parent history:

- `gh pr view` shows multiple commits where one belongs to the landed parent PR.
- The file list includes parent/foundation files that should already be on `main`.
- `git diff origin/main...HEAD` is much larger than the intended child scope.

## Rebuild pattern

1. Keep the same open PR head branch; do not open a replacement PR unless the user asks.
2. Save or identify the child-only patch/commit.
3. Rebuild the branch on latest `origin/main` using a controlled reset/cherry-pick/reapply-from-patch flow.
4. Prefer a single clean commit when the PR no longer needs staged review history.
5. Force-push with lease to the existing PR branch.

## Required verification before reporting success

```bash
git fetch origin --prune
git merge-base HEAD origin/main
git rev-parse origin/main
git rev-list --left-right --count origin/main...HEAD
git diff --name-status origin/main...HEAD
git ls-remote origin refs/heads/<child-branch>
gh pr view <child-pr> --json headRefOid,baseRefName,mergeStateStatus,statusCheckRollup,files,url
```

Expected result:

- `git merge-base HEAD origin/main` equals `git rev-parse origin/main`.
- `git rev-list --left-right --count origin/main...HEAD` is `0 N`, usually `0 1` for one cleaned follow-up commit.
- PR files contain only the child PR scope.
- The remote head SHA matches local `HEAD`.

## PR metadata cleanup

After flattening/rebuilding the branch, update the PR body if it still says the PR is stacked or depends on a parent branch. The body should describe the current standalone diff and test plan.

Do not report `mergeStateStatus=BLOCKED` as a conflict by itself. After a force-push/rebase, `BLOCKED` commonly means required checks or preview deployment are pending. Inspect `statusCheckRollup`/`gh pr checks` first, and report pending checks separately from merge conflicts.
