---
name: git-worktree-safety-pack
description: Use when doing local git branch/worktree cleanup, main-checkout safety checks, repo-root .worktrees policy, or stale-branch classification; points to an inactive detailed skill pack instead of keeping many overlapping active skills.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, worktree, cleanup, branch-safety, skill-pack]
    related_skills: [github-pr-workflow]
---

# Git Worktree Safety Pack

## Overview

This is the active entrypoint for local Git/worktree safety workflows in this repo-local Hermes setup. The detailed procedures were consolidated out of active `.hermes/skills/` to reduce duplicated skill surface while preserving the underlying knowledge.

## When to Use

- Updating local `main` safely before repo work.
- Creating or validating repo-root `.worktrees/<flat-name>` worktrees.
- Preventing edits in a checkout currently on `main`.
- Cleaning stale local branches/worktrees.
- Classifying branch value by synthetic squash, rebase portability, or latest-main diff.

## Required Context

Read `.hermes/skill-packs/git-worktree-safety/INDEX.md`, then load only the detailed skill file(s) selected by that index. The index includes a canonical ownership map; patch the owning detailed skill instead of duplicating the same Git/worktree procedure in another file.

## Common Pitfalls

1. Do not recreate a narrow active skill for a one-off branch/worktree cleanup incident; add a reference under this pack instead.
2. Do not bulk-load every detailed skill in the pack. Pick the relevant detailed file from the index.
3. Keep repo-specific cleanup learnings in the governing detailed file or a reference, not as a new top-level active skill.

## Verification Checklist

- [ ] `INDEX.md` was read before detailed cleanup/refactor work.
- [ ] Only relevant detailed files from the pack were loaded.
- [ ] New cleanup lessons were added to this pack instead of creating another active sibling skill.
