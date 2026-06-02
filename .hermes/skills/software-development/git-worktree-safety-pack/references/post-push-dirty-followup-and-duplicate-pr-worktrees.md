# Post-push dirty follow-up and duplicate PR worktrees

Use this reference during repo-local workspace cleanup when a preserved PR branch was just created/amended/force-pushed, or when a duplicate worktree appears for the same PR content.

## Pattern

After preserving PR-less dirty work into an open PR, do not assume the worktree is clean just because the push succeeded.
Run another dirty sweep immediately on the source and retained PR worktrees.
In several web UI cleanup sessions, related files appeared after the first commit/amend, including source/test pairs, page/widget pairs, and runtime residue.

## Required handling

1. After every `git commit --amend` + `git push --force-with-lease`, run `git status --porcelain=v1 -uall` in that worktree before moving on.
2. If new dirty files are clearly the same PR scope, inspect the diff, include them in the same PR, amend, force-push, and repeat the sweep.
3. If a dirty file is a follow-up test/spec for behavior that is not implemented in the PR, do not preserve it blindly.
   Either implement the missing behavior if it is clearly required for the PR, or revert the out-of-scope test so the preservation PR stays self-contained.
4. If a duplicate worktree/branch appears with the same `HEAD` as a retained open-PR branch, especially one tracking a stale `origin/pr/<number>` ref, verify with:
   - `git rev-parse HEAD`
   - `git rev-parse <retained-branch>`
   - `gh pr list --state open --head <retained-branch> --json number,headRefOid,title`
   Then remove the duplicate worktree and delete the duplicate local branch.
5. GitHub PR metadata can be stale immediately after a force-push.
   Compare `git ls-remote origin refs/heads/<branch>` with `gh pr view <number> --json headRefOid,statusCheckRollup` before assuming checks are attached to the latest head.
6. Do not start a delayed wait/recheck timer until every retained worktree is clean and duplicate worktrees have been removed.

## Reporting shape

When reporting a delayed cleanup pass, distinguish:

- PRs that are clean/pass now.
- PRs whose latest head is pushed but checks are still queued/in progress.
- Local cleanup state: root `main`, retained open-PR worktrees, duplicate/stale worktrees removed, and whether any dirty follow-up was included or reverted.
