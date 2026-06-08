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
   - If the local worktree branch is both ahead of and behind `origin/<headRefName>`, do not rebase or force-push immediately. First inspect `git log --left-right --cherry-pick HEAD...origin/<headRefName>` and the diff/stat between local and remote. If local-only commits are stale copies of commits now in `origin/main` or rewritten equivalents of the remote PR head, align the worktree to `origin/<headRefName>` with `git reset --hard origin/<headRefName>` before rebasing so another agent's remote work is not overwritten.
4. Run `git fetch origin main --prune` immediately before each branch rebase.
   - `origin/main` can advance while earlier PR branches are being rebased.
5. Rebase and resolve conflicts.
   - Run `git rebase origin/main`.
   - If conflicts occur, preserve both latest-main behavior and the PR's intended final state.
   - If an intermediate historical commit conflicts but a later PR commit already contains the intended final fix, inspect the remote PR head and carry forward the PR's final intent rather than blindly taking either side.
   - After staging conflict resolutions, use `GIT_EDITOR=true git rebase --continue` in non-interactive CLI sessions.
6. Push with lease.
   - Use `git push --force-with-lease origin <headRefName>` because rebase rewrites commit SHAs.
7. Final verification is mandatory, and may require another rebase loop.
   - Fetch `origin/main` again.
   - Re-list open PRs.
   - If another PR merged during the sweep, its remote branch may be deleted and `origin/main` may have advanced; treat that as normal live churn, not as a failed rebase.
   - For every still-open PR branch, verify `git merge-base origin/main origin/<headRefName>` equals `origin/main`.
   - Do this even when GitHub reports `mergeStateStatus: CLEAN` or the PR `baseRefOid` matches the current `origin/main`; GitHub's mergeability state can be CLEAN while the branch tip still does not contain the latest base commit.
   - If any still-open branch is behind current `origin/main` or has become conflicting again after another PR merged, rebase/push it again before reporting completion.
   - Repeat fetch → re-list → merge-base verification until every still-open PR branch is based on the same latest `origin/main` SHA.
8. Final report should explicitly state:
   - Which PRs were rebased and pushed.
   - Which PRs disappeared because they were merged/closed during the sweep.
   - Any skipped cross-repo PRs.
   - Root `main` status.
   - Retained worktree cleanliness.

## Pitfalls

- A successful push is not enough; `main` may advance mid-sweep, so final merge-base verification against the current `origin/main` is required.
- If one open PR merges while you are rebasing another, immediately re-list open PRs after `git fetch --prune`; the merged PR branch may disappear, and the remaining PR may need a second rebase onto the new `origin/main` even if it was just rebased successfully.
- A missing remote ref for a branch may mean the PR was merged or closed, not that the rebase failed. Confirm with `gh pr view <number> --json state,headRefName,baseRefName,url`.
- Do not leave a PR branch in an in-progress rebase. Either complete the rebase and push, or abort and report the blocked PR clearly.
- Do not run local build/test by default when the user's repo preference is commit/push first and monitor CI, unless the user explicitly requested local verification.