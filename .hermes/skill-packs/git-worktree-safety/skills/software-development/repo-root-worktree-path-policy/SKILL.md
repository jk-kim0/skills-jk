---
name: repo-root-worktree-path-policy
description: Common worktree path policy — create linked git worktrees under the repository's own `.worktrees/<flat-name>` directory, keep names flat, and verify the checkout before editing.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, worktree, path, repository, safety, workflow]
---

# Repo-root worktree path policy

Use this as the default policy whenever a workflow says to create a fresh worktree, unless the user explicitly overrides it.

## Relationship to main-checkout safety

This skill owns the path and verification policy for linked worktrees. The canonical rule that forbids editing a checkout on `main` lives in `main-checkout-edit-taboo`; load that skill for pre-edit gates, dirty-main recovery, or duplicate/upstreamed main cleanup. Do not duplicate that procedure here.

## Core rule

Create linked worktrees under the repository's own `.worktrees/` directory.

Preferred pattern:

```bash
git worktree add .worktrees/<flat-name> -b <branch-name> origin/main
```

Examples:

```bash
git worktree add .worktrees/fix-seo-baseline -b fix/seo-baseline origin/main
git worktree add .worktrees/pr-321-followup origin/feature/pr-321
```

## Important branch-selection distinction

Choose the worktree base from the real review intent, not only from whether a PR number was mentioned.

- New independent work with no unmerged dependency -> create the worktree from `origin/main` on a fresh branch.
- Follow-up fixes to an existing open PR -> create a fresh worktree on that existing PR branch and update the same PR.
  - If that branch is already checked out by another worktree, create the fresh worktree from a fetched PR ref in detached HEAD instead of creating a new branch/PR: `git fetch origin pull/<pr>/head:refs/remotes/origin/pr/<pr> --force && git worktree add .worktrees/<flat-name> origin/pr/<pr>`.
  - After committing/rebasing in the detached worktree, push back to the existing PR branch explicitly with a lease: `git ls-remote origin refs/heads/<branch>` then `git push --force-with-lease=refs/heads/<branch>:<old-sha> origin HEAD:refs/heads/<branch>`.
- New work that should use an existing open PR as the baseline, but should land in its own later PR -> create a fresh worktree from the open PR head branch, create a new child branch there, and open a stacked PR whose base is the parent PR branch.

Representative stacked-PR pattern:

```bash
git fetch origin --prune
git worktree add .worktrees/contact-us-form-offset -b fix/contact-us-form-panel-offset origin/refactor/issue-459-company-page-contract
# ...commit...
gh pr create --base refactor/issue-459-company-page-contract --head fix/contact-us-form-panel-offset
```

Why this matters:
- it keeps the parent PR review scope unchanged
- it lets the child PR be reviewed or merged after the parent lands
- it avoids silently pushing new scoped work into the parent PR when the user only meant “use that implementation as the baseline”

## Why this policy exists

- keeps worktrees colocated with the owning repository
- avoids scattering related checkouts across `~/workspace`, `/tmp`, or ad hoc sibling directories
- makes cleanup and inspection easier via one predictable namespace
- works well with `git worktree list` and repo-local cleanup skills

## Flat-name rule

The worktree directory name must be flat even if the branch name contains slashes.

Good:
- branch `fix/issue-78`
- path `.worktrees/issue-78`

Good:
- branch `docs/rewrite-pr-body`
- path `.worktrees/rewrite-pr-body`

Risky:
- path `.worktrees/fix/issue-78`
- path derived mechanically from the branch name with slashes

Why:
- nested worktree paths are easy to misread and mistarget
- later `git -C`, file-tool, and cleanup commands become more error-prone

## Verification after creation

Do not trust the `git worktree add` success message by itself.
Always verify:

```bash
git worktree list --porcelain
test -f .worktrees/<flat-name>/README.md || test -f .worktrees/<flat-name>/package.json || true
git -C .worktrees/<flat-name> branch --show-current
git -C .worktrees/<flat-name> rev-parse --show-toplevel
git -C .worktrees/<flat-name> status --short --branch
find .worktrees/<flat-name> -maxdepth 2 | sed -n '1,30p'
```

Expected signs:
- the worktree appears in `git worktree list --porcelain`
- the branch/base matches what you intended
- the directory contains a normal repo checkout shape, not only a tiny partial directory created by an accidental write
- `rev-parse --show-toplevel` resolves successfully
- `git status --short --branch` works from the worktree path

If a newly created follow-up worktree is incomplete, missing, or disappears before edits are applied, preserve any drafted file to `/tmp`, remove/prune the broken worktree, fetch the intended branch/PR ref again, and recreate it before continuing. For existing open-PR follow-up work, see `existing-pr-followup-worktree/references/followup-worktree-integrity.md`.

## Path-handling rule for later commands

Use absolute paths for follow-up tool calls when the calling environment may not preserve cwd reliably.

Example:

```bash
WT="$(pwd)/.worktrees/issue-78"
git -C "$WT" status --short
```

Interpretation:
- create the worktree under repo-root `.worktrees/`
- but when issuing later shell/tool commands, prefer an absolute path to that repo-root worktree

## Recovery if the worktree is broken

If the directory exists but is incomplete, missing, or not registered correctly:

```bash
rm -rf .worktrees/<flat-name>
git worktree prune
git worktree add .worktrees/<flat-name> -b <branch-name> origin/main
```

## Scope

This is a generic repository workflow policy.
It is not specific to `corp-web-japan`, `skills-jk`, or any other one repo.

## Anti-patterns

Avoid these as defaults unless the user explicitly asks:
- `~/workspace/<repo>-<topic>` as the normal worktree location
- `/tmp/<topic>` as the normal worktree location
- nested paths derived directly from branch names such as `.worktrees/feature/foo/bar`

## Done criteria

- worktree created under repo-root `.worktrees/`
- directory name kept flat
- checkout verified before editing
- follow-up commands use the correct worktree path consistently
