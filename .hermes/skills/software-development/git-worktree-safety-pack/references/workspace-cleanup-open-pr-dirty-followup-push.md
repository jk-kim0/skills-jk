# Workspace cleanup: open-PR dirty follow-up and force-with-lease push

Use this reference when a repo-local workspace cleanup sweep finds an open-PR worktree that is not stale but becomes dirty or diverged during the final verification loop.

## Pattern

During cleanup, `origin/main` may have advanced or a sibling PR may have merged. A retained open-PR worktree can end up in a state like:

- the PR is still open;
- the worktree is clean initially, then final sweep finds dirty files;
- the branch is ahead/behind its upstream because it has been rebased locally onto the latest `origin/main` while the remote PR head still points at the old base;
- the dirty file is not a cleanup artifact but a same-scope implementation/test follow-up.

Do not delete, stash, or ignore this worktree. Treat it as part of the open PR preservation path.

## Steps

1. Confirm the PR is still open:
   - `gh pr view <number> --json state,headRefName,headRefOid,mergeStateStatus,url`
2. Inspect local relationship and payload:
   - `git status --short --branch`
   - `git rev-list --left-right --count @{upstream}...HEAD`
   - `git rev-list --left-right --count origin/main...HEAD`
   - `git diff --stat`
   - targeted `git diff -- <dirty-path>`
3. Decide whether the dirty payload belongs to that PR's scope.
   - If yes, commit or amend it into the retained PR branch.
   - If a follow-up test file appears after committing the implementation, inspect it too; include it when it updates same-scope structure/contract tests.
   - If no, revert or preserve in a separate appropriate branch only after proving it is meaningful and unrelated.
4. Before force-pushing, capture the current remote PR head OID from `gh pr view` and/or `git rev-parse origin/<branch>`.
5. Push with an explicit full-ref lease:
   - `git push --force-with-lease=refs/heads/<branch>:<expected-remote-oid> origin <branch>:refs/heads/<branch>`
6. If the push is rejected with `stale info`, fetch the specific branch, re-read the PR head OID, and retry only if the PR is still open and the remote head is the expected old PR head.
7. After push, GitHub's PR API can briefly report the old `headRefOid`. Wait briefly or re-query; do not assume the push failed if `git push` succeeded.
8. Re-run the final cleanup sweep:
   - root `git status --short --branch`;
   - dirty status for all retained worktrees;
   - unregistered `.worktrees/` child directories;
   - PR checks for any PR branch that was updated.

## Reporting

In the final report, distinguish:

- stale merged branches/worktrees removed;
- open PR worktrees intentionally retained;
- any open PR branch that was updated during cleanup, with the new short SHA;
- checks that are still pending because GitHub aggregation has not completed.
