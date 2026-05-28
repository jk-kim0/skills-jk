# Detached worktree follow-up for an already-checked-out PR branch

Use this when an open PR needs follow-up changes but its branch is already checked out in another local worktree.

## Pattern

1. Confirm the PR is open and get the branch name.

```bash
gh pr view <number> --json state,headRefName,baseRefName,mergeStateStatus,url
```

2. Fetch the base and PR branch.

```bash
git fetch origin main <headRefName> --prune
```

3. Create a fresh detached worktree from the remote PR branch so the existing worktree is not disturbed.

```bash
git worktree add --detach .worktrees/pr-<number>-followup origin/<headRefName>
```

4. Make the follow-up changes, run the narrowest relevant verification, and commit on detached HEAD.

```bash
git add -A
git commit -m "fix: <short follow-up description>"
```

5. Rebase the detached HEAD onto latest `origin/main` when the repo requires PR branches to be current.

```bash
git fetch origin main <headRefName> --prune
git rebase origin/main
```

6. Re-run the narrowest relevant verification after rebase.

7. Push detached HEAD back to the same PR branch using an explicit refspec and force-with-lease against the previously fetched branch tip.

```bash
old=$(git rev-parse origin/<headRefName>)
git push --force-with-lease=refs/heads/<headRefName>:$old origin HEAD:refs/heads/<headRefName>
```

8. Verify the remote branch tip directly before trusting PR UI status, because GitHub can lag after force-push.

```bash
git ls-remote origin refs/heads/<headRefName>
gh pr view <number> --json headRefOid,statusCheckRollup,mergeStateStatus,url
```

## Pitfalls

- Do not create a second branch/PR for open-PR follow-up just because the local branch is already checked out elsewhere.
- Do not reuse or mutate the existing worktree if a fresh worktree was requested or expected.
- After rebasing an old PR branch onto latest `origin/main`, `git diff origin/<headRefName>..HEAD` may show all main changes plus the follow-up because the old remote branch was behind. Use commit range or PR diff after push for review scope.
- Preserve unrelated legacy asset references when doing broad path replacement. Search/inspect diffs for over-broad replacements before commit.
