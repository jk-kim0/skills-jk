# Existing PR branch already checked out in another worktree

When updating an open PR, the preferred behavior remains: use a fresh worktree and update the existing PR branch, not a new PR.

Git constraint:
- A local branch can be checked out in only one worktree at a time.
- If the PR head branch is already checked out elsewhere, commands such as `git switch -C <pr-head> origin/<pr-head>` fail with `fatal: '<branch>' is already used by worktree at '<path>'`.

Safe follow-up pattern:

1. Fetch and inspect the PR head.

```bash
git fetch origin --prune
gh pr view <number> --json state,headRefName,baseRefName,headRefOid,mergeStateStatus,url
```

2. Create a fresh disposable worktree/branch from the remote PR head, using a distinct local branch name.

```bash
git worktree add .worktrees/<pr-topic-followup> origin/<pr-head>
git -C .worktrees/<pr-topic-followup> switch -c <pr-head>-followup --track origin/<pr-head>
```

3. Make the narrow follow-up change in that worktree. Verify targeted tests/checks.

4. Rebase onto latest base if needed.

```bash
git -C .worktrees/<pr-topic-followup> fetch origin --prune
git -C .worktrees/<pr-topic-followup> rebase origin/main
```

5. Push this worktree's `HEAD` explicitly back to the original PR branch, not to the temporary branch.

```bash
OLD_REMOTE_SHA=$(git ls-remote origin refs/heads/<pr-head> | awk '{print $1}')
git -C .worktrees/<pr-topic-followup> push \
  --force-with-lease=refs/heads/<pr-head>:$OLD_REMOTE_SHA \
  origin HEAD:refs/heads/<pr-head>
```

6. Verify the actual remote ref and PR metadata.

```bash
git ls-remote origin refs/heads/<pr-head>
gh pr view <number> --json headRefName,headRefOid,mergeStateStatus,statusCheckRollup,url
```

Pitfalls:
- Do not open a second PR just because the exact PR branch is already checked out somewhere else.
- Do not push the temporary `*-followup` branch as the review branch.
- If `--force-with-lease` rejects, refetch/reinspect; another actor may have updated the PR branch.
- `gh pr view` can lag after push, so verify `git ls-remote origin refs/heads/<pr-head>` first.
