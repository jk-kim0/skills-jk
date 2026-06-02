# Profile config preservation during workspace cleanup

Use this reference when a repo-local cleanup starts with root `main` dirty, an existing PR-less preservation worktree already contains meaningful local guidance, and the current dirty root includes repo-tracked Hermes profile/config changes.

## Pattern

1. Do not create a duplicate preservation branch if a clean PR-less worktree already represents the same local-guidance bucket. First compare root dirty files with that worktree and its branch diff against `origin/main`.
2. If the existing worktree is the right bucket, update that worktree and open one PR from it rather than splitting overlapping local guidance into another PR.
3. For simple profile/config scalar changes such as `display.compact: true`, avoid carrying the full output of `hermes config set` into the PR when it rewrote YAML formatting, comments, nulls, or list indentation.
4. Restore the affected config file(s) in the preservation worktree from `origin/main`, then patch only the intended scalar value.
5. If the root checkout contains the same setting plus YAML-normalization noise, preserve the setting in the PR branch, then reset/clean root after the PR branch is pushed and verified.
6. Verify with both a diff review and YAML loading, for example checking each target file's `display.compact` resolves to `True`.
7. After PR creation, remove only merged/stale worktrees/branches. Keep the open PR worktree clean and registered.

## Pitfalls

- `git diff origin/main` from a dirty root that is behind latest main can show stale deletion hunks and unrelated upstream differences; do not apply it wholesale.
- `hermes config set` is useful for runtime config updates, but in repo-tracked config it may produce noisy review diffs. Preserve reviewability by reducing the branch diff to the intended key change.
- A PR-less branch pushed to origin is not equivalent to a review PR. If it contains meaningful work and no open PR, update/push it and create the PR through the repo-standard mechanism.
