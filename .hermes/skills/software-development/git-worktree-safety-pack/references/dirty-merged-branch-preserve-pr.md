# Dirty merged-branch worktree preservation pattern

Use during repo-local `workspace 정리` / `main 업데이트` cleanup sweeps.

## Situation

A local worktree branch may appear stale because its branch HEAD is already merged into `origin/main` or tracks `origin/main`, but the worktree can still contain meaningful uncommitted/untracked changes.

Example signal:

```text
branch docs/auth-ui-terminology [origin/main]
merged_to_origin_main: true
git status --short:
 M docs/ui/README.md
 M docs/ui/screen-overview.md
 M docs/user-auth-requirements.md
?? docs/ui/auth-account-terminology.md
```

Deleting this as a merged branch would lose real work.

## Required handling

1. For every non-main worktree, check `git status --short` before any deletion.
2. If dirty, do not delete solely because the branch is merged into `origin/main` or has no open PR.
3. Inspect the diff and untracked files enough to classify the dirty payload:
   - If it is meaningful repo work, commit it on that worktree branch, push it, and create or update a PR.
   - If it is generated/cache/runtime residue, remove it only when it is clearly disposable under repo policy.
4. When committing meaningful dirty work, run a second `git status --short` after the first commit. Untracked or adjacent modified files can be missed if only the initially reviewed diff is staged.
5. Include all related dirty files in the same PR when they belong to the same logical change.
6. After push/PR creation, rerun final cleanup and preserve the worktree as an open-PR worktree.

## Verification

- Root checkout is on clean `main` and up to date with `origin/main`.
- All remaining worktrees are either clean open-PR worktrees or explicitly reported dirty preserved worktrees.
- No meaningful dirty branch was deleted merely because its HEAD was merged or its upstream was `origin/main`.
