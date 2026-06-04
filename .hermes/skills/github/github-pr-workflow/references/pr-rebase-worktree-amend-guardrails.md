# PR rebase worktree and amend guardrails

Use when a PR branch must be rebased, amended, and force-pushed.

## Guardrails

- Before creating a new worktree, inspect whether the PR branch is already checked out with `git worktree list --porcelain` or `git branch -vv`.
- If the branch is already used by a worktree, operate in that existing worktree instead of forcing a duplicate checkout.
- After `git rebase`, `git commit --amend`, or any conflict-resolution step, run `git status --short --branch` before push.
- If an intended edit remains unstaged after amend, stage it and amend again before pushing.
- After force-push, verify with:
  - `git rev-parse HEAD origin/<branch>`
  - `gh pr view <pr> --json headRefOid,statusCheckRollup,mergeStateStatus`

## Why this matters

A rebase can succeed while a subsequent local edit remains unstaged. If the branch is force-pushed at that point, the PR head is updated but the requested follow-up edit is omitted. The status check before push catches this cheaply.