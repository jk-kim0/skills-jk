# Cross-repo workspace cleanup: concise output and dirty-root preservation

Use this note when the user asks to inspect and clean every git repo under `~/workspace` or another broad workspace root.

## Observed pattern

A cross-repo cleanup can touch many repositories and default branches. Some `git merge --ff-only` operations produce extremely large fast-forward summaries, especially monorepos or content repositories. If those raw summaries are printed inline, the useful cleanup report can be truncated and later verification becomes harder to read.

Dirty root checkouts also commonly block default-branch fast-forward. Examples include generated comparison output, release-note work, local confluence-mdx var files, or repo-managed Hermes config edits. Do not reset or stash these just to make the workspace look clean.

## Recommended pattern

1. Discover immediate child git directories under the workspace root and group by `git rev-parse --git-common-dir` so linked worktrees are processed through their owner repo.
2. For each owner repo:
   - `git fetch origin --prune`
   - prune missing worktree registry entries
   - if the root checkout is clean and already on the default branch, `git merge --ff-only origin/<default>`
   - if the root checkout is dirty, preserve it and record a short dirty preview; do not switch branches or fast-forward it
   - remove only confirmed stale/merged/prunable worktrees and branches
   - preserve open-PR worktrees and unique local branches
3. Write full machine-readable results to a temp JSON file such as `/tmp/workspace_cleanup_results.json`.
4. Print only a concise per-repo summary while running:
   - repo name
   - action names
   - deleted worktree/branch names
   - preserved dirty/open/unique items
   - errors
5. After cleanup, re-scan owner repos and report a compact final status table.

## Output pitfall

Avoid printing raw fast-forward file lists for large repos in the main terminal response. They can be tens or hundreds of thousands of characters and drown out the actual cleanup result. Store full stdout in JSON/log output if needed, but summarize it in the user-facing report as `ff_default <branch>`.

## Preservation rule

A dirty root checkout may remain behind its remote default branch after cleanup. That is an intentional safe outcome, not a failure. Report it explicitly as preserved due to local dirt, with a short preview of the blocking files.
