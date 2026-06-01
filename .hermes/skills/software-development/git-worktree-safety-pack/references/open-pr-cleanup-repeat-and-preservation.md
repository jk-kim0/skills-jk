# Open PR cleanup repeat and preservation loop

Use this reference when a repo-local workspace cleanup is combined with Open PR checking, CI follow-up, newly preserved PRs, or a delayed repeat pass.

## What this captures

A cleanup sweep can change the repository while it is running:

- open PRs may merge during the first pass;
- parent PR branches can be deleted while child PRs remain open and retarget to `main`;
- PR-less dirty worktrees can turn out to contain meaningful implementation or test work;
- root `main` may be dirty and behind latest `origin/main`;
- a newly preserved PR can leave additional local untracked files or generated residue in root;
- `gh pr view` can briefly show stale head/check metadata after a force-push.

Do not treat the first scan as the final state. Keep looping until root, retained worktrees, PR metadata, and remote heads agree.

## Recommended loop

1. Fetch/prune and fast-forward root `main` if root is on `main` and clean.
2. If root `main` is dirty and behind, preserve meaningful payload first using `references/dirty-root-behind-main-preservation.md`.
3. List open PRs and targeted PR lookup for every local branch.
4. Run a dirty sweep for every registered worktree.
5. For open PR branches:
   - if CI failed, inspect failed logs and fix the branch before reporting completion;
   - if the branch is dirty with related follow-up edits, stage/amend to that same PR and force-push with lease;
   - if a parent PR merged and GitHub retargeted the child to `main`, rebuild or rebase the child so its diff is only the child scope, update stale parent/base text in the PR body, then force-push.
6. For PR-less dirty worktrees:
   - inspect the diff instead of deleting or stashing;
   - if meaningful, commit it, rebase onto the right base, push, and create a Korean PR body/title with no auto-closing keywords;
   - after creating the PR, immediately re-run the dirty sweep because supporting files may still be untracked.
7. After every push, verify the actual remote head with `git ls-remote origin refs/heads/<branch>` before trusting GitHub PR metadata.
8. For a failed open PR check, inspect the failing job log, fix the smallest branch-local cause, amend/force-push with lease, then explicitly compare `gh pr view --json headRefOid,statusCheckRollup`, `gh pr checks`, and the newest `gh run list --branch <branch>` entries to confirm the checks are attached to the latest head SHA rather than a superseded run.
9. Re-run open PR checks and dirty sweep until all retained worktrees are clean and every remaining local branch maps to an open PR or `main`. If the latest checks are still pending after a fix push, report them as pending/in-progress instead of calling the PR complete.

## Practical pitfalls

- A preserved PR branch can have an older parent commit still in its local history after the parent PR has merged. Use `git rebase --onto origin/main <old-parent-head> HEAD` or recreate the branch from `origin/main` with only the intended commit(s).
- `GIT_EDITOR=true git rebase --continue` avoids editor hangs after conflict resolution in non-interactive tool sessions.
- If a force-push succeeds but `gh pr view` still shows the old `headRefOid` or old checks, compare `git ls-remote` first and wait/re-query before rewriting again.
- Do not leave a newly created preservation PR with pending local untracked helper files; run one more dirty sweep and amend them into the PR when they are part of the same scope.
- Treat runtime residue such as `.hermes/lsp/` separately from authored skill/reference files. Preserve authored files in a PR, then remove runtime residue from root.
