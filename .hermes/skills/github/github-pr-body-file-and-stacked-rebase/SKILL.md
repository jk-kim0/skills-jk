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

After the rebase succeeds:

```bash
git log --oneline --graph -5
git push --force-with-lease origin HEAD:refs/heads/<branch-name>
```

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
- Do not assume a rebase conflict means manual merge is required; first check whether the conflicting commit is already merged.
- Do not skip commits unless you verified their effect already exists in `main`.
- Do not forget to force-push after a rewritten history rebase.
- Do not leave the PR body describing old stacked/base changes after rebasing onto `main`.

## Minimal checklist

- verify PR base/head
- rebase onto `origin/main`
- inspect conflicts
- skip only duplicate already-merged stacked commits
- force-push updated history
- refresh PR body with `--body-file`
