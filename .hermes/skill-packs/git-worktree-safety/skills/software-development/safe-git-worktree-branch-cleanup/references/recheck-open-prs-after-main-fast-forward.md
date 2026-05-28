# Re-check open PR branches after root main fast-forward

Session learning from a repo-local workspace cleanup in `corp-web-app`:

- Initial classification preserved a worktree/branch because it matched an open PR head.
- During the same cleanup, root `main` was fast-forwarded to `origin/main`.
- That fast-forward pulled in a newly merged PR, so one previously open PR branch became stale while the cleanup was still in progress.
- A final open-PR snapshot caught the change and allowed safe deletion of the now-merged clean worktree/branch.

Reusable rule:

1. Take the initial `env -u GITHUB_TOKEN gh pr list --state open --json number,headRefName,title,url` snapshot before deleting anything.
2. Delete only clean, non-open-PR stale candidates from that snapshot.
3. Fast-forward root `main` when safe.
4. After the fast-forward, run a fresh open-PR snapshot, not just `git status` / `git worktree list`.
5. If a branch that was preserved earlier is no longer open and its PR is now merged/closed, reclassify it before final reporting.
6. If its worktree is clean and its PR is merged, remove the worktree and delete the local branch in the same cleanup pass.

GitHub CLI safety note:

- In environments with a GitHub CLI gate, use `env -u GITHUB_TOKEN gh ...` for read-only `gh pr list` / `gh pr view` calls as well.
