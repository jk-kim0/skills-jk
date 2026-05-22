# Copy-to-worktree repeated local sweep pattern

Use this when the user repeatedly asks to update `main`, summarize local changes, and create PRs from meaningful local changes in `skills-jk`.

## Situation

The root checkout may remain dirty because the user explicitly asked to copy local changes into a new worktree, not to clean/reset root. A previous copy-to-worktree PR may merge between repeated requests, so `origin/main` can advance while the root checkout still contains the same local files.

## Pattern

1. `git fetch --prune origin` and inspect open PRs.
2. Fast-forward `main` when possible. If dirty root blocks the merge, do not immediately classify all dirt as unpublished work.
3. Create a fresh worktree from latest `origin/main` and copy the root candidate files into it.
4. Let already-upstreamed files collapse to no-op in the fresh worktree. Trust `git -C <worktree> status --short` and `git diff origin/main...HEAD` there as the payload source of truth.
5. Exclude runtime residue such as `.hermes/lsp/**`.
6. If there is a residual meaningful diff, commit/push it and create the PR through `.github/workflows/create-pr.yml`.
7. If the user asked to copy/clone local changes, leave root dirt intact after PR creation and report that explicitly. Only reset/clean root if the user also asked for cleanup.
8. Re-check root status after final verification. New tracked skill/reference changes can appear during the session; if they are meaningful and not part of the just-created PR, split them into another narrow PR rather than silently leaving them unreported.

## Pitfalls

- Do not create a duplicate PR for files already absorbed by the previous merged copy-to-worktree PR.
- Do not summarize the stale root candidate set as if it were the PR payload; summarize the fresh worktree diff.
- If the user repeats the same request mid-workflow, continue the in-progress flow with fresh state checks instead of restarting from the old assumptions.
- `mergeStateStatus: BLOCKED` with zero attached checks can be a normal fresh docs/skills PR state in this repo; verify branch SHA and PR object rather than treating it as a failed check.
