# Merged News MDX Follow-up Pattern

Use this when a user asks for a small follow-up edit to an MDX news item or branch name that appears to be tied to an already-merged PR.

## Workflow

1. Confirm the active root/worktree branch first; do not assume the current checkout is the target branch.
2. If a named branch or worktree exists but its upstream is `[gone]`, check whether the matching PR is already merged:
   - `gh pr list --head <branch> --state all --json number,title,state,mergedAt,closedAt,url`
3. If the PR is merged and the remote branch was deleted, do not add new commits to that stale branch.
4. Start a fresh branch from latest `origin/main` in the relevant worktree or a new repo-root `.worktrees/` worktree.
5. Reapply only the requested minimal change from the stale worktree/diff.
6. For content that cannot be found in the current checkout, use git history before asking the user:
   - `git log --all --name-only --pretty=format: | sed '/^$/d' | sort -u | grep '<substring>'`
   - `git grep -n '<exact text>' $(git rev-list --all) -- . 2>/dev/null | head -50`
7. For narrow MDX copy/markup fixes, verify with `git diff --check` and source inspection; skip local build unless the user requests it or the change affects code/schema/routing.
8. Commit, push, and open a new PR if the user's repo workflow expects PR follow-through.

## Pitfall

A merged PR's deleted remote branch can still have a local worktree with the exact target file. It is useful for locating the previous content, but it is not the right branch to push follow-up changes to. Always base the follow-up on current `origin/main` once the original PR is merged.
