---
name: workspace-stale-git-cleanup
description: Safely clean stale git branches and worktrees across many repositories under a workspace root, using conservative rules and explicit verification.
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Workspace stale git cleanup

Use when the user asks to clean stale branches/worktrees from the current workspace root rather than from a single repository.

## When this skill applies

- Current directory is a workspace folder like `~/workspace`, not a git repo itself.
- There may be many sibling repos, some with linked worktrees.
- The user wants safe cleanup, not aggressive pruning.

## Scope interpretation rule

Distinguish carefully between these two user intents:

1. `workspace 정리해줘` or similar, when the user clearly means the whole local workspace root
   - interpret as cross-repository cleanup under `~/workspace`
2. `이 repo 의 workspace 정리` / `this repo's workspace cleanup`
   - interpret as repo-local cleanup only
   - clean only the current repository's worktrees, local branches, and obvious temp leftovers
   - do **not** scan or modify sibling repositories

If the user is currently inside a repo and the phrasing mentions `this repo`, prefer repo-local interpretation even if the word `workspace` appears.

## Safety rules

1. Do not delete the current checked-out branch.
2. Do not delete any branch currently checked out by any worktree.
3. Do not delete detached worktrees if they have uncommitted or untracked files.
4. Do not auto-delete generic local branches like `main`, `master`, `develop`, `release`, or `alpha` unless the user explicitly asks.
5. Treat top-level repos in detached HEAD state as special; do not assume they are stale worktrees.

## Discovery steps

1. Confirm the current directory is not itself a git repo:
   - `git rev-parse --show-toplevel`
2. Enumerate sibling repos under the workspace root by checking for `.git`.
3. Deduplicate repos by `git rev-parse --git-common-dir` so secondary linked worktrees are not processed twice as if they were separate repositories.
4. For each unique repo, collect:
   - `git worktree list --porcelain`
   - `git branch -vv`
   - default branch via `git symbolic-ref refs/remotes/origin/HEAD` (fallback to current branch if needed)

## Default interpretation for "workspace cleanup"

In this user's setup, a request like `workspace 정리` means:

1. refresh remote refs
2. move each repo root checkout back to its default branch (`main`, `develop`, etc.) when the root worktree is clean
3. update that default branch to the latest remote HEAD with a safe fast-forward when possible
4. remove clearly stale local worktrees and branches
5. preserve any dirty root repo or dirty worktree instead of forcing cleanup

User-specific requirement:
- include default-branch update as a standard part of workspace cleanup, not an optional extra
- for `main`-based repos, this normally means aligning local `main` to the latest `origin/main`
- if the root worktree is dirty, do not switch branches or fast-forward automatically; report it as intentionally preserved
- if the update is not a clean fast-forward, stop and report rather than forcing history changes

## Conservative stale classification

### Worktree candidates

Mark as removable only when one of these is true:
- `prunable` in `git worktree list --porcelain`
- detached worktree with clean `git status --porcelain`
- branch-backed worktree whose head branch has no open PR and only closed/merged PR history, indicating it is a post-merge leftover

Keep if:
- detached but dirty
- branch-backed worktree with an open PR or active unpublished purpose
- main/top-level repo even if detached

### Escalation rule for repeated repo-local cleanup requests

If the user repeatedly asks to clean "this repo's workspace" after conservative cleanup already removed the obvious clean/prunable items, treat that as permission to escalate one level further:

- preserve root worktrees with real local modifications
- preserve normal branch-backed worktrees that correspond to open PR head branches
- preserve open-PR local branches even if their detached helper worktrees are removed
- remove detached helper worktrees used only for rebase/conflict/follow-up scratch state, even when they are dirty, if all of the following are true:
  - they are not the primary/root worktree
  - they are detached rather than branch-backed
  - they are clearly helper names like `pr157-rebase`, `pr158-rebase-latest`, `pr157-followup`, `pr158-mainrewrite2`, etc.
  - the meaningful open-PR branch or kept branch-backed worktree remains elsewhere

This matches the practical user expectation that repeated cleanup requests mean "stop preserving conflict scratchpads and helper clones; keep only real active worktrees."
### Branch candidates

Mark as removable only when one of these is true:
- local branch has upstream `[gone]` in `git branch -vv` and is not checked out anywhere
- local branch is fully merged into the repo default branch and is not checked out anywhere
- local branch has no open PR and only closed/merged PR history, and is not checked out anywhere

Exclude by default:
- current branch
- any branch present in any worktree
- `main`, `master`, `develop`, `release`, `alpha`

## GitHub PR cross-check for branch-backed worktrees

When a worktree is branch-backed, do not rely only on `git merge-base --is-ancestor` or ahead/behind counts.
Squash merges often leave the original branch commit graph appearing unmerged even though the PR was already merged.

Preferred check:

```bash
repo=$(gh repo view --json nameWithOwner -q .nameWithOwner)
gh pr list --repo "$repo" --head <branch> --state open --json number,state,isDraft,url,title
gh pr list --repo "$repo" --head <branch> --state closed --json number,state,mergedAt,closedAt,url,title
```

Interpretation:
- open PR exists -> not stale by default
- no open PR and closed PR is `MERGED` -> usually stale if the worktree is just leftover cleanup
- closed PR without merge -> inspect before deleting

Important practical follow-up:
- after removing a merged PR's leftover worktree, `git branch -d` may still refuse deletion because squash/rebase merges are not direct ancestors
- when the PR is confirmed merged and the branch is no longer attached anywhere, it is acceptable to delete the branch with `git branch -D <branch>`
- do not use `-D` based only on `upstream: gone`; require merged-PR evidence first

## Temporary PR-body files inside stale worktrees

Files like `.tmp-pr-body.md` are often PR-process leftovers rather than meaningful work product.
If the branch has no open PR and only merged PR history, an untracked temp PR-body file should not by itself block stale-worktree deletion.
Inspect the file briefly, but if it is clearly a PR draft/body scratch file, treat it as disposable cleanup state.

## Important command pitfalls

When removing a worktree, run the command from the owning repo context:

```bash
git -C /path/to/main/repo worktree remove --force /path/to/worktree
```

Do not run plain `git worktree remove ...` from an arbitrary non-repo directory. That can fail with `fatal: not a git repository`.

If the main repo itself is dirty and you need to switch the root worktree back to `main`, be careful with nested linked worktrees stored under the repo directory such as `.claude/worktrees/...`.

Observed behavior:
- `git stash -u` does not absorb nested linked worktrees
- Git can print lines like `Ignoring path .claude/worktrees/<name>/`
- after switching branches, the parent repo may still show `?? .claude/worktrees/`

Interpretation:
- this does not by itself mean the root repo is unsafe or that the child worktrees are stale
- do not delete nested worktree directories just to make `git status` look clean
- treat them as active linked worktrees and inspect `git worktree list` first

## Recommended execution order

1. Report what is being checked.
2. Discover repos and candidates.
3. Remove only clearly safe stale worktrees first.
4. Run `git -C <repo> worktree prune` after removals.
5. Delete clearly stale local branches.
6. Re-run `git worktree list --porcelain` and `git branch -vv` to verify the result.
7. If a `git worktree remove --force <path>` attempt fails, do not assume the worktree is still present. Re-check both:
   - whether the filesystem path still exists
   - whether `git worktree list --porcelain` still tracks that path
   In practice, some "failed" removals are already effectively cleaned up, especially after prune or when the path disappeared earlier.
8. Summarize what was deleted and what was intentionally left alone.

## Good final-report format

- Deleted stale worktrees
- Deleted stale branches
- Verification result
- Intentionally preserved items and why

## Example preserved items

- detached worktree with untracked temp files
- generic local branch names with possible policy meaning
- top-level repo in detached HEAD state

## Additional safe cleanup win: empty worktree namespace directories

In large workspaces, after `git worktree prune` there may be no real removable worktrees left, but empty namespace directories can remain under containers like:

- `.worktrees/<group>`
- `.claude/worktrees/<name>/.claude`

These are not worktrees themselves; they are just leftover empty directories.

Safe rule:
- only remove them if the directory is completely empty
- do not remove non-empty grouping directories just because they are not registered worktrees
- do not recurse into populated worktree trees looking for arbitrary empty subdirectories; limit cleanup to obvious top-level namespace shells or clearly empty helper dirs

Recommended sequence:
1. run `git worktree prune`
2. verify there are no prune candidates with `git worktree prune --dry-run --verbose`
3. optionally delete only clearly empty namespace/helper directories

This is a good conservative fallback when the user wants the workspace "cleaned up" but branch/worktree deletion is not clearly safe.
