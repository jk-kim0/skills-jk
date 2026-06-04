# Single PR latest-main rebase race

When a user asks to rebase one PR onto the latest `main`, `main` can advance while the branch is being rebased, verified, or force-pushed.

Recommended sequence:

1. Fetch before rebase: `git fetch origin main <branch>`.
2. Rebase the PR branch: `git rebase origin/main`.
3. Verify the local base: `git merge-base --is-ancestor origin/main HEAD`.
4. Push with lease: `git push --force-with-lease origin <branch>`.
5. Immediately re-query GitHub: `gh pr view <pr> --json headRefOid,baseRefOid,mergeStateStatus,statusCheckRollup`.
6. Fetch `origin/main` again and compare it to the PR `baseRefOid`.
7. If they differ, `main` moved during the rebase/push window; repeat fetch/rebase/verify/push before saying the PR is on latest main.
8. After force-push, ignore check output attached to the old head SHA. Re-query or watch checks for the new `headRefOid`.

This is especially easy to miss when the first post-push `mergeStateStatus` changes from `DIRTY` to `BLOCKED`: `BLOCKED` may simply mean required checks are pending, but the PR may also already be based on a newer base SHA than the local `origin/main` snapshot used before push.