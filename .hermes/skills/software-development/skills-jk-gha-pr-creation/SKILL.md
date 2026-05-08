---
name: skills-jk-gha-pr-creation
description: Create pull requests in the skills-jk repository via the repo's GitHub Actions workflow `.github/workflows/create-pr.yml` instead of direct `gh pr create`, to avoid local shell quoting issues and follow repo convention.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [github, pull-request, github-actions, workflow-dispatch, skills-jk]
---

# skills-jk GHA PR Creation

Use this skill when creating a PR in the `skills-jk` repository.

## Why this exists

`skills-jk` has a repository-standard PR creation workflow at `.github/workflows/create-pr.yml`.
It accepts `branch`, `title`, and `body` via `workflow_dispatch`, then creates the PR in GitHub Actions.
This is safer than local `gh pr create --body "..."` when the body contains backticks, paths, or multiline markdown that can be mangled by shell quoting.

## When to use

Trigger this skill when:
- working inside the `skills-jk` repository
- a new PR needs to be opened
- the branch is already committed and pushed
- the PR body is multiline markdown

## Procedure

1. Confirm you are in `skills-jk` and that the work branch is pushed.
   - Check current branch with `git branch --show-current`
   - Check remote tracking with `git status -sb`

2. Confirm whether a PR already exists for the branch.
   - Use `gh pr status`
   - If a PR already exists, edit that PR instead of creating a new one

3. Prepare the PR body in a file first.
   - Write the full markdown body to a temporary file
   - Avoid inline shell interpolation of multiline markdown

4. Trigger the repository workflow instead of calling `gh pr create` directly.
   - Use `gh workflow run .github/workflows/create-pr.yml`
   - Pass:
     - `-f branch=<branch>`
     - `-f title=<title>`
     - `--raw-field body="$(cat <body-file>)"`

5. Wait for the workflow run to appear and finish.
   - Use `gh run list --workflow create-pr.yml --limit 5`
   - In this repo, the dispatched `create-pr.yml` run may appear with `headBranch` shown as `main` in `gh run list`, even when it creates a PR for another branch. Do not try to identify the run by filtering on the feature branch name.
   - If you need to inspect the run, take the newest `create-pr.yml` run and use `gh run view <run-id>` or `gh run watch <run-id>`.

6. Verify the PR was created.
   - Prefer `gh pr status` to confirm the resulting PR.
   - If you need a branch-specific lookup, use `gh pr list --head <branch>` or `gh pr view <branch>`.
   - Do not use `gh pr view --head <branch>`; that flag is not supported by `gh pr view` and fails with `unknown flag: --head`.
   - Do not rely on `gh run list --branch <branch>` to prove the PR-creation workflow ran; that branch filter may show nothing for this workflow even when PR creation succeeded.
   - Report the PR number and URL

## If a PR already exists

Do not dispatch the create workflow again unless intentionally creating a replacement PR.
Instead:
- use `gh pr edit <number> --title ...`
- or `gh pr edit <number> --body-file <file>`

## Pitfalls

- Follow the active repository/global GitHub CLI safety policy when invoking `gh`. In this environment that means using `env -u GITHUB_TOKEN gh ...` rather than raw `gh ...`.
- Do not pass complex markdown directly to `gh pr create --body` in this repo unless there is a strong reason
- `create-pr.yml` targets `main` as the base branch
- The workflow appends a GitHub Actions bot footer to the body
- If the branch has an existing open PR, the workflow may fail or create duplicate intent; check first
- After dispatching the PR-creation workflow, verify completion with `gh run watch` and then confirm the resulting PR with `gh pr view` or `gh pr status`
- `gh pr checks` may legitimately report no checks for the new PR branch; if so, also inspect `gh run list --branch <branch>` before concluding that no CI ran
- When the local workspace contains mixed changes, inspect `git status --short`, `git diff --stat`, and representative diffs before staging. In `skills-jk`, it is common to have meaningful tracked changes under `.hermes/` mixed with local-only artifacts such as `.claude/worktrees/` or scratch files like `test.txt`; exclude those temporary artifacts from the PR unless the user explicitly asks to include them

## Local workspace sweep workflow

When the user asks to create a PR from the current local workspace state rather than from a single known change:

1. Review all current changes first:
   - `git status --short`
   - `git diff --stat`
   - `git diff --name-status`
   - `git ls-files --others --exclude-standard`
2. Read representative diffs or files to classify them:
   - meaningful tracked repo changes
   - new skill/reference content that should be committed
   - local runtime/worktree/scratch artifacts that should stay untracked
3. Refresh repository references before committing:
   - `git fetch origin --prune`
   - inspect whether the current branch tracks a deleted remote branch (`[gone]` in `git branch -vv`)
   - inspect whether local `main` is behind `origin/main`
4. If local `main` is behind and is not currently checked out, fast-forward it safely with:
   - `git branch -f main origin/main`
   - This updates local `main` without disturbing the dirty current branch.
5. If the current branch corresponds to an already merged/closed PR, do **not** keep committing on that branch even if it still has useful local changes.
   - Fast detection: run `env -u GITHUB_TOKEN gh pr status` first. In `skills-jk`, this often surfaces the problem immediately as `Current branch  #<N> ... Merged` even when the remote branch has already been deleted.
   - Confirm with `env -u GITHUB_TOKEN gh pr list --head <branch> --state all --json number,state,mergedAt,url,title` when needed.
   - Additional signals:
     - `git status -sb` shows the branch is diverged (`[ahead N, behind M]`)
     - the remote tracking branch may already be deleted or stale
   - Refresh repository refs and fast-forward local `main` before branching:
     - `git fetch origin --prune`
     - `git branch -f main origin/main`
   - Preferred safe pattern in this repo when the user wants the current dirty workspace turned into a new PR without disturbing the root checkout:
     - create a fresh worktree and fresh branch from latest `origin/main`
       - `git worktree add -b <new-branch> <new-worktree> origin/main`
     - enumerate the current meaningful local changes in the dirty root checkout
       - `git diff --name-only`
       - `git ls-files --others --exclude-standard`
     - copy only those changed/untracked files from the dirty root checkout into the fresh worktree
     - verify the fresh worktree now shows exactly that change set against `origin/main`
   - This avoids using `stash`, keeps the user's existing dirty root workspace intact, and still yields a clean latest-main PR branch.
   - Important repeat-request lesson: if the user asks for the same "update main + make a PR from current local changes" flow again later in the same dirty root checkout, do **not** assume the last follow-up branch/PR is still open or still matches the current root state.
     - Re-check both the current root branch and any most recently created follow-up branch/PR.
     - A previous PR you created from a fresh worktree may already be merged, while the root checkout still sits on an older merged branch with additional new local edits accumulated afterward.
     - In that case, repeat the same safe transplant flow again from the current root diff onto a brand-new latest-`origin/main` branch, rather than trying to reuse the earlier follow-up branch name or infer state from the last PR you created.
   - Safer fallback when a clean file-copy transplant is impractical:
     - `git stash push -u -m '<note>'`
     - refresh repository refs and update local `main` to latest `origin/main`
     - create a fresh branch from `origin/main`
     - if there is an unmerged local commit you still need, cherry-pick it onto the new branch
     - if the cherry-pick becomes empty because latest `main` already contains that change, use `git cherry-pick --skip`
     - `git stash pop`
   - This preserves the still-local work while avoiding accidental reuse of a stale merged-PR branch.
   - If there is an unmerged local commit you still need, cherry-pick it onto the new branch.
   - If the cherry-pick becomes empty because latest `main` already contains that change, use `git cherry-pick --skip` and continue.
   - Only then continue with staging/committing. This preserves the current file state while ensuring the new PR is based on clean latest main rather than a previously merged PR branch.
6. Commit only the meaningful files on the current branch.
7. Before push/PR creation, verify the final file/tree state still differs from latest `origin/main`.
   - Do not rely only on commit history such as `git log origin/main..HEAD`; local commits can remain on a stale merged branch even when the final file tree is already identical to latest `origin/main`.
   - Check both:
     - tracked diff: `git diff --name-status origin/main -- .`
     - tree identity when helpful: `git rev-parse HEAD^{tree}` vs `git rev-parse origin/main^{tree}`
   - If the tracked diff is empty and the trees match, there is no real PR payload left. Do not manufacture a follow-up PR just because old local commits still exist.
   - In that case, report that `main` was updated, no tracked changes remain, and only any local scratch/untracked files are left for the user to keep or delete.
8. Before push/PR creation, rebase the current branch onto latest `origin/main`.
   - This is especially important when the branch was created from an older local `main` or its remote tracking branch is gone.
   - If rebase conflicts come from settings already present on latest `main`, keep the newer `main` values and continue so the PR diff stays focused on the still-local changes.
9. After any manual conflict resolution, explicitly scan the touched files for leftover merge markers before committing or pushing.
   - In `skills-jk`, append-only markdown files such as `.hermes/memories/*.md` and skill `SKILL.md` files often conflict when both latest `main` and the local work added new bullets near the end.
   - Do not blindly choose one side; read the conflict block and keep both sides' new entries unless they are true duplicates.
   - Preserve existing separators like `§` in memory files.
   - At minimum run a targeted search like `rg -n '^(<<<<<<<|=======|>>>>>>>)' <files...>`.
   - Do not rely only on `git status`; a file can be marked resolved while still containing conflict text.
   - For config files such as `.yaml`, also run a lightweight parse check (for example `python -c 'import yaml, pathlib; yaml.safe_load(pathlib.Path(...).read_text())'`).
   - When resolving against latest `main`, prefer the actual `origin/main` file content as the source of truth instead of guessing which side of the conflict to keep.
9. If `git rebase --continue` is blocked because you restored broader local workspace changes while the rebased commit itself only touches a smaller subset of files, temporarily move the unrelated non-index changes back out of the way.
   - Practical pattern:
     - stage the actual conflict-resolved file(s) that belong to the rebased commit
     - `git stash push -u --keep-index -m '<temp-note>'`
     - `GIT_EDITOR=true git rebase --continue`
     - re-apply the earlier broader workspace stash after the rebase finishes
   - This is especially useful in `skills-jk` when a one-file commit is being rebased but the working tree also contains many restored local skill/memory edits from the user's current workspace.
   - Without this step, `git rebase --continue` can fail or become confusing because the rebase commit is ready, but unrelated restored changes are still sitting unstaged in the working tree.
10. Push the branch, then create or update the PR.
10. Leave local-only artifacts untracked unless the user explicitly wants them in the PR.
11. In the PR body, briefly note what was intentionally excluded if that helps reviewers understand the scope

## Evidence from use

Observed in `skills-jk`:
- direct local `gh pr create --body` caused shell quoting issues with markdown/backticks
- `.github/workflows/create-pr.yml` already exists and is the repo-preferred PR creation path

## Completion checklist

- branch pushed
- existing PR checked
- workflow dispatched
- workflow completed successfully
- resulting PR number and URL verified
