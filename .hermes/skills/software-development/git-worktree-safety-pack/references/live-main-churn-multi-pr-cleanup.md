# Live main churn during multi-PR workspace cleanup

Use this reference when a repo-local `workspace 정리` sweep overlaps with active merges, branch deletion, or other agents creating/updating worktrees.

## Durable lessons

1. Treat every classification as short-lived.
   - A worktree that was clean and PR-less earlier in the sweep can become dirty before deletion.
   - Re-run `git status --short --branch` inside the exact worktree immediately before `git worktree remove`.
   - If deletion refuses because files are modified/untracked, stop and inspect the payload; do not retry with `--force` by default.

2. If a PR merges while you are rebasing or preparing to push its branch, do not recreate the deleted remote branch.
   - Re-check `gh pr view <n> --json state,mergedAt,headRefName,headRefOid` and `git ls-remote origin refs/heads/<branch>` immediately before pushing.
   - If the PR is `MERGED` and the remote branch is gone, fetch/fast-forward root `main`, then compare the local branch tree to `origin/main`.
   - If `git diff --quiet origin/main..HEAD` succeeds, remove the local worktree/branch as merged residue.
   - If there is still a meaningful tree diff, preserve only the still-valid payload in a fresh latest-main branch/PR; do not resurrect the merged PR branch.

3. Dependent PRs can be retargeted by GitHub after their base PR merges.
   - A child PR that originally targeted another feature/docs branch may become base=`main` after the base branch merges/deletes.
   - Re-query `baseRefName`, `baseRefOid`, and `mergeStateStatus`; if it is `DIRTY`, rebase the child branch onto latest `origin/main` and push with `--force-with-lease` only while the PR is still open.

4. Avoid monolithic final verification scripts during active churn.
   - If a script loops over multiple `gh pr view`, `gh pr checks`, `git fetch`, and worktree status probes, a single slow GitHub/API call can make the whole script exceed tool timeout and hide partial progress.
   - Prefer short, independent terminal calls or small parallel batches for the final stability loop: root status, open PR views, dirty sweep, branch list, and unregistered directory check.

5. Preserve newly discovered dirty PR-less work instead of deleting it as stale.
   - If targeted lookup says `NO_PR` but the worktree has meaningful dirty files or untracked docs, commit them, rebase onto latest `origin/main`, push, and create a narrow Korean PR.
   - If conflicts arise while rebasing documentation preservation work, keep latest main structure and avoid resurrecting stale decisions; preserve only the still-current wording/docs payload.

## Quick command pattern

```bash
# Before deleting a candidate worktree:
git -C <worktree> status --short --branch
git -C <worktree> rev-list --left-right --count origin/main...HEAD
gh pr list --state all --head <branch> --json number,state,title,url,mergedAt,closedAt,baseRefName --limit 20

# If its PR merged mid-sweep and the remote branch is gone:
git fetch --prune origin
git merge --ff-only origin/main
git -C <worktree> diff --quiet origin/main..HEAD && echo "tree-equivalent"

# If still open and you need to update it:
gh pr view <n> --json state,mergedAt,headRefName,headRefOid,baseRefOid,mergeStateStatus
git ls-remote origin refs/heads/<branch>
git -C <worktree> rebase origin/main
git -C <worktree> diff --check
git -C <worktree> push --force-with-lease=refs/heads/<branch>:<expected-remote-oid> origin <branch>:refs/heads/<branch>
```

## Reporting note

The final report should distinguish:

- merged/stale local worktrees actually removed;
- open PR worktrees intentionally retained;
- PR-less dirty work preserved into new PRs;
- PR branches that merged mid-cleanup and were removed only after tree-equivalence verification;
- any checks still pending versus checks confirmed green.
