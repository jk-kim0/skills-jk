# Repo-local workspace cleanup sweep

Use this reference when the user asks for `workspace 정리`, `repo workspace 정리`, or similar cleanup of the current repository.

## Goal

Bring the root checkout to the latest `origin/main`, keep only useful local worktrees/branches, preserve meaningful work that has not reached a PR yet, and remove stale local residue safely. For this user, this means repo-local cleanup only, not a sweep of all `~/workspace`.

## Required behavior

1. Start with a short estimate/status in Korean, then act immediately.
2. Work from the current repository root and do not modify the root checkout except to fast-forward `main`.
3. Fetch and fast-forward root `main` before classification.
4. Classify every local branch with targeted `gh pr list --state all --head <branch>` lookups, not only one broad open-PR list.
5. Check every worktree for dirty/untracked content before deletion.
6. Preserve open PR branches/worktrees.
7. Preserve PR-less branches if they have meaningful net diff or dirty content: inspect the diff, rebase onto latest `origin/main`, push, and open a narrow PR rather than deleting.
8. Delete clean worktrees/branches whose PRs are merged/closed, and delete PR-less clean branches only when `origin/main...<branch>` is `0 0`.
9. Run final verification loops until root `main` is current, retained worktrees are clean, unregistered `.worktrees/` directories have been inspected/preserved/deleted deliberately, and `.worktrees/` has no empty residue directories.

## Fast command sequence

```bash
pwd
git status --short --branch
git remote -v
git fetch --prune origin
git merge --ff-only origin/main

git worktree list --porcelain
git branch -vv --format='%(refname:short)%09%(upstream:short)%09%(worktreepath)%09%(committerdate:iso8601)%09%(subject)'
gh pr list --state open --json number,headRefName,title,url,updatedAt
```

Targeted branch-to-PR lookup:

```bash
git for-each-ref --format='%(refname:short)' refs/heads | while read -r b; do
  json=$(gh pr list --state all --head "$b" --json number,state,title,url,mergedAt,closedAt --limit 20)
  python3 - "$b" "$json" <<'PY'
import sys,json
b=sys.argv[1]
data=json.loads(sys.argv[2])
if not data:
    print(f'{b}\tNO_PR')
else:
    print(f'{b}\t' + '; '.join('#{} {} {}'.format(p['number'], p['state'], p['title']) for p in data))
PY
done
```

Dirty sweep:

```bash
git worktree list --porcelain | awk '
  /^worktree /{if(path){print path "\t" branch}; path=$2; branch=""}
  /^branch /{branch=$2; sub("refs/heads/", "", branch)}
  END{if(path){print path "\t" branch}}
' | while IFS=$'\t' read -r path branch; do
  printf '%s\t%s\t' "$branch" "$path"
  dirty=$(git -C "$path" status --porcelain)
  if [ -z "$dirty" ]; then printf 'clean\n'; else printf 'DIRTY\n%s\n' "$dirty"; fi
done
```

Unregistered `.worktrees/` directory sweep:

```bash
git worktree list --porcelain | awk '/^worktree /{print $2}' | sort > /tmp/registered-worktrees.txt
find "$(pwd)/.worktrees" -maxdepth 1 -mindepth 1 -type d -print | sort > /tmp/all-worktree-dirs.txt
comm -13 /tmp/registered-worktrees.txt /tmp/all-worktree-dirs.txt | while read -r d; do
  echo "--- unregistered $d"
  git -C "$d" status --short --branch || true
  git -C "$d" remote -v || true
  git -C "$d" diff --stat || true
done
```

If this finds a standalone checkout or nested repo with meaningful work, use `references/unregistered-worktrees-during-cleanup.md` before deleting it.

Net diff counts:

```bash
git for-each-ref --format='%(refname:short)' refs/heads | while read -r b; do
  printf '%s\t' "$b"
  git rev-list --left-right --count origin/main..."$b" || true
done
```

## Deletion rules

Safe deletion candidates:

- branch has no open PR and all matching PRs are `MERGED` or `CLOSED`, and its worktree is clean;
- branch has no PR, worktree is clean, and `git rev-list --left-right --count origin/main...<branch>` is `0 0`.

Delete worktree before branch:

```bash
git worktree remove <path>
git branch -D <branch>
git worktree prune
```

Remove empty residue directories under `.worktrees/` only after checking they contain no files:

```bash
for d in .worktrees/*; do
  [ -d "$d" ] || continue
  if [ -z "$(find "$d" -mindepth 1 -print -quit)" ]; then
    rmdir "$d"
  fi
done
```

## Preservation rules for PR-less work

If a branch has no PR but has dirty content or meaningful net diff:

1. Inspect `git diff --stat`, key file diffs, and missing linked files.
2. If the change is meaningful, stage and commit it in that worktree.
3. Rebase onto current `origin/main`.
4. Push the branch.
5. Create a PR with Korean title/body and no auto-closing issue keywords.
6. Verify the PR URL and branch head.
7. Continue stale cleanup.

For docs splits, verify that newly referenced docs actually exist before opening the PR. If a changed document links to a new file that was not created, recover the missing content from the pre-split document or otherwise create the linked file so the PR is self-contained.

## Preservation PR hygiene

When preserving PR-less dirty work during cleanup, keep the preservation PR reviewer-friendly and avoid creating duplicate scope:

- Inspect whether the dirty branch is a previously merged PR branch before opening a new PR. If its remaining dirty files overlap a newly preserved PR or are already represented by an open preservation PR, remove the stale merged branch/worktree instead of creating another duplicate PR.
- If an existing open preservation PR already covers the dirty root/worktree's scope, update that PR branch instead of creating a duplicate PR.
- Use a human-readable Korean PR title/body that describes the actual scope, not a mechanical branch-name dump. Avoid shell/JSON escaping that can leak `\\uXXXX` sequences into GitHub titles.
- After creating a preservation PR, immediately re-check the former dirty source branch/worktree. If the source branch was a merged branch used only as a temporary holding area, delete it once the preserved PR is verified.
- If preserving multiple PR-less branches in one sweep, re-run the open PR list and targeted branch lookup after each preservation PR so later branches are classified against the new open PRs, not stale state.

## Open PR rebase repair during cleanup

If an open PR branch becomes non-clean after `origin/main` advances, treat it as part of the cleanup sweep rather than only reporting the dirty merge state:

1. Confirm the PR is still open and the branch worktree is clean before rewriting history.
2. Rebase the PR branch onto the latest `origin/main` instead of merging `main` into the branch.
3. For documentation conflicts caused by a recently merged sibling PR, resolve main-side canonical structure first, then re-apply only the still-relevant PR-specific delta so stale duplicate sections do not return.
4. Re-run `git diff origin/main...HEAD` or targeted file diffs to confirm the branch still contains its intended scope and no unrelated conflict residue.
5. Immediately before force-pushing, re-check `gh pr view <n> --json state,mergedAt,headRefName,headRefOid` and `git ls-remote origin refs/heads/<branch>`. If the PR has merged/closed or the remote branch is gone, stop and clean up the local worktree/branch instead of pushing; otherwise a cleanup run can accidentally recreate a branch that GitHub already deleted after merge.
6. Push with `--force-with-lease`, then re-check the PR merge state and status checks.
7. Do not merge or close the PR during cleanup unless the user explicitly asks.

## Final stability loop

Cleanup can race with other agents or merges. After deleting stale worktrees/branches, rebasing an open PR branch, or pushing a preservation PR, repeat this loop until stable:

1. `git fetch --prune origin`
2. `git merge --ff-only origin/main` in the root checkout if root is `main` and clean.
3. Re-run open PR list and targeted branch lookup.
4. Re-run dirty sweep for every remaining worktree.
5. If a retained open-PR worktree has related dirty files, amend/commit and push to that same PR, then repeat.
6. If `origin/main` advanced and formerly open PRs are now merged, remove their clean worktrees/branches.
7. If a branch has no PR but a dirty worktree or meaningful ahead diff, do not stop at classification. Inspect the diff and either preserve it by committing/pushing/opening a PR, or explicitly delete it only when it is clean and equivalent to `origin/main`.
8. Remove empty `.worktrees/` residue directories.
9. Inspect direct child directories under `.worktrees/` that are not registered by `git worktree list`. If one is a standalone checkout with dirty or ahead work, preserve it by committing/pushing/opening a PR before deleting the directory; see `references/unregistered-worktrees-during-cleanup.md`.

When the user asks to wait and repeat the open-PR/cleanup sweep, the post-wait run must still perform cleanup actions, not merely print a classification report. After the delayed pass finishes, immediately follow up on any newly merged PR branches, newly opened PR branches, and newly discovered PR-less dirty worktrees before giving the final answer.

Final report should include root path/branch, whether `main` is up to date, root clean status, stale items removed, intentionally retained worktrees with PR numbers, newly preserved PR-less work if any, and the final `git status --short --branch`.