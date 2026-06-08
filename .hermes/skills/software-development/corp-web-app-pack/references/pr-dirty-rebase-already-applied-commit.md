# PR DIRTY rebase when earlier commits already landed on main

Use this for corp-web-app PRs that show `mergeStateStatus: DIRTY` or conflicts while checks are otherwise green, especially stacked/follow-up PRs where earlier commits may already have merged to `main`.

## Steps

1. Confirm the active repo/worktree and fetch latest base plus PR head:
   - `git fetch origin main pull/<PR>/head:<local-branch> --force`
2. Inspect metadata and checks:
   - `gh pr view <PR> --json number,title,state,headRefName,baseRefName,headRefOid,mergeStateStatus,statusCheckRollup,url`
3. In a clean PR worktree, compare against latest main:
   - `git log --oneline --decorate --left-right --cherry-pick origin/main...HEAD`
   - `git diff --name-only origin/main...HEAD`
4. Run `git rebase origin/main`.
5. If rebase says `warning: skipped previously applied commit <sha>`, that is expected when an earlier stacked commit already landed on main. Do not reapply it unless it is still in scope.
6. Verify the post-rebase diff contains only the remaining PR-scoped files, then push:
   - `git push --force-with-lease origin <branch>`
7. Re-query the PR head and merge state. `BLOCKED` immediately after push usually means newly queued/running checks, not unresolved conflicts.

## User-facing reporting

Keep the update short: say the conflict state was cleared by rebasing onto latest main, mention any skipped already-applied commit, report the new head SHA, and state which checks are pending/running. Do not wait passively for long CI; start a background watcher if helpful.