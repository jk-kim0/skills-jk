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

## Absolute taboo: never edit main checkout

A workspace checked out to `main` is a protected control workspace. Do not modify files there. Treat this as a hard safety rule, not a preference.

Before any repository edit, run:

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
```

If the active branch is `main`, stop before editing and create/select a linked worktree under the repository's own `.worktrees/` directory. Only edit inside that non-main worktree unless the user explicitly authorizes main-workspace edits for that exact task.

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
git -C .worktrees/<flat-name> branch --show-current
git -C .worktrees/<flat-name> rev-parse --show-toplevel
find .worktrees/<flat-name> -maxdepth 2 | sed -n '1,30p'
```

Expected signs:
- the worktree appears in `git worktree list --porcelain`
- the branch/base matches what you intended
- the directory contains a normal repo checkout shape
- `rev-parse --show-toplevel` resolves successfully

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
