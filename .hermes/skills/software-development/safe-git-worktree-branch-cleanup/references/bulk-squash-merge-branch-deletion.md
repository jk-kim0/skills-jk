# Bulk squash-merge branch deletion in PR-heavy repos

## Context
Repos with heavy squash-merge workflows accumulate 50-100+ stale local branches. `git branch -d` fails silently on squash-merged branches because the branch tip is not an ancestor of `origin/main`.

## Reliable classification script

```bash
# For each candidate branch:
git merge-base --is-ancestor <branch> origin/main
git diff --stat origin/main..<branch>
```

| merge-base | diff --stat | Action |
|------------|-------------|--------|
| success    | empty       | `git branch -d` |
| fail       | empty       | `git branch -D` (squash-merge residue) |
| any        | non-empty   | Preserve for review |

## Practical notes from cleanup runs
- Removing 40+ worktrees in one loop takes 2-3 minutes; do not abort midway.
- `git fetch --prune` removes `[gone]` markers from `git branch -vv`; open PR list is the definitive stale signal.
- For 100+ branches, script the merge-base + diff check instead of running `git branch -d` on a list.
- After removing worktrees, always run `git worktree prune` before verifying remaining state.
