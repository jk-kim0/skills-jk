# Closed / merged PR follow-up after late feedback

Use this when a user asks for a follow-up change on a PR that may have been merged while the session continued.

## Problem

After a PR is merged, pushing a branch with the same name may recreate the remote branch, but it does not update the already-merged PR. GitHub CLI/GraphQL can also keep showing the old PR head SHA for the closed PR, which makes it look as if the push did not work or as if the branch is stale.

## Check first

Before pushing follow-up work to an existing PR branch, check whether the original PR is still open:

```bash
gh api repos/<owner>/<repo>/pulls/<pr> --jq '{state,merged,merged_at,merge_commit_sha,head:{ref:.head.ref,sha:.head.sha},base:{ref:.base.ref,sha:.base.sha}}'
```

Also check for an already-open follow-up PR with the same head branch before creating a new one:

```bash
gh pr list --state open --head <branch> --json number,title,url,headRefOid,mergeStateStatus
```

## Correct action

- If the original PR is still open: rebase the branch onto latest `origin/main`, push with `--force-with-lease`, then re-query PR head/checks.
- If the original PR is merged/closed: create a new follow-up PR from latest `origin/main` with only the follow-up diff.
- If `gh pr create` fails with a transient GitHub GraphQL 504, first re-run `gh pr list --state open --head <branch>` to avoid duplicate PRs, then retry creation.

## Reporting

State explicitly that the original PR was already merged/closed and provide the new follow-up PR URL. Do not imply the merged PR was updated.