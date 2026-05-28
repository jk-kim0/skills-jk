# Clean merged PR worktrees after upstream branch pruning

Use this reference when a repo-local `workspace 정리` request finds worktrees whose local branches track remote refs that were pruned after PR merge.

## Signal pattern

- Root checkout is on `main`, clean, and behind `origin/main`.
- `git fetch --all --prune` reports deleted remote branches.
- `git branch -vv` shows feature/doc branches with `[gone]` upstreams and attached `.worktrees/<name>` paths.
- The user asked for repo-local workspace cleanup, not a new preservation/audit PR.

## Safety checks before deleting

For each gone-upstream branch/worktree:

```bash
git -C <worktree> status --short --branch
git -C <worktree> rev-list --left-right --count origin/main...HEAD
gh pr list --head <branch> --state open --json number,title,url
gh pr list --head <branch> --state merged --json number,title,url,mergedAt
```

Delete only when:

- the worktree has no uncommitted local changes;
- there is no open PR for the branch;
- there is a merged PR for the same head branch, or the branch is otherwise proven already preserved;
- no meaningful unmerged local patch needs promotion.

If the branch is far behind or has multiple unique commits and there is no merged PR proof, switch to the synthetic-squash workflow in `references/promote-portable-backup-patch.md` instead of deleting.

## Cleanup sequence

```bash
git worktree remove <worktree>
git branch -D <branch>
git checkout main
git pull --ff-only origin main
git worktree prune
```

If there are several merged stale worktrees, remove all clean/stale worktrees first, then delete their local branches, then fast-forward `main` once.

## Final verification

```bash
git status --short --branch
git worktree list --porcelain
git branch -vv
find .worktrees -mindepth 1 -maxdepth 2 -print 2>/dev/null || true
```

Report:

- root repo path;
- current `main` HEAD and clean alignment with `origin/main`;
- removed worktree paths and local branch names;
- PR evidence used for deletion, if any;
- whether `.worktrees/` contains only expected residue such as `.gitkeep`.
