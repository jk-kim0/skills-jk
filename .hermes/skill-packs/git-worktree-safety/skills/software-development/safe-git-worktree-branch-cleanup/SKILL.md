---
name: safe-git-worktree-branch-cleanup
description: Safely update local main and clean stale local git branches/worktrees without deleting dirty or still-attached work; orchestrates the canonical stale-classification and workspace-cleanup skills instead of duplicating them.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, worktree, cleanup, branch, safety]
    related_skills: [git-worktree-safety-pack, branch-squash-validity-and-stale-cleanup, workspace-stale-git-cleanup, main-checkout-edit-taboo]
---

# Safe git worktree/branch cleanup

## Purpose

Use this skill for repo-local cleanup: update local `main`, remove stale local branches/worktrees, and preserve meaningful unpublished work.

This is now an orchestration checklist. Detailed logic is canonicalized in:

- `main-checkout-edit-taboo` for protected-main handling and dirty-main preservation/recovery.
- `branch-squash-validity-and-stale-cleanup` for branch-by-branch synthetic squash, rebase portability, dirty-worktree classification, detached worktree rules, and stale deletion sequence.
- `workspace-stale-git-cleanup` for cleanup across many repositories or named sibling/standalone workspace directories.

Do not duplicate the full algorithms here. Patch the canonical detailed skill when a new lesson belongs to one of those areas.

## References

- `references/repeated-repo-local-cleanup-root-merged-pr.md` — repeated repo-local cleanup pattern when the root checkout is a clean PR branch that was merged and pruned since the prior cleanup pass.

## Scope interpretation for this user

For wording like `workspace 정리`, `repo workspace 정리`, or `이 repo 정리`, prefer repo-local cleanup unless the user explicitly asks for all of `~/workspace`.

Repo-local cleanup means:

1. inspect current repo state and root checkout branch
2. update/fetch remote refs
3. classify local branches and linked worktrees
4. preserve meaningful unpublished changes in branches/worktrees, not stashes
5. delete only stale, merged, no-op, or redundant local residue
6. fast-forward local `main` to `origin/main` when safe
7. report whether root main is clean and updated

## Required discovery

Run from the repo root or intended worktree:

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
git fetch origin --prune
git worktree list --porcelain
git branch -vv --all
```

For GitHub-backed repos, cross-check PR state before deleting branch/worktree names that look stale:

```bash
env -u GITHUB_TOKEN gh pr status || true
env -u GITHUB_TOKEN gh pr list --state open --json number,title,headRefName,headRefOid,baseRefName,url
```

## Safety rules

- Never delete dirty worktrees without first classifying their net diff against latest `origin/main`.
- Never assume a local branch is stale only because its remote tracking branch is `[gone]`; the PR may be merged, closed, renamed, or represented by another open branch.
- Prefer preserving meaningful work in a named branch/worktree over stashing.
- When root checkout is on `main` and dirty, use `main-checkout-edit-taboo` before reset/cleanup.
- After deleting a worktree, re-run `git worktree list --porcelain`; registered worktrees and filesystem directories can diverge.
- If the current shell cwd was inside a removed worktree, move to a valid repo path before continuing.

## Canonical classification flow

Use `branch-squash-validity-and-stale-cleanup` for the actual branch decision. The high-level rubric is:

- Keep: open PR branch, unpublished meaningful diff, dirty worktree with meaningful current patch, detached worktree with unique commits.
- Preserve then cleanup: stale branch history whose current dirty patch is meaningful; promote the patch to a clear backup/follow-up branch first.
- Delete: merged clean branch, no-op alias of latest main, redundant local helper for an open PR head, detached helper exactly equal to a merged/open PR head, or disposable synthetic-rebase helper.

Recommended evidence for each candidate:

```bash
git rev-list --left-right --count origin/main...<branch>
git diff --stat --find-renames origin/main...<branch> --
git diff --name-status --find-renames origin/main...<branch> --
```

For dirty worktrees or branches with stale history, follow the synthetic squash method in `branch-squash-validity-and-stale-cleanup` rather than judging by raw commit history.

## Execution order

1. Handle protected root/main state using `main-checkout-edit-taboo`.
2. Fetch/prune and inspect branch/worktree/PR state.
3. Classify candidates with `branch-squash-validity-and-stale-cleanup`.
4. Preserve meaningful work in a branch/worktree when needed.
5. Delete stale worktrees first, then delete stale branches.
6. Fast-forward local `main` only when it is safe and not dirty.
7. Re-run discovery commands and verify root/main status.

## Deletion commands

Use explicit names and re-check immediately after each destructive action:

```bash
git worktree remove <path>
git worktree prune
git branch -D <branch>
git worktree list --porcelain
git branch -vv
```

If a branch is checked out by a worktree, remove or preserve the worktree before deleting the branch.

## Final report format

Report concisely:

- root checkout branch and cleanliness
- whether local `main` equals `origin/main`
- removed worktrees/branches
- preserved branches/worktrees and why
- candidates intentionally left alone and why
- any backup patch/branch paths created

## Maintenance note

If this skill starts accumulating detailed incident-specific sections again, move those details to the canonical classification skill (`branch-squash-validity-and-stale-cleanup`) or workspace-wide cleanup skill (`workspace-stale-git-cleanup`) and keep this file as the repo-local orchestration entrypoint.
