# Final PR metadata after rebase or amend

Use this when the user asks to rebase a PR onto latest main and rewrite the PR title/description, or when later amendments change the final PR scope.

## Pattern

1. Treat title/body rewriting as a finalization step, not only as an early PR-edit step.
2. After conflict resolution, content/asset renames, squash/amend, and force-push are complete, re-read the final diff against the latest base (`origin/main...HEAD`) and describe only what is currently in the branch.
3. Update the PR title and description to match the final branch contents, including any explicitly out-of-scope split work.
4. If a later follow-up amendment changes filenames, routes, tests, or user-visible scope, update the PR body again before reporting completion.
5. After every amend/force-push, verify local and remote head equality, PR `headRefOid`/`baseRefOid`, `mergeStateStatus`, and check rollup. Do not reuse successful CI output from an older SHA as current status.

## Useful commands

```bash
git fetch origin main
git log --oneline origin/main..HEAD
git diff --stat origin/main...HEAD
git status --short --branch
gh pr view <pr> --json title,body,headRefOid,baseRefOid,mergeStateStatus,statusCheckRollup
```

Use `gh pr edit <pr> --title ... --body-file ...` after preparing a final body file.
