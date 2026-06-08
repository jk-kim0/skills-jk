# Stacked PR base refresh before commit

Use when working on a stacked PR whose base is another open PR branch.

## Problem

The parent PR branch can move while the child/stacked PR worktree has uncommitted edits. If you commit from the stale parent head, the child PR may include outdated parent commits or be harder to review/rebase.

## Pattern

Immediately before committing or pushing, re-check the parent/base branch:

```bash
git fetch origin <base-branch>
git status --short --branch
git rev-parse HEAD origin/<base-branch>
git log --oneline --left-right --graph HEAD...origin/<base-branch> --max-count=20
```

If the stacked worktree is behind the parent branch while local edits are uncommitted, preserve and replay the diff on the latest parent head:

```bash
PATCH=/tmp/<topic>.patch
git diff --binary > "$PATCH"
git reset --hard origin/<base-branch>
git apply --3way "$PATCH"
```

Then rerun the targeted verification because the base changed, commit, push the child branch, and create/update the PR with `--base <base-branch>`.

## Notes

- Prefer doing this before the first commit on the stacked branch; it avoids rewriting an already-created child commit.
- If conflicts occur during `git apply --3way`, resolve them like a normal rebase/merge conflict, then rerun focused tests.
- This is a workflow pattern, not a claim about any specific PR or branch.
