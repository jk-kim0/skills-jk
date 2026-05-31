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

For repo-local workspace cleanup requests such as `workspace 정리`, first read `references/repo-local-workspace-cleanup-sweep.md` from this skill.

If cleanup discovers a PR-less branch/worktree with meaningful dirty content during an open-PR sweep, also read `references/pr-less-preservation-during-open-pr-sweep.md` so the work is preserved as a PR and then treated as part of the same CI/mergeability loop.

If `.worktrees/` contains subdirectories that are not listed by `git worktree list`, read `references/unregistered-worktrees-during-cleanup.md` before deleting anything. Some of these may be standalone checkouts or accidentally nested repositories with meaningful dirty work that must be preserved first.

If the repository still has `.hermes/skill-packs/git-worktree-safety/INDEX.md`, read that index too, then load only the detailed skill file(s) selected by the index. The index includes a canonical ownership map; patch the owning detailed skill instead of duplicating the same Git/worktree procedure in another file.

If the repo-local detailed index is missing or empty, do not block cleanup. Use this skill's bundled reference and live Git/GitHub state as the source of truth.

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

- [ ] For workspace cleanup, `references/repo-local-workspace-cleanup-sweep.md` was read.
- [ ] If present, `.hermes/skill-packs/git-worktree-safety/INDEX.md` was also read before detailed cleanup/refactor work.
- [ ] Only relevant detailed files from the pack were loaded.
- [ ] Root `main` was fetched and fast-forwarded, and final `git status --short --branch` was reported.
- [ ] Every local branch received targeted PR lookup via `gh pr list --state all --head <branch>`.
- [ ] Every worktree was checked for dirty/untracked files before deletion.
- [ ] Direct children of `.worktrees/` that were not registered in `git worktree list` were inspected as possible standalone checkouts before deletion.
- [ ] PR-less branches with meaningful diff or dirty content were preserved by creating/updating a PR instead of being deleted.
- [ ] After deletions/pushes, fetch/main update/dirty-sweep verification was repeated until no retained worktree was dirty and no empty `.worktrees/` residue remained.
- [ ] New cleanup lessons were added to this pack instead of creating another active sibling skill.
- [ ] For `main 업데이트` / `workspace 정리` sweeps, the final report distinguishes root `main` cleanliness, any intentionally retained open-PR worktree, and merged/stale worktrees or branches that were deleted.
