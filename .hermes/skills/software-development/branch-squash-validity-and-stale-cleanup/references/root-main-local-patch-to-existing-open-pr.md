# Root `main` local patch belongs on an existing open PR

Use this pattern when the user asks to update `main` and make/write the PR, but the live repo state shows the local root patch actually belongs to an already-open review line.

## Signal pattern

- root checkout is on `main`
- `git status --short` shows tracked local edits
- those edits are not random residue; they align with exactly one currently open PR topic/path set
- creating a new PR would duplicate an existing review line

## Handling rule

1. Refresh live state first.
   - `git fetch origin --prune`
   - inspect `gh pr list --state open ...`
   - inspect root `git status --short --branch`
2. Decide whether the root-local patch maps to an existing open PR branch.
   - compare changed paths/topic against open PR payloads
   - if there is a single clear match, reuse that PR instead of creating a new one
3. Move the patch onto a fresh worktree of the open PR branch.
   - copy only the intended tracked files
   - avoid leaving root `main` as the long-lived home of the patch
4. Rebase the PR branch onto latest `origin/main`.
5. If rebase conflicts occur, prefer a merged resolution that keeps both:
   - upstream main-side updates
   - the intended local follow-up patch
6. Commit/push the PR branch update.
7. Restore root `main`, then fast-forward it to latest `origin/main`.
8. Re-scan local branches/worktrees and remove stale merged siblings from the same line if they are now redundant.

## Why this matters

The user may say `PR 작성` in a generic way, but the correct action is not always `open a brand-new PR`.
When the local patch clearly extends an already-open PR, splitting it into another PR creates duplicate review state and dirties root `main` unnecessarily.

## Suggested summary labels

- `root-local follow-up transplanted onto existing open PR branch`
- `existing open PR updated instead of creating duplicate PR`
- `root main restored and fast-forwarded after PR update`
