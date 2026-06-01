# Repeated cleanup after merged preservation PR with stale deletion hunks

Use this reference when a repeated `main 업데이트` / `workspace 정리` sweep starts right after a prior preservation PR has merged, but the root checkout is still on the pre-merge `main` and contains additional authored skill/docs changes.

## Symptom

After `git fetch --prune`, the state looks like:

- root `main` is behind `origin/main` by the just-merged preservation PR;
- the previous preservation worktree branch tracks a deleted remote head and its PR is `MERGED`;
- root is dirty with new authored changes;
- `git diff origin/main --stat` shows a mix of useful additions plus many apparent deletions of files that now exist on `origin/main`.

Those deletion hunks are usually stale root-baseline artifacts, not intended removals.

## Safe preservation pattern

1. Verify the prior PR state before deleting anything:
   - `gh pr view <prior-pr> --json state,mergedAt,headRefName,url`
   - targeted `gh pr list --state all --head <branch>` for each local branch.
2. Save a repo-external backup of the dirty root:
   - `git diff --binary > /tmp/<repo>-preserve/local.diff`
   - `git ls-files --others --exclude-standard > /tmp/<repo>-preserve/untracked.txt`.
3. Create a fresh repo-root worktree from latest `origin/main` on a new preservation branch.
4. Do not apply the dirty root as a whole patch when the diff includes deletion hunks for files that exist on latest `origin/main`.
5. Instead, copy only root paths that currently exist and are authored payload into the fresh worktree:
   - modified tracked files that carry real new guidance;
   - untracked authored skill/reference directories;
   - exclude runtime/cache paths such as `.hermes/lsp/`, `.hermes/pairing/`, sessions/logs, profile caches, and curator backups.
6. Do not delete files from the fresh worktree just because they are absent in the stale root checkout. Keep `origin/main` as the source of truth for already-merged files.
7. Run lightweight checks in the fresh worktree:
   - `git diff --check`
   - changed-file conflict-marker scan using `^(<<<<<<<|>>>>>>>)( |$)|^=======$`
   - `git diff --name-status origin/main --` to confirm there are no unintended deletions.
8. Commit, push, and create/update the PR through the repository’s normal PR mechanism.
9. After verifying remote head and PR head, reset root to `origin/main`, remove only the now-preserved untracked root payload/runtimes, then delete the merged prior worktree/branch.
10. Re-run the full dirty sweep and targeted PR lookup until only clean root `main` plus clean open-PR worktrees remain.

## Pitfalls

- Do not open a PR from the stale root branch or stale previous preservation branch; it can reintroduce old deletions.
- Do not use `git clean -fd -- .hermes/skills` before the new preservation PR is verified; untracked authored references may be lost.
- Do not push a rebased local branch whose remote head was deleted after merge. Treat the merged branch as local residue and create a fresh follow-up branch from `origin/main` for any new payload.
- In the final report, distinguish: prior PR merged and local residue removed; new PR opened for additional payload; root `main` reset/updated to latest `origin/main` and clean.
