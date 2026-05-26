# Rebase and CI follow-up for an open PR

Use this when the user asks to rebase an existing PR onto latest main and fix CI.

Workflow:
1. Reuse the existing PR branch/worktree. Do not create a new PR for the same review cycle unless the original PR is merged/closed or the user explicitly asks.
2. Fetch `origin`, check PR state, and rebase the PR branch onto `origin/main`.
3. If CI is already failing, inspect failed jobs with `gh run view <run-id> --log-failed` or the PR `statusCheckRollup` before changing code.
4. Reproduce the failed job locally as narrowly as possible first: focused test files, then the CI test group if dependencies are available.
5. If the failure is a current-main/test-contract mismatch that blocks the rebased PR but is outside the original narrow feature scope, make the smallest CI-stabilizing fix on the same PR branch and describe it explicitly in the PR body.
6. Push to the same PR branch, then re-check the new head SHA until required checks are green or a new actionable failure appears.
7. Report final state with PR URL, head SHA, merge state, and check conclusions.

Pitfalls:
- Do not treat a no-op rebase as completion if the PR still has red CI.
- Do not leave the user with “checks are running” when a short follow-up poll would determine whether the fix worked.
- Do not encode local dependency/setup misses as repo rules; distinguish local worktree environment issues from CI-runner failures.
