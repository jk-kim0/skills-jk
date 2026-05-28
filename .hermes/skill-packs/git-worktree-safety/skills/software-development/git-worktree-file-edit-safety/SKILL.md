---
name: git-worktree-file-edit-safety
description: Safely edit files in a git worktree without accidentally modifying the protected main checkout; routes to the canonical main-checkout and repo-root worktree policies instead of duplicating them.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, worktree, file-tools, safety]
    related_skills: [main-checkout-edit-taboo, repo-root-worktree-path-policy]
---

# Git worktree file-edit safety

## Purpose

Use this detailed skill when Hermes file tools (`read_file`, `write_file`, `patch`) may touch repository files while the shell commands are running in a linked worktree.

This file is intentionally a thin checklist. The canonical rules live in:

- `main-checkout-edit-taboo` — main checkout protection, dirty-main recovery, and duplicate/upstreamed main cleanup.
- `repo-root-worktree-path-policy` — where to create worktrees, flat directory names, and worktree verification.

Do not copy those full procedures here; update the canonical skill instead.

## Required procedure

1. Run the canonical pre-edit gate from `main-checkout-edit-taboo`:

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
```

2. If the active checkout is `main`, stop before editing and create/select a non-main worktree under repo-root `.worktrees/` using `repo-root-worktree-path-policy`.

3. Record the absolute worktree path and use it for all file-tool paths:

```bash
WT="$(git rev-parse --show-toplevel)/.worktrees/<flat-name>"
git -C "$WT" status --short --branch
```

4. For `read_file`, `write_file`, and `patch`, pass absolute paths under `$WT`. Do not rely on `terminal(workdir=...)` to affect file tools.

5. After the first edit, verify both locations:

```bash
git status --short --branch
git -C "$WT" status --short --branch
```

If edits appear in the root/main checkout, follow the recovery flow in `main-checkout-edit-taboo` before continuing.

## Release/rebase force-push reminder

For follow-up work on an existing branch, verify the remote ref before force-pushing:

```bash
branch=$(git -C "$WT" branch --show-current)
old=$(git ls-remote origin "refs/heads/$branch" | awk '{print $1}')
# after rebase/amend:
git -C "$WT" push --force-with-lease="refs/heads/$branch:$old" origin HEAD:"refs/heads/$branch"
```

Use the more specific GitHub PR workflow pack when the task is about an open PR branch rather than only local file-edit safety.

## Minimum verification

- active edits are in a non-main worktree
- file tools used absolute paths under that worktree
- root/main checkout status did not gain task-related changes
- branch/ref safety checks were done before push or force-push
