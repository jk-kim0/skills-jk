# Merged preservation PR branch refusal during cleanup

Use this reference when a cleanup/preservation sweep is updating a preservation PR branch, but the original PR is merged while the agent is still working.

## Signal

- A push or force-push to the previous preservation branch is rejected, or PR metadata shows the PR was merged while the local branch/worktree still has follow-up changes.
- The root/main cleanup still has meaningful local skill/docs payload that must be preserved.

## Safe response

1. Do not resurrect or force-update the branch of a merged PR.
2. Fetch and fast-forward the root/base `main` to the latest `origin/main`.
3. Create a fresh worktree/branch from the latest main.
4. Copy or re-apply only the selected authored payload; do not replay the stale whole patch, because it may contain deletion hunks for files already merged into main.
5. Commit, push, and create a new PR for the remaining payload.
6. Remove the merged PR's stale local worktree/branch after verifying the new PR branch contains the intended files and the root checkout is clean.
7. Final report should explicitly distinguish:
   - root `main` status and SHA,
   - the new open PR/worktree intentionally retained,
   - the merged/stale worktree/branch removed,
   - whether CI/check rollups are absent, pending, blocked, or failing.

## Pitfall

A merged preservation PR changes the meaning of the local diff. Treat broad stale diffs as suspicious; preserve only live authored content onto a fresh latest-main branch.