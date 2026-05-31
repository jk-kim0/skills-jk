# PR-less preservation during open-PR cleanup sweeps

Use this note when an `Open PR 점검` + `workspace 정리` sweep discovers a local branch/worktree that has no matching PR but has meaningful dirty content or ahead diff.

## Pattern

1. Do not delete the branch just because it has no PR.
2. Inspect the net diff against latest `origin/main` and run lightweight hygiene such as `git diff --check`.
3. If the diff is meaningful, preserve it by committing the local work, rebasing onto current `origin/main`, pushing the branch, and opening a narrow PR.
4. Immediately add the normal repo assignee when the open-PR review workflow requires it.
5. Treat the newly created preservation PR as part of the same open-PR sweep, not as a separate afterthought:
   - wait for required checks when the current pass requires completion;
   - inspect failed logs;
   - fix real build/test failures on that same preservation branch;
   - push fixes and re-check until the PR is mergeable or a clear blocker remains.
6. If later in the same delayed/repeated sweep that preservation PR has merged, remove its clean local worktree and branch during the final cleanup pass.

## CI failure interpretation

Preservation PRs often surface stale local assumptions because the work may have existed before the latest `main` contract changed.

Common examples:
- TypeScript build failures where an API route schema no longer matches the service input type after the preserved branch changed shared domain fields.
- Source-inspection tests that still assert old UI labels after the preserved branch intentionally changed the source contract.

Fix these as normal PR maintenance issues, not as reasons to abandon or delete the preserved branch.

## Reporting

Mention preservation explicitly in the final report:

- which PR-less branch was preserved;
- the PR number/URL created for it;
- any CI failures fixed while preserving it;
- whether it remained open or was later merged and cleaned up during the delayed repeat.