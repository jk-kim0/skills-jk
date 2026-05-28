---
name: main-checkout-edit-taboo
description: "Mandatory safety rule for repository work: never create local file changes in a workspace checked out to main; always use a non-main worktree unless explicitly authorized."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [git, worktree, safety, repository, taboo]
---

# Main checkout edit taboo

Use this skill for any repository work that might read, write, patch, generate, restore, commit, or push files.

## Absolute rule

Never create local file changes in a workspace checked out to `main`.

Treat the main checkout as a protected control workspace for inspection, fetch, status, and cleanup only. This is a hard taboo, not a preference.

Only exception: the user explicitly authorizes editing the main workspace for the exact current task.

## Mandatory pre-edit gate

Before any file edit or generated file write, run:

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
```

If `git branch --show-current` returns `main`, do not edit. Create or select a linked worktree under the repo root using the canonical path and verification policy in `repo-root-worktree-path-policy`.

## File-tool safety

When working from a non-main worktree, use absolute paths for `read_file`, `write_file`, and `patch`. Do not assume file tools inherit `terminal(workdir=...)`.

After the first edit, check both locations:

```bash
git status --short --branch
git -C .worktrees/<flat-name> status --short --branch
```

If changes appear in the main checkout, stop, report the violation, move/reapply changes into the intended worktree if needed, and restore main before continuing.

## Automatic remediation when a violation is discovered

If local changes are discovered in a `main` checkout and they appear to be agent-created or task-related, do not leave them there and do not continue normal work from main.

Perform this recovery automatically:

1. Report the violation to the user briefly.
   - Say that main checkout pollution was found.
   - List the changed files.
   - Say that recovery is being performed.

2. Capture the root workspace diff before touching anything:

```bash
git status --short --branch
git diff --binary > /tmp/<repo>-main-pollution.patch
git diff --stat
```

3. Create or select the correct non-main worktree/branch:

```bash
git fetch origin --prune
git worktree add .worktrees/<flat-name> -b <branch-name> origin/main
```

If the intended branch/worktree already exists, verify it is not `main` and use that.

4. Move the mistaken changes into the non-main worktree:

```bash
git -C .worktrees/<flat-name> apply --index /tmp/<repo>-main-pollution.patch || git -C .worktrees/<flat-name> apply /tmp/<repo>-main-pollution.patch
```

If the patch does not apply cleanly, stop and report the conflict instead of improvising. Preserve the patch path.

5. Restore the root main workspace:

```bash
git restore <changed-tracked-files>
# do not delete content-like untracked files (docs, references, skills, markdown) just to clean root main
# only remove obvious runtime/lock/cache artifacts after listing them; otherwise preserve/report them first
```

Do not stash by default. Prefer preserving work in the branch/worktree over stashing.

6. Verify both locations:

```bash
git status --short --branch
git -C .worktrees/<flat-name> status --short --branch
git -C .worktrees/<flat-name> diff --stat
```

7. Continue work only in the non-main worktree.

## Preferred recovery when root `main` dirt is meaningful and a fresh latest-main task must start now

A recurring real-world case is:
- root checkout is on `main`
- there are meaningful local changes already sitting in that root checkout
- the user asks for a new task that should start from latest `origin/main`
- continuing on dirty `main` would violate the taboo, but simply discarding the dirt would lose work

Preferred handling for that case:
1. briefly tell the user that root `main` is dirty and cannot be used directly
2. preserve the dirty root state onto a clearly named non-main branch **from the root checkout itself**
3. commit the preserved files there
4. switch the root checkout back to `main`
5. hard-reset or fast-forward root `main` to the latest `origin/main`
6. create a fresh worktree/branch from that clean latest-main baseline
7. do the new task only in the fresh worktree

Important variant: the user may ask for both `main` refresh and immediate PR creation from the already-dirty root changes.

Common trigger wording includes "이 repo 의 변경사항을 PR 로 작성해줘" / "create a PR from this repo's changes" when `git status` shows meaningful tracked/untracked changes on a root `main` checkout. Treat those changes as the user's intended PR payload unless inspection shows obvious unrelated runtime/cache residue.

Important pitfall when root `main` is behind latest `origin/main`:
- do not repopulate the fresh latest-main worktree by blindly copying every dirty root file over the checkout
- a raw file copy can overwrite content that already changed upstream and effectively reintroduce stale pre-merge text
- instead, transplant tracked changes as a diff relative to the dirty root base using `git diff --binary` plus `git apply --3way` in the fresh worktree, then copy only authored untracked files that are truly new or intentionally different from `origin/main`
- for untracked files whose paths already exist in `origin/main`, compare the root file to `origin/main:<path>` first and skip byte-identical copies; only carry them over when they are a real follow-up edit
- after transplant, resolve any narrow conflicts by keeping latest-main content and adding only the new local follow-up lines

In that case, do not stop after merely preserving the dirty root on a branch.
Use this exact sequence:
1. inspect and summarize the intended payload first with `git diff --stat` and `git diff --name-status`, including untracked files that should be part of the PR
2. commit the meaningful root changes onto a non-main branch from the root checkout
3. switch root back to `main`
4. fast-forward root `main` to latest `origin/main`
5. open a fresh linked worktree for the preserved branch
6. rebase that preserved branch onto the refreshed `origin/main`
7. verify the PR diff is now only the intended preserved change
8. push and create the PR from the non-main worktree
9. verify local HEAD, remote branch HEAD, PR head SHA, base branch, and PR file list before reporting completion

Why this variant matters:
- it satisfies the user's `main 업데이트` request immediately instead of leaving root `main` stale
- it avoids opening a PR whose base is older than the freshly updated `origin/main`
- it keeps the review diff narrow and avoids mixing root-control cleanup with feature/docs preservation

Recommended verification for this variant:
```bash
git status --short --branch
git rev-parse main
git rev-parse origin/main
git -C .worktrees/<flat-name> rev-list --oneline origin/main..HEAD
git -C .worktrees/<flat-name> diff --name-only origin/main...HEAD
```

Practical rule for generated local runtime files and untracked authored docs during this preservation flow:
- do not automatically add machine-local generated files just because they are untracked in the dirty root checkout
- do not automatically add untracked authored docs/guidance/planning files just because they look relevant; first verify whether they belong to the current request, another local branch, another agent's work, or an already-open PR
- classify and usually exclude obvious runtime/usage artifacts such as lock files or local usage state when they are not part of the intended repo change
- commit only the meaningful tracked files plus intentional new authored reference/doc/source files whose provenance and scope match the current PR

Example pattern:

```bash
git status --short --branch
git switch -c preserve/<topic>
git add <intended-files>
git commit -m "chore: preserve local main changes before new task"
git switch main
git fetch origin --prune
git reset --hard origin/main
git worktree add .worktrees/<flat-name> -b <branch-name> origin/main
```

Why this pattern matters:
- it preserves the user's existing local work as inspectable branch history rather than a stash
- it restores the root `main` checkout to a clean control baseline immediately
- it avoids mixing old root-local dirt into the new task branch
- it keeps the next implementation branch truly based on the latest remote main tip

Use this preservation-branch pattern when the dirty root changes are coherent and worth keeping as their own line of work. Use the patch-file migration flow above when the changes must be transplanted directly into the new task worktree instead.

## Main update when dirty changes are already present upstream

When the user asks to update `main` and the root checkout is dirty, first determine whether the dirt is meaningful unpublished work or merely local duplicates of changes that have already landed in `origin/main`.

Recommended flow:

```bash
git fetch origin --prune
git status --short --branch
git diff --stat
git diff --name-status
git log --oneline --decorate --left-right main...origin/main
```

For each dirty tracked/untracked file that overlaps upstream changes:
- compare the local file against `origin/main:<path>` when the path exists there
- for untracked files that would block checkout/reset, use `cmp -s local <(git show origin/main:path)` or an equivalent byte-level comparison before removing them
- inspect upstream excerpts for files where local text is similar but not identical; prefer the newer upstream version when it is clearly the completed form of the same change

If the local dirt is confirmed to be duplicate/upstreamed rather than separate work:
1. save a safety backup first, e.g. `git diff --binary > /tmp/<repo>-main-update-<timestamp>/local.diff`, and copy any untracked blocker files there
2. remove only untracked files that are byte-identical to `origin/main:<path>` and would block the update
3. reset/fast-forward root `main` to `origin/main`
4. verify `git status --short --branch`, `git rev-parse main`, and `git rev-parse origin/main`
5. check conflict markers with an anchored search such as `^(<{7}|>{7})`; a broad `=======` search can false-positive on markdown/comment separators

Do not use this shortcut when local files differ materially from `origin/main` or their provenance is unclear. Preserve those changes onto a non-main branch/worktree instead.

## Done criteria

- any discovered main-checkout pollution has been reported
- task-related mistaken changes have been moved to a non-main worktree/branch, or duplicate/upstreamed dirt has been safely backed up and removed before updating main
- root main workspace has been restored to its pre-task clean/control state, except explicitly pre-existing unrelated changes
- all new edits are in a non-main worktree
- commits and pushes happen from the worktree branch, never from `main`
