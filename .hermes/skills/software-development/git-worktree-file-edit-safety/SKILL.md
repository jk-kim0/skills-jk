---
name: git-worktree-file-edit-safety
description: Safely edit files when working in a git worktree so Hermes file-edit tools do not accidentally modify the main checkout.
---

# Git worktree file-edit safety

Use this skill whenever you are making code or workflow changes in a separate git worktree instead of the repository's main checkout.

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

3. Before the first file edit, verify edit context.
   - Prefer absolute file paths for `read_file`, `write_file`, and `patch` when working in a worktree.
   - Do not assume tool-relative paths now point at the worktree just because `terminal(workdir=...)` does.

4. After the first edit, immediately verify location.
   - Check `git status --short` in both:
     - the main checkout
     - the worktree
   - If changes appeared in the wrong checkout, stop and fix it before continuing.

5. If edits landed in the wrong checkout:
   - Copy the changed files into the intended worktree if needed.
   - Restore tracked files in the wrong checkout with `git restore ...`.
   - Remove unintended untracked files manually.
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

## Pitfalls

- `terminal(workdir=...)` succeeding does not guarantee `patch`/`write_file` will target that same directory implicitly.
- A clean worktree branch setup can still be undermined by wrong-path edits.
- This mistake is easy to miss until verification if the same relative file paths exist in both locations.

## Minimum verification before finishing

- Main checkout is clean or only has pre-existing unrelated changes.
- Intended worktree contains the actual diff.
- `git show --stat HEAD` or `git diff --stat` in the worktree matches the requested scope.
- Remote branch push comes from the worktree branch, not from main.
