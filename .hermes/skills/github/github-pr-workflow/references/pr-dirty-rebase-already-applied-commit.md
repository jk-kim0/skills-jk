# PR mergeStateStatus DIRTY when earlier PR commits already landed on main

Use this pattern when an open PR shows `mergeStateStatus: DIRTY` or merge conflicts even though checks are green, especially after the PR was stacked on another branch or contains commits that may already have merged to `main`.

## Investigation

1. Fetch the latest base and PR head explicitly:
   - `git fetch origin main pull/<PR>/head:<local-branch> --force`
2. Inspect the PR metadata before editing:
   - `gh pr view <PR> --json number,title,state,headRefName,baseRefName,headRefOid,mergeStateStatus,statusCheckRollup,url`
3. Compare PR head against latest main in the PR worktree:
   - `git log --oneline --decorate --left-right --cherry-pick origin/main...HEAD`
   - `git diff --name-only origin/main...HEAD`
4. If a suitable existing worktree for the PR branch exists and is clean, reuse it; otherwise create a branch-isolated worktree.

## Fix pattern

1. Run `git rebase origin/main` in the clean PR worktree.
2. If Git reports `warning: skipped previously applied commit <sha>`, treat it as a normal outcome when that commit already landed on main. Do not reapply it unless the skipped commit is still part of the requested PR scope.
3. Confirm the resulting diff only contains the remaining PR-scoped changes:
   - `git status --short --branch`
   - `git log --oneline --decorate --left-right --cherry-pick origin/main...HEAD`
   - `git diff --name-only origin/main...HEAD`
4. Push with lease:
   - `git push --force-with-lease origin <branch>`
5. Re-query the PR head and merge state:
   - `gh pr view <PR> --json headRefOid,mergeStateStatus,statusCheckRollup,url`

## Reporting

After a force-push, `mergeStateStatus` may move from `DIRTY` to `BLOCKED` while new checks are queued or running. Report this as a successful conflict/rebase fix with checks pending, not as a new merge conflict. Start a background `gh pr checks <PR> --watch --fail-fast` watcher only if useful, and do not passively wait for long CI runs unless the user asked you to watch.