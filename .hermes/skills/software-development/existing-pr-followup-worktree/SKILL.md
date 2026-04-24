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
env -u GITHUB_TOKEN gh pr view <pr-number> --json number,headRefName,url,state,updatedAt
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
- If the branch is already checked out in another worktree, use a detached worktree from `origin/<pr-branch>` and then check out a local branch pointing to that remote.
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

### 6. Commit and push back to the same PR branch
```bash
git add <files>
git commit -m "fix: address PR feedback"
git push origin HEAD:<pr-branch>
```

Do not create a new PR here.

### 7. Re-check the PR and CI
```bash
env -u GITHUB_TOKEN gh pr view <pr-number> --json number,headRefName,updatedAt,commits
env -u GITHUB_TOKEN gh pr checks <pr-number>
```

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
