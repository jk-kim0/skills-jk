# Closed unmerged PR branch preservation during cleanup

Use this during repo-local workspace cleanup when a local branch has meaningful diff, its matching GitHub PR is `CLOSED` but not merged, and the user asked to preserve meaningful local changes as PRs.

## Pattern

A closed PR can still have meaningful branch payload that is not on `origin/main`. Do not delete it just because the PR is closed.

1. Inspect the closed PR directly.
   ```bash
   gh pr view <number> --json number,state,mergedAt,closedAt,title,headRefName,headRefOid,baseRefName,url
   git -C <worktree> diff --stat origin/main...HEAD
   git -C <worktree> diff --name-status origin/main...HEAD
   git -C <worktree> status --short --branch
   ```
2. If the diff is meaningful and unmerged, rebase the branch onto latest `origin/main` and push with `--force-with-lease`.
3. Try to reopen the original PR once.
   ```bash
   gh pr reopen <number>
   ```
4. If GitHub refuses to reopen the PR, do not keep retrying and do not discard the payload. Create a fresh replacement branch from the rebased local HEAD, push it, and open a new PR with a Korean title/body explaining that the old PR could not be reopened.
   ```bash
   git switch -c <old-branch>-<date>
   git push -u origin <old-branch>-<date>
   gh pr create --base main --head <old-branch>-<date> --title '<title>' --body-file <body-file>
   ```
5. Verify the new PR head SHA matches the remote branch.
6. After the replacement PR is verified, delete the obsolete local old branch if it is no longer checked out. Do not delete remote branches or close PRs unless the user explicitly asks.

## Pitfalls

- `gh pr view` may briefly show stale `headRefOid` after a force-push to a closed PR branch. Prefer `git ls-remote origin refs/heads/<branch>` to verify the remote head before deciding whether the payload was pushed.
- A closed PR with `mergedAt: null` is not equivalent to stale/no-value residue. Classify its net diff against latest `origin/main` before deletion.
- If reopening fails with a GraphQL/API error, capture the successful preservation path as “replacement PR created”; avoid recording the transient API error as a permanent tool limitation.
