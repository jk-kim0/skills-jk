---
name: github-pr-body-file-and-stacked-rebase
description: Safely edit PR bodies with gh using body files, and rebase stacked PRs onto the latest main after upstream/base changes land.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [GitHub, Pull-Requests, Rebase, Stacked-PRs, gh]
    related_skills: [github-pr-workflow]
---

# GitHub PR body-file editing and stacked rebase

Use this when:
- a PR body contains markdown with backticks or shell-sensitive characters
- a stacked PR was opened on top of another branch, then needs to move onto the latest `main`
- rebasing a stacked branch hits conflicts because earlier stacked commits are already merged into `main`

## 1. Prefer `--body-file` for markdown PR bodies

Do not pass rich markdown with backticks directly in a shell string unless it is truly trivial.
Shell interpolation can corrupt the PR body.

Safer pattern:

```bash
cat > /tmp/pr-body.md <<'EOF'
## Summary
- describe the current diff only
- include code spans like `src/file.tsx` safely

## Verification
- `npm run test:ci`
- `npm run build`
EOF

gh pr edit 123 --title "fix: update navigation links" --body-file /tmp/pr-body.md
```

Also use `--body-file` for `gh pr create` when the body includes:
- backticks
- code spans
- fenced code blocks
- parentheses-heavy URLs
- multiline notes copied from markdown

## 2. Rebase a stacked PR onto latest `main`

First inspect whether the PR is still stacked or GitHub already retargeted it to `main`.

```bash
git fetch origin --prune
gh pr view <PR_NUMBER> --json baseRefName,headRefName,title,url
git log --oneline --graph origin/main..HEAD
```

If the branch is clean:

```bash
git rebase origin/main
```

## 2b. If the working tree is dirty, stash first and reapply after rebase

A common practical case:
- the branch has uncommitted tracked changes
- there may also be untracked files
- you need the current local work moved onto the latest `main` without discarding it

Do not try to `checkout main` or start a rebase with a dirty tree.
Instead:

```bash
git status --short --branch
git stash push -u -m '<branch> pre-rebase'
git rebase origin/main
```

Then reapply the local work:

```bash
git stash pop
```

Important observations from real use:
- `git rebase origin/main` may report `skipped previously applied commit ...` when the branch commit already exists in `main`; this is often correct and not itself an error
- after such a skip, `HEAD` can end up exactly at `origin/main`, and the real remaining work is only in the reapplied stash
- if `git stash pop` hits conflicts, Git keeps the stash entry instead of dropping it; keep it until resolution is verified

Useful checks before deciding whether a skipped commit is safe:

```bash
git rev-parse --short HEAD
git rev-parse --short origin/main
git merge-base HEAD origin/main | cut -c1-7
git show --stat --name-status <skipped-commit>
git diff --name-only HEAD...origin/main
```

Goal:
- branch history rebased to latest `main`
- local uncommitted work restored on top of that rebased state

## 2a. If the old stacked base branch was merged and deleted

A common real-world case:
- PR A was based on feature branch `fix/some-base`
- PR A's branch was rebased onto the tip of `fix/some-base`
- later, `fix/some-base` was merged into `main`
- GitHub deleted `fix/some-base`

In that case:
- do **not** try to retarget the PR base to the deleted branch; GitHub API calls like `gh pr edit --base fix/some-base` will fail because the branch no longer exists
- first confirm the upstream PR was actually merged and note its merge commit / merged time
- then move your branch onto the latest `origin/main`, not onto the deleted base branch

Useful checks:

```bash
gh pr view <UPSTREAM_PR_NUMBER> --json state,baseRefName,headRefName,mergeCommit,mergedAt,url
git fetch origin --prune
git rev-parse --short origin/main
git log --oneline --graph origin/main..HEAD
```

If your branch currently contains commits from the deleted stacked base, rebase only your remaining PR-specific commits onto the latest main. One reliable pattern is:

```bash
# old-base-tip is the commit your branch had been stacked on
# rewrite only the commits after old-base-tip onto latest origin/main
git rebase --onto origin/main <old-base-tip> <your-branch>
```

After that, verify the diff against `origin/main`. The goal is for the PR to show only your task-specific changes, not the already-merged upstream stack.

## 3. If rebase conflicts come from already-merged stacked commits

Typical sign:
- the conflict happens while replaying earlier commits from the old stack
- the conflicting changes are already present on `origin/main`
- your actual PR-specific commit is later in the sequence

In that case, skip the duplicate stacked commits and keep rebasing until your PR-specific commit is replayed.

```bash
git rebase --skip
# repeat if the next replayed commit is also already in main
```

This is appropriate only when inspection shows the skipped commit's intent is already in `main`.
Do not skip blindly.

Useful checks:

```bash
git status --short
rg '<<<<<<<|=======|>>>>>>>' src
read the conflicted files
```

## 4. Finish and force-push

After the rebase succeeds, verify both ancestry and intended squash shape before pushing. Even if the PR already had one commit, a conflict-resolving rebase can briefly make the local branch look `ahead N, behind M` relative to its old remote; compare against `origin/main`, not the old PR remote, to confirm the final PR shape.

```bash
git status --short --branch
git rev-parse --short HEAD
git rev-parse --short origin/main
git merge-base HEAD origin/main | cut -c1-7
git rev-list --oneline origin/main..HEAD
git diff --stat origin/main...HEAD
```

Expected result for a squashed single-commit PR:
- `merge-base` equals the current `origin/main` tip
- `git rev-list origin/main..HEAD` contains exactly the intended commit(s), usually one
- `git diff --stat origin/main...HEAD` contains only the PR-specific file set

Then force-push with an explicit destination ref and verify the remote ref matches local HEAD:

```bash
git push --force-with-lease origin HEAD:refs/heads/<branch-name>
git rev-parse HEAD
git ls-remote origin refs/heads/<branch-name>
```

After push, check GitHub against the new head SHA, not stale runs from the old commit:

```bash
gh pr view <PR_NUMBER> --json headRefOid,mergeable,mergeStateStatus,statusCheckRollup,commits,url
gh run list --branch <branch-name> --limit 5 --json headSha,status,conclusion,workflowName,url
```

Interpretation:
- `mergeable=MERGEABLE` plus `mergeStateStatus=BLOCKED` usually means conflicts are resolved and required checks are pending.
- Treat checks as attached only when their `headSha` equals the just-pushed HEAD.


## 4a. Rebuilding a stacked PR chain as single-commit branches

Use this when the user wants several already-open PRs rewritten as squashed stacked PRs on top of the latest `main`.

Safe pattern:
1. Keep one dedicated worktree per PR branch.
2. Rewrite the parent PR first from `origin/main`.
3. For each child PR, reset the child worktree hard to its intended parent branch tip.
4. Restore only the child PR's intended files from the old remote child branch.
5. Create exactly one commit on that child branch.
6. Force-push each branch, then update each PR base branch explicitly.
7. If a child `gh pr edit --base <parent-branch>` fails with `branch not found`, verify the parent remote ref still exists with `git ls-remote origin refs/heads/<parent-branch>` and re-push the parent branch before retrying the base edit.

Practical command pattern:

```bash
# parent
 git -C .worktrees/<parent> reset --hard origin/main
 # restore only intended parent files from origin/<parent-branch>
 git -C .worktrees/<parent> checkout origin/<parent-branch> -- <files...>
 git -C .worktrees/<parent> add -A
 git -C .worktrees/<parent> commit -m "..."
 git -C .worktrees/<parent> push --force-with-lease origin HEAD:refs/heads/<parent-branch>

# child
 git -C .worktrees/<child> reset --hard <parent-branch>
 # remove files that should have moved/renamed if needed
 # restore only intended child files from origin/<child-branch>
 git -C .worktrees/<child> checkout origin/<child-branch> -- <files...>
 git -C .worktrees/<child> add -A
 git -C .worktrees/<child> commit -m "..."
 git -C .worktrees/<child> push --force-with-lease origin HEAD:refs/heads/<child-branch>
 gh pr edit <child-pr-number> --base <parent-branch>
```

Why this is safer than replaying all historical commits:
- old branch history may contain now-unwanted fixes or temporary compatibility edits
- branch-to-branch rebase can keep dragging earlier stacked commits forward
- rebuilding from the intended base plus the exact intended file set produces the cleanest single-commit PR diff

If `git rebase --continue` opens an editor in a non-interactive environment and hangs, continue without launching the editor:

```bash
GIT_EDITOR=true git rebase --continue
```

Use this only after verifying the staged resolution is correct and you want to keep the existing commit message.

Use the fully-qualified destination ref when needed. This is especially useful if `HEAD` is detached during or right after rebase-related recovery.

## 5. Update the PR body after rebase

After rebasing onto `main`, the PR may now contain fewer commits or only the final task-specific diff.
Rewrite the PR body so it describes only what remains in the PR.

Recommended checks:

```bash
git diff --stat origin/main...HEAD
gh pr view <PR_NUMBER> --json title,body,baseRefName,headRefName,url
```

Then replace the body with a body file describing:
- the current summary
- exact files changed
- current verification
- a note that earlier stacked/base work is already in `main`, if relevant

## Pitfalls

- Do not use inline shell strings for complex markdown PR bodies.
- When rewriting stacked PRs into squashed single-commit branches, do not blindly preserve child assertions that only pass because of a transient parent-branch implementation detail; verify the child still matches the latest parent/main contract after the rewrite.
- Do not assume a rebase conflict means manual merge is required; first check whether the conflicting commit is already merged.
- Do not skip commits unless you verified their effect already exists in `main`.
- Do not forget to force-push after a rewritten history rebase.
- Do not leave the PR body describing old stacked/base changes after rebasing onto `main`.
- If you are rebasing a different open PR branch while your current checkout has unrelated local changes, do not perform the rebase in the dirty working tree. Create a temporary isolated worktree from the remote PR branch, rebase there, and force-push from that isolated worktree.
- When `stash pop` conflicts on markdown memory/config files, merge by preserving both durable additions unless one clearly supersedes the other.
- For `rename/delete` conflicts after upstream skill restructuring, decide explicitly whether your local intent was “delete this content” or “edit the moved file”; do not accept Git's default blindly.
- If `stash pop` reported conflicts, do not drop the stash until `git status` shows no unmerged paths and the resulting diff matches your intended local work.
- When the top of a stack is a CI/path-scope PR and lower stacked PRs moved or renamed tests/files, rebasing the CI PR onto the new stack tip is not enough by itself. Reconcile both sources of truth for scope classification in the same update:
  - the GitHub workflow `paths-filter` globs
  - the repo-local matcher/assertion logic (for example `scripts/ci/test-groups.mjs` plus `assert-test-groups.mjs`)
  Then run the local assertion before force-push. Otherwise the PR can look rebased correctly while CI scope detection silently drifts or fails with unassigned/overlapping moved tests.

## Additional practical pattern: rebasing another open PR branch safely

Use this when:
- PR A is open on branch `feature/a`
- your current checkout is on branch `feature/b` with unrelated local or untracked changes
- the user asks to rebase PR A onto latest `main`

Safe pattern:

```bash
git fetch origin --prune

# follow repo-root-worktree-path-policy
git branch -f main origin/main
git worktree add .worktrees/feature-a-rebase -b feature-a-rebase origin/feature/a
cd .worktrees/feature-a-rebase
git rebase origin/main
```

Why this is safer:
- avoids polluting the current branch/worktree
- avoids accidental staging of unrelated local changes
- lets you resolve conflicts against the target PR branch only

### Typical conflict pattern in repo-local state files

When rebasing a repo that tracks durable memory/config/skill state, conflicts often appear in files like:
- `.hermes/memories/MEMORY.md`
- `.hermes/memories/USER.md`
- `.hermes/skills/.bundled_manifest`

Useful rule of thumb:
- for memory files, if both sides add distinct durable facts, keep both entries and remove only conflict markers
- for generated manifest-like files, preserve valid entries from both sides and remove only the markers/duplicate empty side
- re-check with a marker search such as `rg '^(<<<<<<<|=======|>>>>>>>)'` before continuing

## Minimal checklist

- verify PR base/head
- if working tree is dirty, `git stash push -u` first
- rebase onto `origin/main`
- inspect conflicts
- skip only duplicate already-merged stacked commits
- `git stash pop` and resolve any post-rebase conflicts
- verify `HEAD`, `origin/main`, and `merge-base` alignment
- force-push updated history
- refresh PR body with `--body-file`
