# Repeated cleanup: helper worktree regeneration and stale branch resurrection

## Pattern: PR re-open after close causes worktree resurrection

In heavy PR repos, a branch/worktree may be removed during cleanup because its PR closed, but then the user re-opens the PR or creates a new PR from the same branch. This creates a "resurrection" scenario where a previously-removed worktree re-appears.

**Real example from `refactor/resource-mdx-collection`:**
- PR #894 was closed during one cleanup pass, worktree removed, branch deleted
- PR was later re-opened (or a new PR created from the same branch)
- New worktree `refactor-resource-mdx-collection` was created but its branch had `ancestor == origin/main` with empty diff because the actual feature work was already merged or moved elsewhere
- The branch appeared in `git branch -vv` without a `[gone]` marker because it tracked a fresh remote ref
- Correct classification was "ancestor + clean + open PR". The worktree was kept because it had an active open PR, even though its content was functionally merged

**Classification rule when a previously-stale branch re-appears:**
1. If the branch is `ancestor of origin/main` + `clean` + `empty diff`: it is a zombie branch even with an open PR. Treat as stale unless it carries genuinely new unpublished work.
2. If the branch is `NOT ancestor` + `has unique diff`: it may be resurrected with new work. Keep it.
3. Always cross-check with `git diff --stat origin/main..branch` before deciding.

## Pattern: helper worktree `work/pr*-fix` auto-generation

Some repos automatically generate helper worktrees named `work/pr824-fix`, `work/pr825-fix`, etc. These are created by agent sessions or CI helpers during conflict resolution or rebase follow-up.

**Classification:**
- These are typically branch-backed worktrees with no corresponding open PR (the open PR uses the official branch name, e.g. `feat/fde-services-tailwind-route-layout`, not `work/pr824-fix`)
- Check if the helper branch has an open PR: `gh pr list --repo $repo --head work/pr824-fix --state open`
- If no open PR AND clean AND `ancestor == origin/main` → stale, remove both worktree and branch
- If no open PR BUT `NOT ancestor` OR `has unique diff` → evaluate further; it may contain unpublished work intended for the next push

## Pattern: orphan local branches (no worktree, no open PR)

After repeated cleanup, some branches may become "orphans":
- The worktree was removed in a previous pass
- The PR was merged/closed
- But the local branch was not deleted (e.g. due to `git branch -d` failing because it was not an ancestor)

**Detection:**
```bash
git branch --format='%(refname:short)' | while read b; do
  found=$(git worktree list | grep -F "[${b}]" | wc -l)
  inpr=$(gh pr list --repo $repo --head "$b" --state open --json number | grep -c '"number"')
  if [ "$found" -eq 0 ] && [ "$inpr" -eq 0 ] && [ "$b" != "main" ] && [ "$b" != "release" ]; then
    echo "$b"
  fi
done
```

**Stale signals for orphan branches:**
- `git merge-base --is-ancestor $branch origin/main` returns true → squash-merged residue, safe to `git branch -D`
- `git diff --stat origin/main..$branch` is empty → no unique work, safe to delete
- Has closed PR with `mergedAt` set → merged residue, safe to delete

## Pattern: root checkout switching during cleanup

When the root checkout is on a non-default branch (e.g. an active PR branch), cleanup should NOT automatically switch it back to `main` unless:
1. The branch has a merged/closed PR AND
2. The working tree is clean AND
3. `git diff --stat origin/main..HEAD` is empty or the branch is an ancestor of `origin/main`

If the root is on an open PR branch (even if the working tree appears clean), preserve the checkout position. The user may be actively working on that PR.
