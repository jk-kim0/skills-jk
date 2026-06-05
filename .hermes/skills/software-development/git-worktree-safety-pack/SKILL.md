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

If the cleanup starts with root `main` dirty while behind `origin/main`, also read `references/dirty-root-behind-main-preservation.md` so meaningful local skill/docs changes are preserved into a reviewable branch before root main is reset or fast-forwarded.

If the root checkout is not on `main`, the root branch's PR is already merged/closed, and the root still has dirty authored skill/docs/config changes, also read `references/root-stale-merged-branch-dirty-preservation.md`; preserve the authored payload on a fresh latest-main PR branch before resetting/cleaning root and switching back to `main`.

If a previous dirty-root preservation PR was recently merged and the stale root diff against `origin/main` shows apparent mass deletions, read `references/repeated-cleanup-merged-preservation-pr-stale-deletions.md`; preserve only selected authored skill/docs payload on a fresh latest-main worktree, not the whole stale patch.

If the cleanup request includes Open PR checking, CI follow-up, a wait-and-repeat pass, newly preserved PRs, or a PR-less branch/worktree with meaningful dirty content, also read `references/open-pr-cleanup-repeat-and-preservation.md` so the sweep keeps looping across merges, retargeted child PRs, stale PR metadata, and newly discovered dirty files.

If the user asks to rebase all open PRs onto the latest `main`, also use the GitHub PR workflow reference `github-pr-workflow/references/batch-open-pr-rebase-latest-main.md`: treat the open PR list as live, fetch `origin/main` before each branch, push rebased branches with `--force-with-lease`, and do a final merge-base verification after re-listing open PRs.

If `.worktrees/` contains subdirectories that are not listed by `git worktree list`, inspect them as possible standalone checkouts or accidentally nested repositories with meaningful dirty work before deleting anything.

If the repository still has `.hermes/skill-packs/git-worktree-safety/INDEX.md`, read that index too, then load only the detailed skill file(s) selected by the index. The index includes a canonical ownership map; patch the owning detailed skill instead of duplicating the same Git/worktree procedure in another file.

If the repo-local detailed index is missing or empty, do not block cleanup. Use this skill's bundled reference and live Git/GitHub state as the source of truth.

If the current repository does not have that repo-local skill-pack path, proceed with the safety rules in this active skill and verify with live Git/GitHub state instead of blocking cleanup.

## References

- `references/root-dirty-followup-into-existing-pr.md` — when root `main` is up to date but dirty again with authored guidance and an existing open preservation PR covers the same bucket, apply the root authored diff into that PR branch with a 3-way patch, exclude runtime residue such as `.hermes/lsp/**`, amend/force-push, then reset/clean root.
- `references/root-stale-merged-branch-dirty-preservation.md` — when the root checkout is on a stale merged/closed branch rather than `main` but still has dirty authored guidance, preserve the payload on a fresh latest-main PR branch before resetting root, switching to `main`, and deleting stale branches/worktrees.
- `references/repo-local-workspace-cleanup-sweep.md` — canonical repo-local `workspace 정리` sweep: update root `main`, inspect dirty payloads, targeted PR lookup, preserve open-PR worktrees, delete clean merged/stale branches, and report final root/worktree state.
- `references/cleanup-preserve-dirty-payload-into-open-pr.md` — when cleanup finds a dirty PR-less worktree whose payload belongs to an existing open PR, copy/commit or push it into the correct PR branch, verify equality, then remove the redundant source worktree.
- `references/post-push-dirty-followup-and-duplicate-pr-worktrees.md` — after preserving or amending an open PR branch, rerun dirty sweeps, include same-scope follow-up files, revert out-of-scope tests, remove duplicate PR worktrees, and verify remote heads before starting a delayed wait.
- `references/profile-config-preservation-during-cleanup.md` — when cleanup finds repo-tracked Hermes profile/config changes mixed with local guidance, update the existing preservation worktree/PR branch and reduce YAML-normalization noise to the intended scalar config changes.
- `references/merged-preservation-pr-branch-refusal.md` — when a preservation PR is merged mid-cleanup and force-push/update is refused, do not resurrect the merged branch; create a fresh latest-main branch/PR for only the remaining authored payload.
- `references/workflow-dispatch-pr-creation-verification.md` — when cleanup preserves local work and the repo creates PRs through a `workflow_dispatch` action, verify default-branch-dispatched runs without relying on `gh run list --branch <feature-branch>`; pass body content to `-f body=...`, not `-f body-file=...`, unless the workflow defines that input.
- `github-pr-workflow/references/batch-open-pr-rebase-latest-main.md` — companion GitHub PR workflow reference for rebase-all-open-PR sweeps: live open-PR list, per-branch latest-main fetch, `--force-with-lease`, and final merge-base verification.
- When a single PR is rebased onto latest `main`, re-query `gh pr view <pr> --json headRefOid,baseRefOid,mergeStateStatus,statusCheckRollup` after push. If `origin/main` advanced during the rebase/push window and the PR `baseRefOid` no longer matches the freshly fetched `origin/main`, fetch/rebase/push again before reporting the PR as current.

## Common Pitfalls

0. When creating or using repo-root `.worktrees/<name>` worktrees for Node/Next.js repositories, avoid duplicating large dependency directories inside every worktree. If the root checkout already has the needed dependencies, prefer a worktree-local symlink from the package directory to the root checkout's `node_modules` (for example, from `.worktrees/<name>/front`: `ln -s ../../../front/node_modules node_modules`). Only reinstall in the root checkout when the shared dependency tree is missing or the lockfile requires it.

1. Do not recreate a narrow active skill for a one-off branch/worktree cleanup incident; update the canonical existing reference in this pack instead.
2. Before adding a new cleanup reference, check `skills-jk/references/reference-dedupe-preflight.md` and search this pack's references for the durable topic. Repeated cleanup incidents should usually patch an existing reference, not create a new session-named file.
3. Do not bulk-load every detailed skill in the pack. Pick the relevant detailed file from the index.
4. Keep repo-specific cleanup learnings in the governing detailed file or a reference, not as a new top-level active skill.
4. After preserving meaningful dirty-root changes in a PR, do one final root-state sweep before reporting completion. Restore duplicate inspection/copy artifacts from the root checkout only after verifying the PR branch contains the intended payload; then remove merged/stale worktrees and branches while keeping the open PR worktree. See `references/final-sweep-after-preserve-pr.md`.
5. In repeated cleanup after a preservation PR has merged, treat apparent deletions from stale root-vs-latest-main diffs as suspicious. Preserve additional work by creating a fresh latest-main worktree and copying only existing authored payload; do not let an old root baseline delete files that the merged PR already added. See `references/repeated-cleanup-merged-preservation-pr-stale-deletions.md`.
6. Do not rely only on a single broad `gh pr list --state open` result before deleting local worktrees/branches. For any remaining dirty, ambiguous, recently touched, or otherwise suspicious branch, run a targeted PR lookup such as `gh pr list --state all --head <branch> --json number,state,title,url,mergedAt,closedAt` and preserve the worktree if it has an open PR.
7. A branch can be merged into `origin/main` or track `origin/main` while its worktree still contains meaningful uncommitted/untracked work. Inspect dirty payloads before deletion; if meaningful, commit/push/create or update a PR, then rerun status to catch missed related files. See `references/dirty-merged-branch-preserve-pr.md`.
8. When a dirty PR-less worktree or dirty root contains payload that belongs to an existing open PR, preserve it in that open PR branch instead of opening a duplicate PR. Commit or copy the payload into the retained PR worktree, verify equality for copied generated/assets files, amend/force-push if needed, and only then remove the source/root duplicate. See `references/cleanup-preserve-dirty-payload-into-open-pr.md` and `references/open-pr-cleanup-repeat-and-preservation.md`. If follow-up files appear after the PR was created or updated, amend/force-push the same PR branch before the final clean sweep; do not leave related docs/spec edits dirty just because the main payload was already pushed.
9. For brand-new repositories with no commits or missing `origin/main`, use an orphan worktree under repo-root `.worktrees/` instead of editing unborn `main`; keep `.worktrees/` out of root status via local `.git/info/exclude` unless a tracked ignore file is desired. See `references/empty-repo-orphan-worktree.md`.
10. During a non-interactive rebase after resolving conflicts, `git rebase --continue` can open an editor and hang in CLI agent sessions. Use `GIT_EDITOR=true git rebase --continue` when the existing commit message should be accepted unchanged.
11. When resolving a PR rebase conflict in a repo-root worktree, preserve the latest `origin/main` structural wrapper and reapply only the PR's still-valid payload inside it. A common conflict shape is a page or route file where main added a new shell/anatomy/section structure while the PR added a new section against an older wrapper; do not resurrect the old wrapper just to keep the PR hunk. After manually rebuilding the tail/section tree, run `git diff --check`, confirm no conflict markers remain, then continue the rebase.
12. If root `main` is behind latest `origin/main` after a previous preservation PR merged, broad diffs against `origin/main` can contain stale deletion hunks. Do not apply the whole patch; copy only selected authored skill/docs payload onto a fresh latest-main worktree, verify the PR branch, then reset/clean root. See `references/repeated-cleanup-merged-preservation-pr-stale-deletions.md`. If that preservation PR merges mid-cleanup and updating/force-pushing its branch is refused, do not resurrect the merged branch; create a new latest-main branch/PR for the remaining authored payload. See `references/merged-preservation-pr-branch-refusal.md`.
13. A push is not the end of a preservation cleanup step. After every commit/amend/force-push, rerun the dirty sweep in the retained PR worktree; same-scope source/test/page/widget follow-up files should be amended into that PR, while tests for unimplemented extra scope should be reverted or implemented deliberately. See `references/post-push-dirty-followup-and-duplicate-pr-worktrees.md`.
14. When CI/checks remain pending and a delayed follow-up is warranted, use a tracked short timer/background process and return control. On timer completion, perform a full fetch + open PR check rollup + retained worktree clean sweep. If all checks are green, explicitly stop the wait loop instead of scheduling another timer. See `references/open-pr-cleanup-repeat-and-preservation.md`.
15. Duplicate worktrees can point at the same open-PR head under different local branch names, including stale branches tracking `origin/pr/<number>`. Compare `git rev-parse HEAD`, the retained branch head, and `gh pr view/list` head OIDs before deleting the duplicate; once equal and clean, remove the duplicate worktree/branch instead of preserving a second PR.
16. If root `main` is already up to date but dirty again with authored local guidance while an open preservation PR covers the same bucket, update that existing PR instead of opening a duplicate. Build a binary patch from root authored paths, exclude runtime residue such as `.hermes/lsp/**`, apply it into the PR worktree with `git apply --3way`, resolve documentation conflicts by keeping both class-level lessons, amend/force-push, verify the remote head, then reset/clean root. See `references/root-dirty-followup-into-existing-pr.md`.

## Verification Checklist

- [ ] For workspace cleanup, `references/repo-local-workspace-cleanup-sweep.md` was read.
- [ ] For dirty root behind latest main, `references/dirty-root-behind-main-preservation.md` was read.
- [ ] If root is on a stale merged/closed non-main branch with dirty authored payload, `references/root-stale-merged-branch-dirty-preservation.md` was read and payload was preserved on a fresh latest-main PR branch before resetting root.
- [ ] If a prior preservation PR was recently merged or the stale root diff shows apparent mass deletions, `references/repeated-cleanup-merged-preservation-pr-stale-deletions.md` was read and stale deletion/runtime hunks were excluded from the new preservation PR.
- [ ] For Open PR + cleanup repeat/preservation loops, `references/open-pr-cleanup-repeat-and-preservation.md` was read.
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
