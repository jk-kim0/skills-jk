# Top-level linked review worktree cleanup

Use this reference when a workspace root contains a sibling directory that is a linked worktree rather than a standalone clone, especially names like `<repo>-pr-817-review`.

## Pattern

A top-level sibling can share the canonical repo's git common-dir but have a local helper branch whose name does not match the GitHub PR head branch, e.g.:

- directory: `/Users/jk/workspace/corp-web-app-pr-817-review`
- local branch: `pr-817`
- actual GitHub PR head: `feat/tailwind-route-groups`

In this case, `gh pr list --head pr-817` is insufficient and can falsely report no PR. If the directory name includes a PR number, query by PR number directly.

## Safe sequence

1. Confirm it is a linked worktree:
   - `git -C <dir> rev-parse --git-common-dir`
   - compare common-dir with the canonical sibling repo.
2. Extract the PR number from the directory name when present.
3. Query PR state by number:
   - `gh -R <owner/repo> pr view <number> --json number,state,mergedAt,closedAt,headRefName,title,url`
4. If the PR is `MERGED`, the worktree has no meaningful local dirt, and the canonical repo remains available, remove it from the owning repo context:
   - `git -C <canonical-repo> worktree remove --force <top-level-review-worktree>`
   - `git -C <canonical-repo> worktree prune`
5. Delete the helper local branch only after it is no longer checked out anywhere:
   - `git -C <canonical-repo> branch -D <helper-branch>`

## Pitfall

Do not rely only on the local branch name for review helper worktrees. These helpers often use local names like `pr-817`, while GitHub knows the PR by its true head branch. Querying by PR number avoids preserving stale merged review worktrees unnecessarily.