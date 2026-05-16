# skills-jk local sweep: squash-merged PR worktree cleanup

Use this reference when a repeated `skills-jk` cleanup request lands after the prior follow-up PR was squash-merged and its remote branch was deleted, while the agent is still inside the old PR worktree.

## Observed session pattern

- Current cwd was the old PR worktree:
  - `.worktrees/hermes-config-update-20260516`
  - branch `update/hermes-config-and-skills-20260516`
- `gh pr status` reported the current branch's PR as `MERGED`.
- `git fetch --prune` removed `origin/update/hermes-config-and-skills-20260516`.
- Root `main` was behind `origin/main` by the squash merge commit.
- The PR head SHA was **not** an ancestor of `origin/main`, because GitHub used squash merge.
- `git diff origin/main...<pr-head>` misleadingly listed the full PR payload because the merge-base was before the PR, even though the final tree was already absorbed.
- `git diff origin/main <pr-head>` was empty, and scoped blob IDs for `.hermes/config.yaml`, `.hermes/memories/MEMORY.md`, and `.hermes/memories/USER.md` matched.

## Reusable decision rule

For merged PR cleanup after squash merge, ancestry and triple-dot diff are not enough.

Use all of these instead:

```bash
git fetch origin --prune
env -u GITHUB_TOKEN gh pr view <pr> --json state,mergedAt,headRefName,headRefOid,mergeCommit,url

git diff --name-status origin/main <pr-head-sha>
for f in .hermes/config.yaml .hermes/memories/MEMORY.md .hermes/memories/USER.md; do
  a=$(git rev-parse origin/main:"$f")
  b=$(git rev-parse <pr-head-sha>:"$f")
  test "$a" = "$b" && echo "equal $f" || echo "different $f"
done
```

If the two-dot/tree diff is empty and the user-named scoped files match, treat the old worktree/branch as stale historical residue, not unpublished work.

## Safe cleanup sequence

Run cleanup from the root checkout, not from inside the stale worktree:

```bash
ROOT=/path/to/skills-jk
WT="$ROOT/.worktrees/<old-worktree>"

git -C "$ROOT" fetch origin --prune
git -C "$ROOT" reset --hard origin/main

git -C "$WT" status --short  # must be empty before removal
git -C "$ROOT" worktree remove "$WT"
git -C "$ROOT" branch -D <old-branch>

rm -f "$ROOT/.hermes/kanban.db" "$ROOT/.hermes/.gitignore.swp"
git -C "$ROOT" status -sb
git -C "$ROOT" worktree list --porcelain
git -C "$ROOT" branch -vv
```

## Reporting

Report three facts separately:

1. The previous PR was already merged, so no new PR was needed for the same payload.
2. `main` was fast-forwarded/reset to the merge commit on latest `origin/main`.
3. The stale PR worktree/branch and local runtime residue were removed, leaving root `main` clean.
