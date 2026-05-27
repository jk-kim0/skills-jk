# Local sweep: promote a meaningful no-open-PR dirty worktree

Use this during `skills-jk` repo-local cleanup when the requested scoped config/memory payload is already handled or empty, but another local worktree still contains focused dirty changes with no open PR.

## Signal pattern

- Root `main` is dirty with broad generated `.hermes/skills/**` residue or stale copied files.
- A sibling repo-root worktree under `.worktrees/` is on a non-main branch.
- `gh pr list --head <branch> --state all` returns no open/merged PR for that branch.
- The worktree has a focused dirty patch in source/test files, not just generated skill bundle churn.
- Representative `git diff` shows a coherent implementation/test change.

## Safe workflow

1. Inspect the dirty worktree directly.
   - `git -C <worktree> status --short --branch`
   - `git -C <worktree> diff --stat`
   - `git -C <worktree> diff --name-status`
   - `gh pr list --head <branch> --state all --json number,state,title,url,headRefName,headRefOid`
2. If the patch is coherent and no PR exists, commit it in that worktree.
   - Run at least `git diff --check` first.
   - Stage only the focused source/test files, not root generated residue.
3. Fetch and rebase the worktree branch onto latest `origin/main`.
   - This also absorbs any freshly merged scoped memory/config PRs so they do not appear in the new PR diff.
4. Push the branch and verify the remote ref.
   - `git ls-remote origin refs/heads/<branch>` must match local `HEAD`.
5. Create the PR via `.github/workflows/create-pr.yml`, not direct `gh pr create`.
6. Verify the PR file list from GitHub and the branch diff from the worktree.
7. Only after meaningful branches are safely pushed, reset/clean root `main` generated residue and delete stale merged worktrees/branches.

## Reporting distinction

Report these as separate facts:

- the requested scoped config/memory PR status (possibly already merged or no-op)
- the separately promoted no-open-PR worktree PR
- root `main` reset/fast-forward cleanup
- remaining worktrees are active open-PR worktrees only

## Pitfall

Do not treat a no-open-PR dirty worktree as stale just because it was discovered during workspace cleanup. If its current diff is focused and latest-main-portable, promote it to a reviewable PR before deleting or resetting anything.
