# Merged PR branch recreation recovery

Use this note when a follow-up change is accidentally pushed to a branch whose PR was already merged or closed.

## Symptom

- `git push` succeeds and GitHub says `Create a pull request for '<old-branch>'`.
- `gh pr view <old-branch>` shows the previous PR as `MERGED` or `CLOSED`.
- `git ls-remote origin refs/heads/<old-branch>` now shows a branch ref that did not need to exist anymore.
- The intended change is not attached to the merged PR; it has merely recreated the old remote branch.

## Recovery

1. Preserve the intended delta from the mistaken worktree/branch:

```bash
git -C <old-worktree> show --binary --format= HEAD > /tmp/intended-followup.patch
```

2. Create a fresh branch from latest main:

```bash
git -C <repo-root> fetch origin --prune
git -C <repo-root> worktree add .worktrees/<new-topic> -b <new-branch> origin/main
```

3. Apply only the intended delta:

```bash
git -C <new-worktree> apply --index /tmp/intended-followup.patch
```

4. Verify, commit, push, and open a new PR.

5. Delete the accidentally recreated old remote branch:

```bash
git push origin --delete <old-branch>
```

6. Verify:

```bash
git ls-remote origin refs/heads/<old-branch> || true
git ls-remote origin refs/heads/<new-branch>
gh pr view <new-branch> --json state,headRefOid,url
```

## Prevention

Before every existing-PR follow-up push, run:

```bash
gh pr view <branch-or-pr> --json state,headRefName,headRefOid,url
git ls-remote origin refs/heads/<head-branch>
```

If `state` is not `OPEN`, do not push to that branch.
