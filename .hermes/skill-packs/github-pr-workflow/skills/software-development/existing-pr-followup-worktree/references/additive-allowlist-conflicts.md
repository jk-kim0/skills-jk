# Additive allowlist conflicts during existing PR follow-up

Use this reference when an open PR is green in CI but GitHub reports `mergeStateStatus=DIRTY` after another PR landed on `main`.

Observed pattern:
- The open PR adds one route/config entry to a shared allowlist or table.
- A recently merged PR adds different entries to the same array/table.
- Rebase produces a content conflict even though both changes are valid.

Preferred resolution:
1. Rebase the existing PR branch onto current `origin/main` in a fresh worktree.
2. Inspect the conflicting file and identify latest-main entries versus PR-specific entries.
3. Treat allowlists, navigation maps, route tables, test matrices, and similar config arrays as additive by default.
4. Preserve both sides unless code comments, tests, or product requirements show that one entry replaces the other.
5. Run the narrow test that exercises the combined list.
6. Verify ancestry before pushing:
   - `git merge-base origin/main origin/<pr-branch>` equals `origin/main`
   - `git rev-list --left-right --count origin/main...origin/<pr-branch>` is usually `0 1` for a one-commit PR
7. Force-push back to the same PR head with `--force-with-lease`.
8. Refresh the PR title/body in the repository's required language and report that new CI runs are attached to the new head SHA.

Concrete example:
- Latest main added legal route rewrite entries such as `/privacy-policy` and `/terms-of-service`.
- The open PR added `/eula` to the same middleware default-locale rewrite allowlist.
- Correct conflict resolution preserved `/eula` and all legal entries, then reran `npm exec vitest run src/__tests__/middleware.test.ts`.
