# Repo-local cleanup with meaningful dirty root changes

Use this reference when a repo-local `workspace 정리` / stale worktree cleanup or repeated local-sweep request starts from a root checkout on `main` that is dirty.

## Core distinction

Treat root cleanup and meaningful local preservation as separate deliverables:

- If the user asks for workspace cleanup / main update and expects a clean root, preserve meaningful root dirt first, then restore/remove the same root copies so root `main` ends clean and aligned.
- If the user explicitly says to copy/clone local changes into a worktree/PR, preserve the payload in the worktree/PR but leave the original meaningful root changes in place; remove only obvious runtime residue.

## Pattern

1. Fetch/prune and inspect root status before deleting stale worktrees or fast-forwarding main.
2. Classify root dirt first:
   - runtime/cache residue such as SQLite WAL/SHM, local LSP state, or curator backups can be removed after brief inspection/back-up when it is the only residue.
   - tracked skill/docs/config changes and meaningful untracked reference/support files should be preserved before root cleanup continues.
3. Preserve meaningful dirt on a fresh branch/worktree based on latest `origin/main`, not on a behind dirty root:
   - save a safety backup of the root diff and meaningful untracked files under `/tmp`.
   - `git worktree add .worktrees/<flat-name> -b <branch> origin/main`.
   - apply the tracked diff with `git apply --3way` and copy only the meaningful untracked support files.
   - run `git diff --check`, commit, push, and create/update the review PR using the repo's normal PR path.
4. Verify the preservation before touching the root copy:
   - local worktree `HEAD` equals `git ls-remote origin refs/heads/<branch>`.
   - PR `headRefOid` equals the pushed commit.
   - PR file list is exactly the intended meaningful payload.
5. Then choose root handling from the user wording:
   - cleanup/main-update wording: restore/remove the same root files and fast-forward root `main` to `origin/main`.
   - copy/clone wording: leave the meaningful root files dirty, but remove runtime WAL/SHM and report clearly that the PR contains a copied payload while root still has the original changes.
6. Continue stale worktree/branch deletion only from a known root state.

## Final verification checklist

- Root `main` equals `origin/main`; if copy/clone mode intentionally leaves root dirty, say so explicitly and list the remaining files.
- Only active/open-PR worktrees remain.
- No registered worktree path is missing on disk.
- Runtime WAL/SHM files such as `.hermes/kanban.db-wal` and `.hermes/kanban.db-shm` are removed at the end if they reappear.

## GitHub PR verification nuance

Some bot-created PR workflows run from `main`, so the workflow run's `headBranch` may be `main` even though the PR head is the pushed feature branch. After dispatch, if `gh pr view <branch>` does not find the PR immediately, query by head branch instead:

```bash
gh pr list --state all --head <branch> --json number,url,state,author,headRefName,title
```

Verify the PR author and `headRefOid` before cleaning or reporting the root copy.
