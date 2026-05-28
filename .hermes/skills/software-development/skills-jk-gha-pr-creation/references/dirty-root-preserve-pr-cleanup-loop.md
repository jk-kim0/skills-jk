# Dirty root preserve → bot PR → clean root loop

Use this note when a `skills-jk` cleanup/main-update request starts from root `main` with meaningful `.hermes/skills/**` tracked/untracked changes while `main` is behind `origin/main`.

## Pattern confirmed

1. Fetch/prune and inspect root first:
   - `git status --short --branch`
   - `git diff --stat`
   - `git diff --name-status`
   - `git ls-files --others --exclude-standard`
2. Treat meaningful skill/reference changes as PR candidates, but do not commit from root `main`.
3. Save a safety copy under `/tmp`, create a fresh repo-local worktree from latest `origin/main`, and apply the tracked root diff there.
4. If `git apply --3way` conflicts in append-style skill files, preserve latest-main guidance and add only the real local additions. Do not let a behind-root copy delete newly merged lines.
5. Copy only meaningful untracked support files into the fresh worktree.
6. Run lightweight verification before commit:
   - `git diff --check`
   - targeted conflict-marker scan: `^(<<<<<<<|>>>>>>>)( |$)|^=======$`
   - final payload list with `git diff --name-only origin/main...HEAD | sort`
7. Commit and push the fresh branch, then create the PR through `.github/workflows/create-pr.yml`.
8. Verify the PR object and branch separately:
   - PR author is `app/github-actions`
   - PR `headRefOid` equals `git ls-remote origin refs/heads/<branch>`
   - PR file list matches the fresh worktree payload
   - absence of `statusCheckRollup` / branch runs is not itself a failure for docs/skill-only PRs
9. Only after remote head + PR verification, restore/remove the same root-local copies and fast-forward root `main` to `origin/main`.
10. Continue stale cleanup: remove merged/gone worktrees/branches only after GitHub PR state confirms `MERGED` and a two-dot/tree diff versus `origin/main` is empty.
11. Final report should distinguish:
   - root `main` alignment and clean status
   - the new PR URL/head/payload
   - deleted stale worktrees/branches
   - intentionally preserved open-PR worktrees

## Pitfall

Do not report cleanup complete while the same root-local files remain dirty after their payload was safely pushed to a PR branch. For `main 업데이트 + workspace 정리`, the expected end state is clean root `main` aligned to `origin/main`, with the review payload preserved in the PR worktree/branch.