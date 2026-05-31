# Empty repository / no-origin-main worktree pattern

Use this when a repository has no commits yet, `main` is an unborn branch, or `origin/main` is missing/gone, but the user still wants repository work to happen outside the protected root `main` checkout.

## Trigger signals

- `git status --short --branch` shows `## No commits yet on main...origin/main [gone]` or similar.
- `git log --all` has no commits.
- `git worktree add .worktrees/<name> -b <branch> origin/main` cannot be used because there is no `origin/main` commit to base from.

## Safe pattern

1. Verify root state first:

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
git remote -v
git worktree list --porcelain
```

2. Create an orphan worktree under repo-root `.worktrees/`:

```bash
mkdir -p .worktrees
git worktree add --orphan -b docs/<topic> .worktrees/<flat-name>
```

3. Verify the worktree before editing:

```bash
git worktree list --porcelain
git -C .worktrees/<flat-name> branch --show-current
git -C .worktrees/<flat-name> rev-parse --show-toplevel
git -C .worktrees/<flat-name> status --short --branch
```

4. Use absolute paths under the worktree for file tools.

5. If the root checkout shows `.worktrees/` as untracked, keep the repository clean without creating a tracked ignore file unless the user asked for one:

```bash
printf '\n.worktrees/\n' >> .git/info/exclude
```

6. Commit from the orphan worktree branch, not from root `main`.

## Notes

- This is appropriate for first-documentation or bootstrap work in a brand-new repository.
- Do not pretend the branch is based on latest `origin/main` when no such commit exists. Report that an orphan worktree was used because the repository has no base commit yet.
- Do not create a PR or merge into `main` unless the user explicitly requested that step.
