# Merged PR as follow-up context

Use this when the user points to a PR URL/number and asks for a related follow-up change.

## Decision rule

1. First inspect the PR state:

```bash
gh pr view <number> --json state,mergedAt,headRefName,headRefOid,baseRefName,title,url
```

2. If the PR is `OPEN`, update the existing PR branch in a fresh worktree.
3. If the PR is `MERGED` or `CLOSED`, do not revive the old branch. Treat the PR as context for code that has already landed, then start a fresh latest-main branch/worktree.

## Common pattern

A user may say that a page or feature was "implemented in PR N" and ask to apply a newer shared primitive or follow-up cleanup to it. If both PR N and the primitive PR are already merged:

- fetch latest origin/main
- create a fresh worktree from `origin/main`
- modify the now-landed code on main
- run the narrow route/source test for the affected page
- open a new follow-up PR

This avoids resurrecting deleted merged branches and prevents old PR metadata/commit history from polluting the new follow-up diff.

## Verification

After pushing the new follow-up branch:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/<branch>
gh pr view <new-pr> --json headRefOid,baseRefName,statusCheckRollup,url
```

The local HEAD, remote branch HEAD, and PR `headRefOid` should match.
