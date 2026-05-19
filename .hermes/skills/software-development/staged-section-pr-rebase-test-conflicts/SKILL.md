---
name: staged-section-pr-rebase-test-conflicts
description: Resolve rebase conflicts when multiple section-scoped PRs all append assertions to the same shared structure test file during staged route-local authoring work.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, rebase, tests, staged-prs, route-local-authoring, nextjs]
---

# Staged section PR rebase conflicts in shared test files

Use this when several small PRs each refactor one page section, but all of them touch the same shared structure test file (for example `tests/ai-dashi-page-structure.test.mjs`).

Typical symptom:
- each PR rebases cleanly except for one shared test file
- latest `main` already contains assertions from earlier merged sibling PRs
- your current PR adds only one more test block for its own section

## Core rule

When rebasing the current PR onto latest `origin/main`:
- keep the latest-main test coverage that already landed from earlier sibling PRs
- append only the current PR's section-specific assertions
- do not drop earlier merged assertions
- do not keep conflict markers or restore an older pre-main version of the file

## Recommended workflow

1. create a fresh worktree from the open PR branch tip
2. run `git rebase origin/main`
3. if the rebase stops on the shared test file, read:
   - the conflicted file in the PR worktree
   - the same file on latest `origin/main`
4. identify which test blocks are already on `main`
5. rebuild the file as:
   - latest-main content
   - plus the current PR's new section test block
6. stage the file and continue rebase with:
   - `GIT_EDITOR=true git rebase --continue`
7. force-push the rebased branch with:
   - `git push --force-with-lease origin HEAD:<pr-branch>`

## Practical heuristic

If earlier sibling PRs added tests for sections A and B, and the current PR adds section C:
- final rebased file should contain A + B + C
- not just C
- and not an older variant of A/B from before those sibling PRs merged

The same additive rule applies to shared category/sidebar data files, not only tests. Example: if latest `main` already added an `events` resource category and the current PR adds `tutorials`, the resolved `resource-category-data.ts` should keep `events` and add `tutorials`; when flattening the current PR before the parent is merged, keep only the current PR's category so the PR remains independent.

## Why this matters

In staged route-local authoring work, the implementation files can be independent enough to rebase cleanly, but the shared structure test file becomes an append-only hotspot. Treat the conflict as a merge of assertion coverage, not a choice between branches.

## Good verification after rebase

Run the narrow structure-oriented test suite that covers the shared file, for example:

```bash
node --test tests/ai-dashi-page-structure.test.mjs tests/ai-dashi-cta-links.test.mjs tests/launch-readiness-coverage.test.mjs
```

Then confirm the PR head moved and CI restarted.

## Anti-patterns

- taking only the PR side and dropping already-merged sibling tests
- taking only the main side and forgetting to add the current PR's section test
- resolving by hand but forgetting `GIT_EDITOR=true` in non-interactive environments
- assuming the implementation rebase result is enough without re-running the structure tests
