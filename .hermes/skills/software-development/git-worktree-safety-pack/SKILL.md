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

If the current repository does not have that repo-local skill-pack path, proceed with the safety rules in this active skill and verify with live Git/GitHub state instead of blocking cleanup.

## References

- `references/repo-local-workspace-cleanup-sweep.md` — canonical repo-local `workspace 정리` sweep: update root `main`, inspect dirty payloads, targeted PR lookup, preserve open-PR worktrees, delete clean merged/stale branches, and report final root/worktree state.
- `references/cleanup-preserve-dirty-payload-into-open-pr.md` — when cleanup finds a dirty PR-less worktree whose payload belongs to an existing open PR, copy/commit or push it into the correct PR branch, verify equality, then remove the redundant source worktree.

## Common Pitfalls

1. Do not recreate a narrow active skill for a one-off branch/worktree cleanup incident; add a reference under this pack instead.
2. Do not bulk-load every detailed skill in the pack. Pick the relevant detailed file from the index.
3. Keep repo-specific cleanup learnings in the governing detailed file or a reference, not as a new top-level active skill.
4. After preserving meaningful dirty-root changes in a PR, do one final root-state sweep before reporting completion. Restore duplicate inspection/copy artifacts from the root checkout only after verifying the PR branch contains the intended payload; then remove merged/stale worktrees and branches while keeping the open PR worktree. See `references/final-sweep-after-preserve-pr.md`.
5. Do not rely only on a single broad `gh pr list --state open` result before deleting local worktrees/branches. For any remaining dirty, ambiguous, recently touched, or otherwise suspicious branch, run a targeted PR lookup such as `gh pr list --state all --head <branch> --json number,state,title,url,mergedAt,closedAt` and preserve the worktree if it has an open PR.
6. A branch can be merged into `origin/main` or track `origin/main` while its worktree still contains meaningful uncommitted/untracked work. Inspect dirty payloads before deletion; if meaningful, commit/push/create or update a PR, then rerun status to catch missed related files. See `references/dirty-merged-branch-preserve-pr.md`.
7. When a dirty PR-less worktree contains payload that belongs to an existing open PR, preserve it in that open PR branch instead of opening a duplicate PR. Commit or copy the payload into the retained PR worktree, verify equality for copied generated/assets files, and only then remove the source worktree. See `references/cleanup-preserve-dirty-payload-into-open-pr.md`. If follow-up files appear after the PR was created or updated, amend/force-push the same PR branch before the final clean sweep; do not leave related docs/spec edits dirty just because the main payload was already pushed.
8. For brand-new repositories with no commits or missing `origin/main`, use an orphan worktree under repo-root `.worktrees/` instead of editing unborn `main`; keep `.worktrees/` out of root status via local `.git/info/exclude` unless a tracked ignore file is desired. See `references/empty-repo-orphan-worktree.md`.

## Verification Checklist

- [ ] `INDEX.md` was read before detailed cleanup/refactor work.
- [ ] Only relevant detailed files from the pack were loaded.
- [ ] New cleanup lessons were added to this pack instead of creating another active sibling skill.
- [ ] For `main 업데이트` / `workspace 정리` sweeps, the final report distinguishes root `main` cleanliness, any intentionally retained open-PR worktree, and merged/stale worktrees or branches that were deleted.
