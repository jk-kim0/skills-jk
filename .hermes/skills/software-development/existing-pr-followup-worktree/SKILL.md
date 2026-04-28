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
- Exception: if the requested "follow-up" actually depends on code or route structure that already landed on latest `origin/main` but is missing from the old PR branch, do not force the change onto the stale PR branch. Treat it as a new independent task: branch from latest `origin/main`, open a separate PR, and mention explicitly why the old PR branch was no longer the right base.
- Practical heuristic for this exception: if you discover during inspection that the target route family, helper layer, sitemap shape, or canonical-path policy already changed on `origin/main` after the old PR branched, switching to a new main-based branch is usually safer than backporting those structural assumptions into the old PR.

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
- In this detached state, some `gh pr ...` commands that rely on the current branch can fail with errors like `could not determine current branch`. Prefer explicit branch/PR arguments, e.g. `gh pr view <pr-branch> --json ...` or `gh pr view <pr-number> --json ...` instead of assuming branch autodetection will work.
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

Special case: the user asks you to remove forbidden-scope changes from an already-open PR branch
- Example: "PR #44에서 CMS 데이터 파일 건드린 건 모두 취소해줘"
- Use a fresh worktree on the existing PR branch, not a new branch/PR.
- Discover the exact file set from the PR diff against the base branch, then restore only that forbidden scope from the base branch.
- For a main-based PR, the safest pattern is:
  ```bash
  git fetch origin --prune
  gh pr view <pr-number> --json headRefName
  git worktree add .worktrees/<topic> origin/<pr-branch>
  cd .worktrees/<topic>

  git diff --name-only origin/main...HEAD -- 'forbidden/scope/**' > /tmp/forbidden-files.txt
  while IFS= read -r f; do
    git checkout origin/main -- "$f"
  done < /tmp/forbidden-files.txt
  ```
- Then verify twice:
  1. `git diff --name-only origin/main...HEAD -- 'forbidden/scope/**'` should become empty after the revert commit.
  2. `git diff --stat -- 'forbidden/scope/**'` should reflect only your local revert before commit, then become clean after commit.
- Why both checks matter:
  - `origin/main...HEAD` answers "does the PR still contain this forbidden scope?"
  - plain `git diff -- ...` answers "what is currently uncommitted in the worktree?"
- On macOS/BSD, do not rely on GNU-only `xargs -a`; prefer the portable `while IFS= read -r f; do ...; done` loop above.
- Commit and push back to the same PR branch:
  ```bash
  git add forbidden/scope
  git commit -m "fix: revert forbidden-scope changes"
  git push origin HEAD:<pr-branch>
  ```
- This pattern is especially important when the forbidden scope is CMS-managed data or routes that the user explicitly said must not be touched. Do not try to "partially keep" those edits unless the user explicitly names the exact file/subtree they still want changed.

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
- After a detached-HEAD rebase succeeds, do not force-push immediately. First verify that the expected post-PR follow-up commit(s) still survived the rebase and that their key scoped changes are still present. A fast check is:
  ```bash
  git log --oneline --decorate -n 5
  git search-files-or-grep-for-the-target-pattern
  ```
  For example, if a later follow-up changed a path prefix or removed a repeated pattern, re-check that exact pattern before pushing.
- Then push with:
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
