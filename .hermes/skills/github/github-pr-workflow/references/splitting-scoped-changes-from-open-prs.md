# Splitting scoped changes out of open PRs

Use when a user asks to move one route, feature, commit, or file subset from an existing open PR into a separate PR while keeping the original PR open for the remaining scope.

## Workflow

1. Inspect the source PR before rewriting anything:
   - `gh pr view <pr> --json headRefName,baseRefName,headRefOid,state,title,url,statusCheckRollup`
   - `gh pr diff <pr> --name-only`
2. Identify whether the desired scope is already isolated as one or more commits.
   - If yes, create a fresh branch from the latest base and `git cherry-pick <commit...>`.
   - If no, create a fresh branch and restore only the scoped paths from the source PR with `git checkout <source-sha> -- <paths>` or interactive staging.
3. Create the split PR first. The body should say it was split from the source PR and list the exact scoped files or route family.
4. Rewrite the original PR branch to remove the split scope.
   - For commit-isolated scope: `git rebase --onto origin/<base> <last-split-commit> <source-branch>` drops the split commit(s) and replays the remaining commits.
   - If rebase leaves the worktree detached, attach the branch ref before pushing: `git branch -f <source-branch> HEAD && git checkout <source-branch>`.
5. Push the rewritten source PR branch with `git push --force-with-lease origin <source-branch>`.
6. Verify both PRs with GitHub compare/API as well as local git:
   - `git diff --name-only origin/<base>...HEAD`
   - `gh api repos/<owner>/<repo>/compare/<base>...<source-branch> --jq '.files[].filename'`
   - `gh pr view <source-pr> --json headRefOid,statusCheckRollup`
7. Update the original PR title/body so it no longer claims the split scope. Add a short split-scope note linking to the new PR.
8. Report both PR URLs and current check status. Do not passively wait for long-running CI unless the user asked you to watch.

## Pitfalls

- Do not rely only on the PR title/body after splitting; stale descriptions can mislead reviewers even when the diff is correct.
- Do not assume `git rebase --onto` left you on the named branch. Verify `git branch --show-current` and branch ref SHA before force-pushing.
- Do not treat a stale `gh pr diff` result immediately after force-push as definitive; re-check with `gh pr view` head SHA and the compare API.

## Session-derived note

This pattern came from splitting a `/company/certifications` route change out of an open PR that also contained news content changes. The scoped change was already isolated in the first commit, so the safe path was: cherry-pick that commit to a new branch and PR, rebase the original branch with `--onto` to drop that first commit, force-with-lease push, then verify with compare API because `gh pr diff` briefly showed stale file names after the force-push.
