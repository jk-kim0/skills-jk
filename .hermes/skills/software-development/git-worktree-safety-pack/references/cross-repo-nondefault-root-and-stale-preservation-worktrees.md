# Cross-repo cleanup: non-default roots and stale preservation worktrees

Use this during cross-repo workspace cleanup when an owner repo root checkout is not on the remote default branch, or when old preservation worktrees remain after newer main/PR work has landed.

## Clean non-default root with meaningful PR-less work

A root checkout can be clean but parked on a non-default local branch with no open or closed PR metadata. Do not delete it or silently switch it back to `main` just because it is not tied to a PR.

Handling pattern:

1. Fetch/prune and compare the branch against the remote default branch.
2. If the net diff is meaningful and the branch is clean, push the branch and open a review PR instead of discarding it.
3. After the PR is created and the remote head is verified, switch the root checkout back to the remote default branch and fast-forward it.
4. Re-add the PR branch as a repo-root `.worktrees/<topic>` worktree so the root stays clean while the active PR remains inspectable.
5. Re-run the workspace cleanup sweep so the newly restored root can participate in final verification.

Useful summary label:
- `meaningful PR-less root branch promoted to PR worktree`

## Old clean preservation worktrees with broad stale deletion diffs

Repeated cleanup cycles can leave old `backup/*`, `preserve/*`, or closed-PR worktrees whose direct diff against current `origin/main` is huge because the branch predates later migrations or preservation PRs. These branches may show many deletions of files that are now canonical on main.

Treat them as stale local residue when all are true:

- the worktree is clean;
- there is no open PR for the branch;
- targeted all-state PR lookup is empty or only closed/non-merged history;
- the direct diff is dominated by broad stale deletions or old baseline churn;
- any small useful payload has already been preserved in a newer open PR or current main.

Safe cleanup sequence:

```bash
git worktree remove .worktrees/<name>
git worktree prune
git branch -D <branch>
```

Do not delete remote branches or close PRs as part of this local cleanup unless the user explicitly asks.

Useful summary label:
- `stale preservation worktree removed; remote/PR lifecycle untouched`
