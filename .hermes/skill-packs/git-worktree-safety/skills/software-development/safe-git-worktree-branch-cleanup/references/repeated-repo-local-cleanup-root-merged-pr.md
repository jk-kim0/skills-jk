# Repeated repo-local cleanup when the root checkout is a newly merged PR branch

Context: during repeated `workspace 정리` passes in a PR-heavy repo, the root checkout can change between requests because another session or the user checked out a PR branch after the previous cleanup. The next cleanup may start on a clean non-main branch whose remote head has just been pruned.

Safe handling pattern:

1. Always re-run `git fetch --prune origin` even if the previous cleanup just finished.
2. Inspect the current root branch with `git status --short --branch`, `git branch -vv`, and `git worktree list --porcelain`.
3. For the root branch, query GitHub PR state by exact head branch:
   - `gh pr list --head <branch> --state open`
   - `gh pr list --head <branch> --state closed`
4. If the root branch is clean, has no open PR, has a merged closed PR, and the remote branch is gone, treat it as stale even though it is currently checked out.
5. Switch the root checkout to `main`, fast-forward `main` to `origin/main`, then delete the stale branch with `git branch -D <branch>`.
6. Preserve any other branch-backed worktree whose PR is still open.
7. Verify final state with:
   - `git status --short --branch`
   - `git rev-parse main origin/main`
   - `git worktree list --porcelain`
   - `git worktree prune --dry-run --verbose`

Pitfall: do not over-interpret a huge `git diff --stat origin/main..<merged-root-branch>` after main has advanced. When a merged PR branch is behind the new main, the diff can look like massive deletions or reversions because latest main contains unrelated newly merged work. The authoritative stale signal is the combination of clean root checkout + no open PR + merged closed PR + pruned remote branch.