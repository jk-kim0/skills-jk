# Merged PR during follow-up recovery

Use when an agent starts by updating an existing open PR branch, but the PR is merged while the session is still working.

## Symptoms

- `gh pr view <number>` changes from `OPEN` to `MERGED` during the session.
- A push to the old head branch still succeeds, or recreates a deleted remote branch, but the PR remains merged and no longer represents the new commit.
- `gh pr view <branch>` may still show stale data for a short time, or the branch may exist without an open PR.

## Safe recovery

1. Stop treating the merged PR as the target.
2. Fetch and update `origin/main`.
3. Verify the merged PR's final file list and merge commit:
   ```bash
   git fetch origin --prune
   gh pr view <number> --json state,mergedAt,mergeCommit,headRefName,headRefOid,files,url
   ```
4. Create a fresh branch/worktree from current `origin/main` for any remaining changes not included in the merged PR.
5. Apply only the remaining scoped patch, not the old PR commit stack.
6. Push and create a new PR.
7. Clean the obsolete old PR worktree/local branch, and delete the old remote head branch only if no open PR uses it:
   ```bash
   gh pr list --state open --json number,headRefName,url
   git push origin --delete <old-head-branch>
   ```

## Verification

- New PR `files` contains only the remaining intended files.
- New PR base is `main` and head is based on current `origin/main`.
- Root `main` is fast-forwarded to current `origin/main` after the merged PR is absorbed.
- `gh pr checks` and `gh run list --branch <new-branch>` are checked once; if there are no automatic PR triggers, report that explicitly instead of waiting.
