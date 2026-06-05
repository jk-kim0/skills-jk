# Open PR sweep: rebase, conflict resolution, and blocker classification

Use this reference when the user asks to check/fix all open PRs in a repository.

## Workflow

1. List every open PR with mergeability, review decision, check rollup, branch, and URL:
   `gh pr list --state open --json number,title,headRefName,baseRefName,mergeStateStatus,reviewDecision,statusCheckRollup,updatedAt,url --limit 100`.
2. For each PR, inspect files/commits/body before changing anything:
   `gh pr view <number> --json number,title,headRefName,baseRefName,mergeStateStatus,reviewDecision,statusCheckRollup,commits,files,url,body`.
3. If the root checkout is dirty, do not mix PR remediation into it. Create or reuse repo-local `.worktrees/<safe-branch-name>` worktrees for each PR branch.
4. Fetch latest `origin/main`, then rebase each PR branch onto `origin/main` in its own worktree.
5. Resolve conflicts by preserving both latest-main additions and PR-scoped additions when the files are registries/indexes (for example skill `References` lists). Do not resolve by taking one side blindly.
6. Before pushing, run a pre-push guard:
   - `gh pr view <number> --json state,headRefName,headRefOid,mergeStateStatus,url`
   - confirm the PR is still `OPEN`
   - confirm the PR head branch matches the local branch
   - confirm the remote head SHA matches the branch you intend to replace
7. Push rebased branches with `git push --force-with-lease origin <branch>`.
8. Re-read all open PRs after pushing and classify the remaining blockers.

## Practical details

- If `git rebase --continue` opens Vim or another editor in a non-interactive Hermes terminal, rerun with `GIT_EDITOR=true git rebase --continue` after conflicts are staged.
- `mergeStateStatus: DIRTY` usually means conflicts or not mergeable with base; rebase or merge-test locally.
- `mergeStateStatus: BLOCKED` with an empty `statusCheckRollup` and `reviewDecision: REVIEW_REQUIRED` is not a CI failure. Report it as a review/approval blocker, not a technical failure.
- `statusCheckRollup: []` means no checks are currently reported for that PR; do not wait for CI that is not present.
- After force-push, always re-query the PR head SHA and merge state; stale pre-push `gh pr view` output is not enough.

## Reporting

Report each open PR separately with:

- PR number and title
- action taken: rebased, conflict fixed, pushed, or no technical fix needed
- final `mergeStateStatus`
- final `reviewDecision`
- whether checks are failing, passing, absent, or pending
- remaining blocker, if any
