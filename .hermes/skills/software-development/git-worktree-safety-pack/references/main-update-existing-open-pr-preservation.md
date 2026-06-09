# Main update with dirty root and an existing open preservation PR

Use this during repo-local `main 업데이트` / `workspace 정리` when root `main` is dirty and behind `origin/main`, a previous preservation PR has already merged or its remote branch is gone, and a newer open preservation PR may cover the same class of local skill/docs changes.

## Pattern

1. Fetch/prune first and identify live state.
   - Check whether any old local worktree branch has `origin/<branch>: gone`.
   - Query the old PR directly (`gh pr view <n> --json state,mergedAt,closedAt,headRefName`) before deciding whether to keep or delete that worktree.
   - Re-list current open PRs; do not assume the previously retained preservation PR is still the right target.
2. Compare the dirty root payload against the latest `origin/main` and the current open preservation PR branch.
   - If the old preservation PR is merged and root is behind, expect stale root file shapes.
   - Do not copy whole root files over the open PR worktree; this can revert newer PR-only guidance or resurrect duplicate/deleted entries.
   - Prefer a 3-way patch for the tracked root diff, then resolve conflicts by keeping the open PR's richer/latest structure and adding only still-missing incremental guidance.
3. Treat untracked runtime state separately.
   - Runtime residue such as `.hermes/pairing/` and `.hermes/lsp/` should not be preserved in docs/skill PRs.
   - If an untracked authored reference exists, first check whether latest `origin/main` or the current open PR already contains it before copying it.
4. Resolve conflicts narrowly.
   - Inspect only the unmerged files for conflict markers. A broad repository grep can find literal conflict-marker examples in templates, tests, or documentation and produce false positives.
   - Stage only the intended resolved files and run `git diff --cached --check`.
5. Amend the existing open preservation PR instead of creating a duplicate PR when scope overlaps.
   - Confirm the PR is still open immediately before force-pushing.
   - Rebase onto `origin/main`, push with `--force-with-lease`, verify `git merge-base origin/main origin/<headRefName>` equals `origin/main`, and update the PR body if the scope changed.
6. Clean after preservation is verified.
   - Reset root to `origin/main` and remove runtime residue.
   - Remove stale merged/gone local worktrees and branches only after their PR is verified merged/closed and the worktree is clean.

## Pitfalls

- A branch with `origin/<branch>: gone` may be a merged PR branch, not failed fetch state. Query the PR and remove the clean worktree/branch after preservation has moved to the current open PR.
- Applying a stale root diff directly into a newer open PR can accidentally delete newer guidance. If a diff shows broad deletions, stop and manually preserve only additive/current lessons.
- Conflict marker scans should be targeted to the files touched by the patch; this repository intentionally contains example marker strings in some skill docs/templates.
