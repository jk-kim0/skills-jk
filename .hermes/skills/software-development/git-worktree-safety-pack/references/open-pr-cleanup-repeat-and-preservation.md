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
6. For PR-less dirty worktrees or dirty root payload:
   - inspect the diff instead of deleting or stashing;
   - if meaningful and no existing open preservation PR covers the same class of guidance/work, commit it, rebase onto the right base, push, and create a Korean PR body/title with no auto-closing keywords;
   - if an existing open preservation PR already covers the same scope, update that PR branch instead of opening a duplicate PR. Apply the root/worktree payload onto the open PR worktree, resolve conflicts by preserving both canonical latest-main guidance and the new payload, amend/force-push the existing PR commit, and refresh the PR body to match the expanded scope;
   - after creating or updating the PR, immediately re-run the dirty sweep because supporting files may still be untracked.
7. After every push, verify the actual remote head with `git ls-remote origin refs/heads/<branch>` before trusting GitHub PR metadata.
8. For a failed open PR check, inspect the failing job log, fix the smallest branch-local cause, amend/force-push with lease, then explicitly compare `gh pr view --json headRefOid,statusCheckRollup`, `gh pr checks`, and the newest `gh run list --branch <branch>` entries to confirm the checks are attached to the latest head SHA rather than a superseded run.
9. Re-run open PR checks and dirty sweep until all retained worktrees are clean and every remaining local branch maps to an open PR or `main`.
   - For each retained open PR branch, compare `git merge-base origin/main origin/<headRefName>` to `origin/main`; do not rely only on GitHub `mergeStateStatus: CLEAN` or `baseRefOid` when deciding the branch is current.
   - If the latest checks are still pending after a fix push, report them as pending/in-progress instead of calling the PR complete.
10. If the user wants a delayed follow-up or long checks are still running, use a short tracked timer/background process rather than passively waiting. When the timer fires, immediately fetch/prune, re-query open PR check rollups, and verify root plus retained worktree cleanliness. If every check is now successful and every retained worktree is clean, report that there is no further wait target instead of scheduling another timer.

## Practical pitfalls

- A preserved PR branch can have an older parent commit still in its local history after the parent PR has merged. Use `git rebase --onto origin/main <old-parent-head> HEAD` or recreate the branch from `origin/main` with only the intended commit(s).
- `GIT_EDITOR=true git rebase --continue` avoids editor hangs after conflict resolution in non-interactive tool sessions.
- If a force-push succeeds but `gh pr view` still shows the old `headRefOid` or old checks, compare `git ls-remote` first and wait/re-query before rewriting again.
- A preservation PR created through `workflow_dispatch` can become `DIRTY` immediately if another PR merges into `origin/main` during the create/cleanup window. Treat this as a normal cleanup race: fetch/prune, rebase the new preservation branch onto the new `origin/main`, resolve conflicts by preserving latest-main structure plus the still-valid preservation payload, force-push with lease, then verify remote head and PR metadata again before reporting.
- During such rebases, file-location conflicts are common when the preservation branch consolidates or renames a skill directory and latest `main` added a reference under the old path. Keep the latest added content, but stage it at the new umbrella/reference path and remove the old path so the consolidation stays self-consistent.
- Do not leave a newly created or newly updated preservation PR with pending local untracked helper/reference files; run one more dirty sweep and amend them into the same PR when they are part of the same scope.
- When a dirty retained open-PR worktree contains payload that appears out-of-scope, check for races before opening or keeping a new preservation PR. Re-fetch the source PR branch, compare the candidate preservation diff against the current source PR diff, and if the source PR already includes the same files/content, avoid leaving a duplicate subset PR. If a duplicate PR was already created, do not close it without explicit user approval; report the duplicate and keep the final cleanup state clean.
- A PR-less worktree can be clean in `git status` but still represent meaningful local work when it is `ahead 1, behind 1` or has a local commit not patch-equivalent to any open PR. Before deleting, inspect `git rev-list --left-right --count origin/main...HEAD`, `git show --stat HEAD`, targeted PR lookup, and patch-id or file overlap against open PR branches. If rebasing that payload onto latest `origin/main` triggers conflicts and resolving it would exceed cleanup scope, `git rebase --abort`, keep the original clean commit, push it as a preservation PR, and report the PR as needing conflict/rebase follow-up instead of deleting or leaving the worktree in a rebase state.
- A dirty PR-less worktree can be a duplicate holder for an already-open PR even when it is behind `origin/main`. Compare `git diff --name-only` (and, when practical, the patch/stat) against the matching open PR's `origin/main...origin/<head>` diff before preserving it. If the dirty payload is already represented by the open PR, reset/remove the duplicate worktree and delete its branch instead of creating another preservation PR.
- When cleanup finds same-scope dirty follow-up inside an open PR worktree, commit/amend it into that PR, force-push with lease, then immediately run another dirty sweep. A first amend can leave or reveal one more related file; amend that into the same PR before reporting the worktree clean.
- For credential/OAuth/runtime-secret follow-up files discovered during cleanup, scan added lines for secret-like values before committing. Public IDs and secret reference metadata may be acceptable, but never preserve raw secret values in the PR or final report.
- After cleaning the root checkout with targeted `git clean`, immediately run `git status --short --branch` again. A first clean can reveal another untracked authored file under a different umbrella skill/reference path; inspect it, add a SKILL.md pointer if needed, amend it into the existing preservation PR when scope matches, then clean root again.
- Treat runtime residue such as `.hermes/lsp/` separately from authored skill/reference files. Preserve authored files in a PR, then remove runtime residue from root.
