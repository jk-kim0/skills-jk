# Batch rebase all open PRs onto latest main

Use this reference when the user asks to rebase all open PRs onto the latest `main` branch.

## Procedure

1. Start from a clean root checkout.
   - Run `git status --short --branch`.
   - Run `git fetch origin main --prune`.
   - Fast-forward local `main` with `git merge --ff-only origin/main` when safe.
2. Treat the open PR list as live and mutable.
   - List with `gh pr list --state open --json number,headRefName,baseRefName,isCrossRepository,url --limit 100`.
   - Skip merged/closed PRs.
   - Do not assume a PR that was open at the beginning is still open at the end.
3. For each same-repository PR branch:
   - Use an existing clean repo-root `.worktrees/<branch>` worktree when available.
   - Otherwise fetch/create a worktree for the head branch.
   - Verify the PR is still open before rebasing.
4. Run `git fetch origin main --prune` immediately before each branch rebase.
   - `origin/main` can advance while earlier PR branches are being rebased.
5. Rebase and resolve conflicts.
   - Run `git rebase origin/main`.
   - If conflicts occur, preserve both latest-main behavior and the PR's intended final state.
   - If an intermediate historical commit conflicts but a later PR commit already contains the intended final fix, inspect the remote PR head and carry forward the PR's final intent rather than blindly taking either side.
   - After staging conflict resolutions, use `GIT_EDITOR=true git rebase --continue` in non-interactive CLI sessions.
6. Push with lease.
   - Use `git push --force-with-lease origin <headRefName>` because rebase rewrites commit SHAs.
7. Final verification is mandatory.
   - Fetch `origin/main` again.
   - Re-list open PRs.
   - For every still-open PR branch, verify `git merge-base origin/main origin/<headRefName>` equals `origin/main`.
   - If any branch is behind current `origin/main`, rebase/push it again before reporting completion.
8. Final report should explicitly state:
   - Which PRs were rebased and pushed.
   - Which PRs disappeared because they were merged/closed during the sweep.
   - Any skipped cross-repo PRs.
   - Root `main` status.
   - Retained worktree cleanliness.

## Pitfalls

- A successful push is not enough; `main` may advance mid-sweep, so final merge-base verification against the current `origin/main` is required.
- A missing remote ref for a branch may mean the PR was merged or closed, not that the rebase failed. Confirm with `gh pr view <number> --json state,headRefName,baseRefName,url`.
- Do not leave a PR branch in an in-progress rebase. Either complete the rebase and push, or abort and report the blocked PR clearly.
- Do not run local build/test by default when the user's repo preference is commit/push first and monitor CI, unless the user explicitly requested local verification.