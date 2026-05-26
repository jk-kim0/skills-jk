# PR merges during scoped-memory update

Use when updating a `skills-jk` scoped memory/config PR and the target PR merges before the follow-up push/metadata edit completes.

## Why it matters

`skills-jk` PRs can be merged quickly during a cleanup session. If the agent continues pushing to the old head branch after merge, the push can recreate a branch that no longer has an open PR. The agent may then accidentally edit the already-merged PR body and believe the new commit is represented there.

## Recovery pattern

1. Re-check the target PR state immediately before pushing follow-up commits or editing the body:
   ```bash
   env -u GITHUB_TOKEN gh pr view <pr> --json state,mergedAt,headRefName,headRefOid,files,url
   ```
2. If the PR is `MERGED`, do not update it further.
3. Fetch and fast-forward local main to the new `origin/main`:
   ```bash
   git fetch origin --prune
   git reset --hard origin/main   # only from clean/protected root after preserving intended local diff
   ```
4. Create a fresh latest-main worktree/branch for the remaining scoped diff.
5. Apply only the remaining file patch, commit, push, and dispatch `create-pr.yml`.
6. Remove the stale old worktree/local branch. Delete the stale old remote head branch only after verifying no open PR uses it:
   ```bash
   env -u GITHUB_TOKEN gh pr list --state open --json number,headRefName,url
   git push origin --delete <old-branch>
   ```

## Reporting rule

Report the merged PR, the new PR, and the final root state as separate facts:
- prior PR merged and absorbed part of the scoped payload
- new PR contains only the remaining diff
- root `main` is aligned with `origin/main` and clean
