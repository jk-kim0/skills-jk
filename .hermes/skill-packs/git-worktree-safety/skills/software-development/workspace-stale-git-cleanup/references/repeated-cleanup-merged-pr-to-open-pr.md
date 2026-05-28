# Repeated repo-local cleanup: merged PR residue plus one meaningful branch

Use this reference when repeated `workspace 정리` requests occur in `skills-jk` or another PR-heavy repo after earlier cleanup passes already looked complete.

## Observed pattern

1. A previously open follow-up PR merges between cleanup passes.
2. `git fetch origin --prune` advances `origin/main` and removes the merged PR remote ref.
3. The local root `main` can be reset/fast-forwarded to `origin/main`, making that merged PR worktree/branch stale.
4. Another local branch/worktree may remain with:
   - no currently open PR at first glance, or a PR object that appears shortly after a create workflow
   - a real direct diff versus `origin/main`
   - a remote branch that still exists

## Safe handling

- Remove only the merged PR residue whose GitHub state is confirmed `MERGED`.
- Do not delete a clean branch-backed worktree merely because it has no open PR if its two-dot diff versus `origin/main` is meaningful.
- For `skills-jk`, convert that meaningful branch into a bot-authored PR via the repo `create-pr.yml` workflow (or verify the PR if it already exists) rather than treating it as stale cleanup.
- Preserve the resulting open-PR worktree/branch.
- Final state should be root `main` clean and aligned to `origin/main`, plus only open-PR worktrees.

## Verification checklist

```bash
git fetch origin --prune
git reset --hard origin/main
git worktree list --porcelain
git branch -vv --no-abbrev
env -u GITHUB_TOKEN gh pr list --state open --json number,headRefName,url
git worktree prune --dry-run --verbose
```

For each non-main branch:

```bash
env -u GITHUB_TOKEN gh pr list --head "$branch" --state all --json number,state,url
git diff --name-status origin/main.."$branch"
git ls-remote origin "refs/heads/$branch"
```

## Pitfall

On macOS `/bin/bash` is often Bash 3.x, so `mapfile` is unavailable. Use POSIX-compatible loops or run an explicit newer shell when writing cleanup scripts intended for this environment.
