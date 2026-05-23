# Repeated workspace sweep final-clean and dedup loop

Use this reference when the user repeatedly asks, in `skills-jk`, to update `main`, inspect local changes, and preserve meaningful changes in PRs/worktrees.

## Core lesson

Treat copy-to-worktree preservation and root workspace cleanliness as separate deliverables:

1. Preserve meaningful root-local changes in the narrowest appropriate PR/worktree.
2. Verify the PR branch local HEAD equals the remote ref and is based on latest `origin/main`.
3. Restore the same root copies after preservation when the request is a main-update/workspace-cleanup flow.
4. Re-run root status after every preservation step; newly loaded or patched skills can create more tracked/untracked files during the session.
5. Stop only when root `main` is aligned with `origin/main` and clean, unless the user explicitly asked to leave the original dirty root in place.

## Multi-PR dedup loop

When several open follow-up PRs exist:

- Compare root candidate files against each open PR worktree before deciding where to preserve them.
- Amend an existing PR when the new delta belongs to that PR's class.
- Create a separate fresh latest-main worktree/branch only when the delta is a different class.
- Compare payloads across all open follow-up PRs before final reporting.
- If a broad PR accidentally includes a file that belongs to a narrower PR, amend the broad PR to remove the duplicate and force-with-lease push.

## Verification checklist

For each PR branch:

- `git rev-parse HEAD`
- `git ls-remote origin refs/heads/<branch>`
- `git merge-base HEAD origin/main` equals `git rev-parse origin/main`
- `git diff --name-status origin/main...HEAD` is the authoritative payload list
- `gh pr view <number> --json state,headRefOid,mergeStateStatus,statusCheckRollup`

For root:

- `git status --short --branch` shows `main...origin/main` with no entries
- `git rev-list --left-right --count main...origin/main` is `0 0`

## Reporting pattern

Report separately:

1. Final `main` / `origin/main` alignment and whether root is clean.
2. Which local changes collapsed because latest main or earlier merged PRs already contained them.
3. Which surviving changes were preserved, with PR URL, branch, commit SHA, and final payload list.

Do not call the sweep complete while the root checkout still has the same dirty files already preserved in a PR, unless the user explicitly asked to keep them dirty.
