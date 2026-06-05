# Reverting a merged frontend PR in outbound-agent

Use this reference when the user asks to cancel/revert a merged frontend/UI PR in `querypie/outbound-agent`.

## Pattern

1. Confirm repo state in the root checkout with `git status --short --branch`.
2. Fetch and fast-forward clean local `main` to latest `origin/main` before basing the revert.
3. Inspect the target PR with `gh pr view <pr> --json number,title,state,baseRefName,headRefName,mergeCommit,mergedAt,url`.
4. If `state` is `MERGED`, use the PR's `mergeCommit.oid` and create a repo-local worktree from latest `origin/main`.
5. Run `git revert -m 1 --no-edit <mergeCommitOid>` to cancel the merged PR without rewriting main history.
6. Inspect `git diff --stat origin/main..HEAD` to make sure the net diff only removes the target PR's files/hooks/tokens/tests.
7. Run at least `git diff --check origin/main..HEAD`.
8. Re-fetch/rebase, push, and create a new PR with a Korean title/body.
9. Avoid issue-closing keywords in the PR body unless the user explicitly asks to close an issue.
10. Watch CI briefly; if checks remain pending, report the current check statuses instead of waiting silently.

## Example commands

```bash
git fetch origin --prune
git merge --ff-only origin/main
env -u GITHUB_TOKEN gh pr view 257 --json number,title,state,mergeCommit,mergedAt,url --jq '.'
git worktree add -b revert/pr-257-viewport-menu .worktrees/revert-pr-257 origin/main
cd .worktrees/revert-pr-257
git revert -m 1 --no-edit <mergeCommitOid>
git diff --check origin/main..HEAD
git fetch origin --prune
git rebase origin/main
git push -u origin revert/pr-257-viewport-menu
env -u GITHUB_TOKEN gh pr create --base main --head revert/pr-257-viewport-menu --title 'revert: ... 취소' --body-file <body.md>
env -u GITHUB_TOKEN gh pr checks <new-pr>
```

## Pitfalls

- Do not revert from a stale local main; PRs may have landed after the target PR.
- Do not use `git revert <mergeCommit>` without `-m 1` for a merge commit.
- Do not include `Closes #...` / `Fixes #...` in revert PR bodies by accident.
- Do not long-watch CI in silence; short active watch and status report is preferred.
