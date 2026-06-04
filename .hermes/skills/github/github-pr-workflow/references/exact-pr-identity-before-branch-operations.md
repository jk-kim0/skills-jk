# Exact PR identity before branch operations

Use this when the user names a specific GitHub PR number, especially during rebase, squash, conflict resolution, force-push, or follow-up work after context compaction.

## Rule

The named PR number is the source of truth. Do not infer the active PR from the current branch, a previous final summary, or a nearby PR number.

## Workflow

1. Before checkout/rebase/push, run:
   `gh pr view <number> --json number,headRefName,baseRefName,headRefOid,url`
2. Checkout the returned `headRefName` only after confirming it belongs to the requested PR number.
3. After rebase/amend/force-push, verify:
   - `git rev-parse HEAD origin/<headRefName>` match
   - `gh pr view <number> --json number,headRefOid,statusCheckRollup,url` returns the same requested PR number
   - `git merge-base --is-ancestor origin/<baseRefName> HEAD` passes when the task was to rebase onto latest base
4. Final report must name the same PR number and URL the user requested unless the user explicitly approved switching scope.

## Pitfall

After context compaction or when adjacent PRs share similar branch names, it is easy to continue with the wrong PR. Re-query the exact PR number at both the start and end of the operation.