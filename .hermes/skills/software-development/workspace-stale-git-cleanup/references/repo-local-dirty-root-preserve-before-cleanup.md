# Repo-local cleanup with meaningful dirty root changes

Use this reference when a repo-local `workspace 정리` / stale worktree cleanup request starts from a root checkout on `main` that is dirty.

## Pattern

Treat root cleanup and meaningful local preservation as separate deliverables:

1. Fetch/prune and inspect root status before deleting stale worktrees.
2. Classify root dirt first:
   - runtime/cache residue such as SQLite WAL/SHM or local LSP state can be removed after brief inspection/back-up when it is the only residue.
   - tracked skill/docs/config changes or meaningful untracked reference files should be preserved before root cleanup continues.
3. Preserve meaningful dirt on a fresh branch/worktree based on the latest `origin/main`, not on the behind dirty root:
   - save a safety backup of the root diff and meaningful untracked files under `/tmp`.
   - `git worktree add .worktrees/<flat-name> -b <branch> origin/main`.
   - apply the tracked diff with `git apply --3way` and copy only the meaningful untracked support files.
   - run `git diff --check`, commit, push, and create/update the review PR using the repo's normal PR path.
4. Only after the preservation branch is pushed and verified, restore/remove the same files from root and fast-forward root `main` to `origin/main`.
5. Continue stale worktree/branch deletion from the clean, updated root.
6. Final verification must show:
   - root `main` equals `origin/main` and is clean.
   - only active/open-PR worktrees remain.
   - no registered worktree path is missing on disk.

## GitHub PR verification nuance

Some bot-created PR workflows run from `main`, so the workflow run's `headBranch` may be `main` even though the PR head is the pushed feature branch. After dispatch, if `gh pr view <branch>` does not find the PR immediately, query by head branch instead:

```bash
gh pr list --state all --head <branch> --json number,url,state,author,headRefName,title
```

Verify the PR author and `headRefOid` before cleaning the root copy.

## Runtime residue that can reappear

During repo-local Hermes cleanup, files such as `.hermes/kanban.db-wal` and `.hermes/kanban.db-shm` can reappear after tool calls. Remove them again at the end if they are the only remaining root residue, then re-run `git status --short --branch`.
