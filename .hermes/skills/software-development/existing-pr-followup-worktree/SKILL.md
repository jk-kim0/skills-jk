---
name: existing-pr-followup-worktree
description: When a user asks for follow-up changes to work already under review, use a fresh worktree on the existing PR branch and update the same PR instead of creating a new one.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, github, pr, worktree, review-feedback]
---

# Existing PR Follow-up via Fresh Worktree

Use this when the user asks for additional fixes or refinements to a PR that already exists.

Core rule:
- Fresh worktree: yes
- Existing PR branch: yes
- New branch: no, unless the user explicitly asks
- New PR: no, unless the user explicitly asks

Important distinction learned from review follow-up work:
- "Every new task should start from a fresh worktree + fresh branch" applies to new independent work.
- "Please update PR #N" or any review/follow-up on work already under review means: use a fresh worktree, but attach it to the existing PR branch and push back to that same branch.
- Do not satisfy the fresh-worktree requirement by creating a second branch/PR for the same review cycle.
- If the referenced PR is already merged and its head branch has been deleted, you cannot continue on that original PR branch. In that case, verify the merge commit is now on `origin/main` (or the PR base branch), create a fresh worktree from that merged tip, and open a new follow-up branch/PR for the requested additional work.

## When to use
- "PR 32에 수정사항 넣어줘"
- "리뷰 반영해줘"
- "기존 PR에 이어서 수정해줘"
- Any follow-up request where work is already under review

## Why
Reusing a stale local checkout or creating a second PR for review follow-up causes confusion:
- accidental divergence from the PR branch
- rebase conflicts from stacking unrelated follow-up work
- duplicate PRs for one logical review cycle
- stale CI status and hard-to-track branch history

## Workflow

### 1. Inspect the existing PR
Use GitHub CLI to confirm the PR number, head branch, and current status.

Example:
```bash
gh pr view <pr-number> --json number,headRefName,url,state,updatedAt
```

Record:
- PR number
- head branch name
- PR URL

### 2. Create a fresh worktree from the PR branch
From the repo root:

```bash
git fetch origin --prune
git worktree add .worktrees/<topic> origin/<pr-branch>
cd .worktrees/<topic>
git checkout -b <pr-branch>-local --track origin/<pr-branch> 2>/dev/null || git checkout <pr-branch>
```

Practical note:
- If the branch is already checked out in another worktree, `git checkout <pr-branch>` in the fresh worktree will fail. In that case, staying on the detached `origin/<pr-branch>` checkout is acceptable for a small follow-up.
- You can make the fix, commit on detached HEAD, and push with `git push origin HEAD:<pr-branch>`.
- This still satisfies the core requirement because the fresh worktree starts from the PR branch tip and updates the same remote PR branch.
- The important thing is: the new worktree must start from the PR's remote head, not from `main` and not from some old local branch.

### 3. Verify you are on the PR line before editing
```bash
git branch --show-current
git status -sb
git rev-parse HEAD origin/<pr-branch>
```

If local `HEAD` and `origin/<pr-branch>` differ before you start, stop and understand why.

### 4. Make the requested fix
Edit only the files needed for the follow-up request.

### 5. Validate
Run the relevant checks before pushing.

Typical examples:
```bash
npm run test:run
npm run typecheck
```

When the follow-up request is a broad cleanup of repeated link behavior on the existing PR branch (for example removing all `target="_blank"` / `rel="noreferrer"` patterns in that PR's surfaces), use an exhaustive search-and-verify loop instead of editing only the first example the user mentions:

1. search the fresh PR worktree for the exact pattern across `src/` (and tests if relevant)
2. patch every matching implementation site
3. re-run the same search and confirm zero matches remain in the intended scope
4. run targeted tests that cover the affected surfaces
5. then commit and push back to the same PR branch

This is especially useful when the user phrases the request as "all links" and gives only one example. The example is a clue, not the full edit set.

### 6. Commit and push back to the same PR branch
```bash
git add <files>
git commit -m "fix: address PR feedback"
git push origin HEAD:<pr-branch>
```

Do not create a new PR here.

Important user-expectation nuance learned from active-review follow-up:
- When a PR is already open and you make additional requested changes, commit and push those changes promptly instead of letting local edits accumulate.
- Treat each meaningful follow-up adjustment as reviewable progress on the existing PR branch unless the user explicitly asks you to batch changes before pushing.
- After each push, re-check PR status and CI so the user can review the updated PR without waiting for a later "finalize" step.
- If the user later asks to clean up the PR title/body, rewrite them to describe only the final end state of the PR. Do not narrate intermediate implementation history unless the user explicitly wants that context.
- If the user asks to squash the branch history for an open PR, use a fresh worktree from the PR branch tip, `git reset --soft <base-branch>`, recommit once with the final conventional-commit message, then `git push --force-with-lease origin HEAD:<pr-branch>` and re-check PR/CI status.
- For small PR follow-ups such as squash, title/body edits, route/path renames, or other narrow review-driven fixes, do not automatically run local build/test verification unless the user explicitly asks for it. Prefer the fast path: edit -> commit -> push -> confirm PR updated -> watch CI.
- At the start of a follow-up task, give a short time estimate. If the work exceeds that estimate, stop and immediately report current status and next step instead of staying silent.

### 6a. If the user asks to rebase the existing PR branch onto the latest main
Use the same fresh-worktree principle, but rebase the PR branch tip onto `origin/main` instead of creating a merge commit.

Recommended flow:
```bash
git fetch origin --prune
git worktree add .worktrees/<topic> origin/<pr-branch>
cd .worktrees/<topic>
git rebase origin/main
```

Important practical findings:
- `git worktree add <path> origin/<pr-branch>` often leaves you on a detached HEAD at the remote branch tip. That is acceptable for a rebase-only maintenance task.
- After a detached-HEAD rebase succeeds, push with:
  ```bash
  git push --force-with-lease origin HEAD:<pr-branch>
  ```
- If conflicts occur, resolve them by preserving the existing PR's intended behavior unless the user explicitly asked to adopt the newer `main` behavior in that area. Rebase conflicts often happen because `main` has evolved policy/tests while the PR still represents a deliberate exception or targeted rollout.
- In non-interactive agent environments, `git rebase --continue` may try to open Vim and hang. Prefer:
  ```bash
  GIT_EDITOR=true git rebase --continue
  ```
  after staging the resolved files.
- After force-pushing, verify both the remote branch tip and the PR head SHA. `gh pr view` can lag briefly right after the push, so confirm with both:
  ```bash
  git ls-remote origin refs/heads/<pr-branch>
  gh pr view <pr-number> --json headRefOid,updatedAt,url
  ```
  If they differ momentarily, wait a few seconds and re-check before concluding the push failed.

### 7. Re-check the PR and CI
```bash
gh pr view <pr-number> --json number,headRefName,updatedAt,commits
gh pr checks <pr-number>
```

Important practical note:
- `gh pr checks <pr-number>` returns a non-zero exit code not only for hard failures, but also while checks are still pending.
- Do not treat the non-zero exit by itself as proof that your branch update failed.
- Read the printed check table first, then classify each check as `pass`, `pending`, or `fail`.
- If needed, follow up with `gh pr view <pr-number> --json headRefOid,updatedAt,url` and/or rerun `gh pr checks <pr-number>` after a short wait.

Confirm:
- the PR still points to the intended branch
- the latest commit on the PR matches your pushed commit
- CI has started for the new head

## Anti-patterns to avoid

### Wrong: create a new PR for review follow-up
This splits one review cycle across multiple PRs.

### Wrong: keep working in an old unrelated worktree
This risks mixing stale local history into the PR.

### Wrong: start from a fresh branch off main for a PR fix
Unless explicitly requested, this creates unnecessary cherry-picking or duplicate PRs.

## Success criteria
- A fresh worktree was used
- The existing PR branch was updated directly
- No extra PR was created
- The new commit is visible on the original PR
- CI re-ran on the original PR
