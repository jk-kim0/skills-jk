# PR-number-named duplicate and obsolete dirty worktrees

Use this during repo-local workspace cleanup when local worktrees are named like `pr824-*` or `work/pr824-*`, but targeted `gh pr list --head <local-branch>` returns `NO_PR`, or when a dirty worktree conflicts during rebase because latest `main` deleted the changed files.

## PR-number-named local duplicates

A local branch name can encode a PR number while not being the actual GitHub PR head branch. In that case a head-name lookup reports `NO_PR`, even though the PR is open under a different head branch.

Before preserving or deleting these branches:

1. Extract the PR number from the path/branch name when present, for example `pr824-fde-services` -> `824`.
2. Query the PR directly:
   ```bash
   gh pr view 824 --json number,state,title,headRefName,headRefOid,mergedAt,closedAt,url
   ```
3. If the PR is open, fetch and compare the real PR head:
   ```bash
   git fetch origin <headRefName>:refs/remotes/origin/<headRefName>
   git rev-parse --short=12 <local-branch> origin/<headRefName>
   git diff --name-status origin/main...<local-branch>
   git diff --name-status origin/main...origin/<headRefName>
   git diff --stat origin/main...<local-branch>
   git diff --stat origin/main...origin/<headRefName>
   ```
4. If the real PR head has the same or newer payload, remove the clean local `work/pr*` duplicate and keep the actual PR head branch/worktree.
5. If the local duplicate contains extra useful files, copy or commit only that payload into the real open PR branch, verify equality, then delete the duplicate.

## Dirty worktree whose payload is obsolete after latest-main rebase

A dirty PR-less worktree is not automatically worth preserving. If committing it and rebasing onto `origin/main` conflicts because latest `main` deleted the modified files, inspect whether the payload targets stale files that were replaced by a newer structure.

Safe obsolete-pattern indicators:

- Conflict is `modify/delete` on files latest `main` intentionally removed.
- The remaining test changes assert paths that latest `main` now asserts should not exist.
- Current source contains a replacement structure that already covers the same responsibility.

Resolution:

1. Inspect the deleted-file patch and the replacement structure.
2. If the payload only revives obsolete files or stale tests, run `git rebase --skip` for that preservation commit.
3. Verify the worktree is clean and points at `origin/main` or an intended retained head.
4. Remove the obsolete worktree/branch.

Do not resurrect deleted files during cleanup just to preserve a dirty residue commit; cleanup should preserve meaningful current work, not stale implementation from an old structure.
