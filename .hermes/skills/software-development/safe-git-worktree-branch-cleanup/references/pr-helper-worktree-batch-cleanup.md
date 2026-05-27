# PR helper worktree batch cleanup pattern

## Context

In PR-heavy repos with stacked or parallel rewrite workflows, helper worktrees with the naming pattern `work/prNNN-*` (e.g. `work/pr824-fix`, `work/pr851-fix`) are sometimes created automatically by agent tools or scripts to hold follow-up fixes, rebase results, or speculative edits for open PRs.

These helpers share the following characteristics:
- The branch name follows `work/pr<number>-<suffix>` (commonly `-fix`)
- The worktree path mirrors the branch under `.worktrees/pr<number>-<suffix>/`
- They are **not** the official open PR branch (which is usually `feat/*` or `refactor/*`)
- They have no open GitHub PR of their own (`gh pr list --head work/prNNN-fix` returns empty)
- They are usually clean and contain narrow diffs versus `origin/main`

## Critical auto-recreation behavior

On repeated cleanup sessions, these helper worktrees can **reappear automatically** after deletion, because:
1. Background agent sessions or cron-style tasks recreate them from script definitions
2. The `.worktrees/pr*-fix` directories may already exist but were unregistered; after `git worktree prune`, a subsequent `git worktree add` recreates them
3. The parent repo has checked-in automation that links certain PRs to helper worktrees

**Lesson from session 2025-06-27**: after deleting `pr863-fix` and `pr864-fix` worktrees and branches, they immediately reappeared in the very next `git worktree list` output. The correct response is to delete them again and verify with a final `git worktree list`.

## Detection

```bash
# List all local branches matching the helper pattern
git branch --format='%(refname:short)' | grep '^work/pr[0-9]\+-

# Check for open PRs on these branches
for b in $(git branch --format='%(refname:short)' | grep '^work/pr[0-9]\+-'); do
  count=$(gh pr list --repo <owner/repo> --head "$b" --state open --json number | jq length)
  echo "$count $b"
done
```

## Safe batch removal

When **all** of the following are true:
1. The branch matches `work/prNNN-*`
2. No open PR exists for that exact branch
3. The worktree is clean (no uncommitted changes)
4. Its content is a subset or alternative of an existing open PR branch

Batch remove with a single shell loop:

```bash
for name in pr824-fix pr825-fix pr826-fix pr827-fix \
            pr839-fix pr851-fix pr852-fix pr853-fix \
            pr855-fix pr856-fix pr857-fix pr858-fix \
            pr859-fix pr860-fix pr861-fix pr862-fix; do
  git worktree remove --force "/path/to/repo/.worktrees/$name" 2>/dev/null
  git branch -D "work/$name" 2>/dev/null
  echo "REMOVED $name"
done
```

## Verification after batch cleanup

Always run a final verification pass because auto-recreation can happen mid-session:

```bash
git worktree list | grep -c 'work/pr[0-9]\+-'
# Should return 0 if all helpers were successfully removed
```

If the count is non-zero, identify which ones reappeared and remove them again.

## When NOT to remove

Do NOT batch-remove `work/pr*` branches indiscriminately if:
- The branch has an open PR of its own
- The worktree is dirty (may contain unpublished local work)
- The branch is the currently checked-out branch in any worktree you intend to keep
- The branch name does NOT match `work/prNNN-*` but is something like `work/some-feature` (could be legitimate unpublished work)
