# Follow-up worktree integrity pitfall

Use this when updating an existing open PR and the PR branch is already checked out in another worktree.

## Problem

A detached follow-up worktree created from `origin/pr/<number>` can appear to succeed but later be incomplete, missing, or pruned unexpectedly before file edits are applied. If the agent writes into that path without checking, it can create a tiny partial directory outside a real checkout and lose the intended worktree context.

## Safe sequence

1. Fetch the PR ref:

```bash
git fetch origin pull/<pr-number>/head:refs/remotes/origin/pr/<pr-number> --force
```

2. Create the detached worktree:

```bash
git worktree add .worktrees/<followup-name> origin/pr/<pr-number>
```

3. Verify the checkout shape before writing any files:

```bash
test -f .worktrees/<followup-name>/README.md
git -C .worktrees/<followup-name> status --short --branch
find .worktrees/<followup-name> -maxdepth 2 | sed -n '1,40p'
```

4. If the worktree is incomplete or disappears:

```bash
cp <drafted-file> /tmp/<drafted-file-name>  # only if you already wrote useful content
rm -rf .worktrees/<followup-name>
git worktree prune
git fetch origin pull/<pr-number>/head:refs/remotes/origin/pr/<pr-number> --force
git worktree add .worktrees/<followup-name> origin/pr/<pr-number>
```

5. If the detached follow-up worktree remains unstable and the original PR branch worktree is clean, remote-matched, and already the PR head branch, it is acceptable to continue in that existing PR worktree for the same PR update. Verify first:

```bash
git -C .worktrees/<existing-pr-branch-wt> status --short --branch
git -C .worktrees/<existing-pr-branch-wt> rev-parse HEAD
git ls-remote origin refs/heads/<pr-branch>
```

Then commit/push to the same PR branch; do not open a second PR.
