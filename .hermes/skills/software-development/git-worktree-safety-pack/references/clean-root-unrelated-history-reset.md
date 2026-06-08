# Clean root `main` with unrelated/diverged history

Use this during repo-local workspace cleanup when the root checkout is clean but local `main` is not the same history as `origin/main` (for example `git pull --ff-only` fails with unrelated histories or the local root is an old bootstrap history).

## Pattern

1. Confirm the root checkout is clean before destructive movement:
   - `git status --short --branch`
   - Do not reset if there are authored files, untracked docs/skills/config, or runtime files that need classification.
2. Fetch/prune first:
   - `git fetch --prune origin`
3. Verify the intended source of truth:
   - `git rev-parse origin/main`
   - Optionally compare `git log --oneline --left-right --cherry-pick main...origin/main` to confirm local-only commits are stale or non-authoritative.
4. If root is clean and `origin/main` is authoritative, align root directly:
   - `git reset --hard origin/main`
5. Do not try to merge unrelated histories during cleanup just to make `main` fast-forwardable.
   - Cleanup's goal is to restore root to the latest remote default branch, not preserve stale root history.
6. Immediately re-run final verification:
   - root `git status --short --branch`
   - root HEAD equals `origin/main`
   - `git worktree list --porcelain`
   - dirty sweep for all retained worktrees
   - unregistered `.worktrees/` directory scan

## Pitfall

A clean root can still be on an obsolete unrelated local `main` history. If the cleanup report says root is current without comparing root HEAD to `origin/main`, stale root history can survive even after branch/worktree cleanup. Always print both OIDs in the final report when a reset or fast-forward was needed.
