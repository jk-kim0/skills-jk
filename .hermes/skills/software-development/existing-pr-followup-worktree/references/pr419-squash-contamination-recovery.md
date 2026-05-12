# PR 419 squash contamination recovery

Use this when an open-PR squash attempt unexpectedly stages files outside the intended PR scope.

## Danger signal
After `git reset --soft origin/main`, `git status --short` shows unrelated files such as:
- renamed tests not part of the PR
- skill/docs files unrelated to the PR
- helper files from another stale local branch state

## Fast decision rule
If the staged file set is larger than the GitHub PR file list, do not continue the squash commit.

## Safer recovery pattern
1. Identify a known-good source for the intended PR scope:
   - current `origin/<pr-branch>` if still clean, or
   - an earlier known-good pre-squash commit SHA
2. Create a brand-new worktree from latest `origin/main`.
3. Copy only the intended PR file set into that clean worktree:
   - `git checkout <good-ref> -- <paths...>`
4. Verify the rebuilt diff:
   - `git diff --name-only origin/main`
   - confirm it matches only the intended PR files
5. Commit once and force-push back to the same PR branch.

## Heuristic
When the real goal is 'same final diff, but one clean commit', prefer clean-scope reconstruction over trying to salvage a suspicious soft-reset squash.
