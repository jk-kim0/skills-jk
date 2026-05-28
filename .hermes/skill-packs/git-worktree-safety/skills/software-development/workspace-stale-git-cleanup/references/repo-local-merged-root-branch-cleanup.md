# Repo-local cleanup when the root checkout is on a merged/gone PR branch

Use this reference when a repo-local `workspace 정리` starts with the main checkout itself on a feature branch whose upstream was pruned.

Observed pattern:
- root checkout is clean but on a non-main feature branch
- `git fetch --prune origin` marks that branch `[gone]`
- `gh pr list --head <branch> --state closed` confirms the PR was merged
- local `main` is behind `origin/main` and can fast-forward
- other local branches may also be merged/gone, while one or more worktrees may still have open PRs

Safe sequence:
1. `git fetch --prune origin` first, so stale upstream refs disappear.
2. For each local branch/worktree, query GitHub by exact head branch:
   - `gh pr list --repo <owner/repo> --head <branch> --state open --json ...`
   - `gh pr list --repo <owner/repo> --head <branch> --state closed --json ...`
3. If the current root branch is clean and its PR is `MERGED`, switch root back to `main`.
4. Fast-forward main with `git pull --ff-only origin main` only after the switch succeeds and the root is clean.
5. Remove merged/gone worktrees first with `git -C <repo-root> worktree remove --force <path>`.
6. Run `git worktree prune`.
7. Delete merged/gone local branches with `git branch -D <branch>` only after merged PR evidence and after they are no longer checked out.
8. Preserve branches/worktrees with open PRs, even if they are behind latest `origin/main`.
9. Verify:
   - `git status --short --branch` shows clean `main...origin/main`
   - `git rev-parse main origin/main` match
   - `git worktree prune --dry-run --verbose` is empty
   - remaining worktrees correspond to root main or open PRs

Important pitfall:
Do not delete a `[gone]` branch just because the upstream disappeared. Require merged PR evidence or another strong stale signal first. This is especially important after `git fetch --prune`, because branch tracking metadata becomes less informative.