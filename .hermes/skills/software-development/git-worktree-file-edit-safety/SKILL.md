---
name: git-worktree-file-edit-safety
description: Safely edit files when working in a git worktree so Hermes file-edit tools do not accidentally modify the main checkout.
---

# Git worktree file-edit safety

Use this skill whenever you are making code or workflow changes in a separate git worktree instead of the repository's main checkout.

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

## Why this exists

In Hermes, shell commands can run in the intended worktree via `terminal(workdir=...)`, but file-edit tools such as `read_file`, `write_file`, and `patch` may still operate relative to the current chat/session cwd if you do not give explicit paths. That can lead to accidental edits in the main checkout even when your git worktree and branch setup were correct.

## When to trigger

- You created or selected a git worktree for branch-isolated changes.
- The user explicitly wants worktree-first safety.
- The repository root and the worktree both contain the same relative paths.
- You plan to use Hermes file-edit tools instead of pure shell editing.

## Required procedure

1. Discover both locations explicitly.
   - Run `pwd`.
   - Run `git rev-parse --show-toplevel` in the current checkout.
   - If using a separate worktree, capture its absolute path too.

2. Create/select the worktree first.
   - Use `git fetch origin --prune`.
   - Create the worktree from `origin/main` (or the requested base).
   - Verify the worktree branch and merge-base before editing.
   - If the repository does not ignore `.worktrees/`, add `.worktrees/` to the root checkout's `.git/info/exclude` after creating the linked worktree. This keeps the protected main checkout clean without committing repository-wide ignore policy changes.

3. Before the first file edit, verify edit context.
   - Prefer absolute file paths for `read_file`, `write_file`, and `patch` when working in a worktree.
   - Do not assume tool-relative paths now point at the worktree just because `terminal(workdir=...)` does.

4. After the first edit, immediately verify location.
   - Check `git status --short` in both:
     - the main checkout
     - the worktree
   - If changes appeared in the wrong checkout, stop and fix it before continuing.

5. If edits landed in the wrong checkout:
   - Report the violation to the user briefly before continuing.
   - Capture the wrong-checkout diff with `git diff --binary > /tmp/<repo>-main-pollution.patch`.
   - Create/select the intended non-main worktree or branch.
   - Apply the captured patch in the intended worktree with `git apply --index` when possible, or plain `git apply` if needed.
   - If the patch fails, stop and report the conflict while preserving the patch file path.
   - Restore tracked files in the wrong checkout with `git restore ...`.
   - Remove only unintended untracked files that were clearly created by the mistaken task, after listing them.
   - Do not stash by default; preserve work in the branch/worktree instead.
   - Re-run `git status --short` in both locations to confirm cleanup.

6. Only commit from the intended worktree.
   - Run `git status --short` in the worktree.
   - Review the diff there.
   - Commit and push from the worktree branch only.

## Recommended command pattern

Use shell commands like these for verification:

```bash
pwd
git rev-parse --show-toplevel
git branch --show-current
git status --short
```

For dual-check verification:

```bash
cd /path/to/main-checkout && git status --short
cd /path/to/worktree && git status --short
```

If the user questions whether work happened in a worktree, answer with evidence, not reassurance. Run a full provenance check and report the exact paths:

```bash
printf 'tool cwd: '; pwd
cd /path/to/main-checkout
git status --short --branch
git branch --show-current
git rev-parse --show-toplevel
git rev-parse --git-dir
git rev-parse --git-common-dir
git worktree list --porcelain
cd /path/to/worktree
git status --short --branch
git branch --show-current
git rev-parse --show-toplevel
git rev-parse --git-dir
git rev-parse --git-common-dir
git log --oneline --decorate --max-count=5
git diff --name-status
```

Then explicitly distinguish:
- the protected/root checkout path and branch,
- the intended worktree path and branch,
- whether either checkout has uncommitted diff,
- whether the remote branch head matches the local worktree `HEAD`, and
- any non-repo skill/memory edits made outside the project worktree.

## Pitfalls

- `terminal(workdir=...)` succeeding does not guarantee `patch`/`write_file` will target that same directory implicitly.
- A clean worktree branch setup can still be undermined by wrong-path edits.
- This mistake is easy to miss until verification if the same relative file paths exist in both locations.

## Release branch rebase / force-push safety

Use this pattern when the user asks to rebase a shared release branch onto the latest main and force-push it.

1. Treat the root `main` checkout as inspection-only. Fetch first:
   ```bash
   git fetch origin --prune
   ```
2. Check whether the local release ref is stale relative to `origin/release`:
   ```bash
   git rev-list --left-right --count release...origin/release
   git log --oneline origin/release..release
   git log --oneline release..origin/release --max-count=10
   ```
3. If local `release` has no unique commits and is behind remote, align it before creating the worktree:
   ```bash
   git branch -f release origin/release
   git worktree add .worktrees/release-rebase release
   ```
4. Rebase from the release worktree, not the root checkout:
   ```bash
   git -C .worktrees/release-rebase rebase origin/main
   ```
5. Resolve conflicts by preserving latest-main behavior plus the release-only fix when both are still needed. For CSS/UI conflicts, inspect `origin/main:<path>`, the release commit (`REBASE_HEAD`), and any added regression tests before choosing one side.
6. Run the narrowest relevant verification before continuing and again rely on the rebase state:
   ```bash
   git add <resolved-files>
   GIT_EDITOR=true git rebase --continue
   ```
7. Before pushing, verify the release branch is exactly latest main plus the intended release-only commits:
   ```bash
   git rev-list --left-right --count origin/main...HEAD
   git log --oneline --decorate -5
   ```
   A common desired result after a hotfix release rebase is `0 1` (no commits missing from release, one release-only commit ahead).
8. Push with lease, then verify remote equality:
   ```bash
   git push --force-with-lease origin release
   git fetch origin --prune
   git rev-parse release
   git rev-parse origin/release
   git rev-list --left-right --count origin/main...release
   ```

## Minimum verification before finishing

- Main checkout is clean or only has pre-existing unrelated changes.
- Intended worktree contains the actual diff.
- `git show --stat HEAD` or `git diff --stat` in the worktree matches the requested scope.
- Remote branch push comes from the worktree branch, not from main.
- For release branch rebases, local `release` and `origin/release` point at the same post-push SHA, and `origin/main...release` shows only the intended release-only commits.
