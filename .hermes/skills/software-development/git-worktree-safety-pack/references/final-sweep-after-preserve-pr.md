# Final sweep after preserving root-local changes in a PR

Use this when a `main 업데이트` / `workspace 정리` request finds meaningful root-local changes, preserves them in a branch/PR, and then needs the repository returned to a clean daily-use state.

## Pattern

1. After committing/pushing the preservation branch, verify the PR branch by remote ref, not only PR metadata:

```bash
git -C <preserve-worktree> rev-parse HEAD
git ls-remote origin refs/heads/<preserve-branch>
gh pr view <pr-number> --json headRefOid,files,statusCheckRollup,mergeStateStatus,reviewDecision
```

Treat `mergeStateStatus=BLOCKED` with an empty `statusCheckRollup` as a review/required-check-policy state until `gh pr checks` or workflow inspection proves there is a failing check.

2. Return to the root checkout and remove any residual tracked edits that were only inspection/copy artifacts, especially if the meaningful payload has already been copied into the preservation worktree/PR:

```bash
git -C <repo-root> status --short --branch
git -C <repo-root> restore -- <artifact-path>
git -C <repo-root> status --short --branch
```

Only restore after confirming the file's intended content exists in the PR branch or on latest `origin/main`.

3. Remove merged/stale worktrees and branches discovered during the sweep:

```bash
git -C <repo-root> worktree remove --force <repo-root>/.worktrees/<merged-worktree>
git -C <repo-root> branch -D <merged-branch>
git -C <repo-root> worktree prune
```

4. Final report must distinguish three states explicitly:

- root `main` is updated and clean (`git status --short --branch`, `git rev-parse main origin/main`)
- preservation PR branch/worktree remains because it backs an open PR
- merged/stale worktrees and branches were removed

## Pitfalls

- Do not declare workspace cleanup complete while the root checkout still contains a duplicate tracked edit that was already preserved in the PR branch.
- Do not delete the worktree/branch for the newly opened preservation PR; it is intentionally still live.
- Do not trust stale PR metadata alone after a push or body edit. Compare local HEAD, remote branch ref, and PR `headRefOid` before reporting success.
