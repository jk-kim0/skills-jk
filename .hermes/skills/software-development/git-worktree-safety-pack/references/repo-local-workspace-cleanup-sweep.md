# Repo-local workspace cleanup sweep

Use this reference when the user asks for `workspace 정리`, `repo workspace 정리`, or similar cleanup of the current repository.

## Goal

Bring the root checkout to the latest `origin/main`, keep only worktrees/branches that are still useful, and remove stale local branches/worktrees safely. For this user, this means repo-local cleanup only, not a sweep of all `~/workspace`.

## Fast sequence

1. Verify current repo and root status before changing anything:

```bash
pwd
git status --short --branch
git remote -v
```

2. Fetch and fast-forward root `main` when safe:

```bash
git fetch --prune origin
git status --short --branch
git pull --ff-only origin main
```

3. Enumerate worktrees, local branches, and PR bindings:

```bash
git worktree list --porcelain
git branch -vv --format='%(refname:short)%09%(upstream:short)%09%(worktreepath)%09%(committerdate:iso8601)%09%(subject)'
gh pr list --state open --json number,headRefName,title,url,updatedAt
gh pr list --state all --limit 100 --json number,headRefName,state,title,url,mergedAt,closedAt,updatedAt
```

4. Check every worktree for uncommitted/untracked payload before deletion:

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

5. Run targeted PR lookup for local branches. Do not rely only on one broad open-PR query:

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

6. Preserve open-PR worktrees/branches. Delete clean worktrees whose PRs are merged/closed and whose branch is no longer useful. For PR-less branches, first verify net diff against latest main; if `git rev-list --left-right --count origin/main...<branch>` is `0 0` and the worktree is clean, it is a stale branch candidate.

   If a PR-less branch has a meaningful net diff, do not delete it just because no PR exists. Treat cleanup as a preservation opportunity: inspect the diff, rebase the branch/worktree onto latest `origin/main`, push it, and open a narrowly titled PR with a concise Korean body before continuing stale cleanup. This is especially important for agent-created `codex/*` branches that may contain useful docs/design artifacts but were never turned into a PR.

7. Remove stale worktrees before deleting their branches:

```bash
git worktree remove <path>
git branch -D <branch>
git worktree prune
```

8. Remove empty residue directories under `.worktrees/` only after confirming they contain no files.

9. Before final reporting, run one more dirty sweep across every remaining worktree. If a newly opened or updated PR worktree still has related dirty docs/spec/source files, amend and force-with-lease push the same PR branch, then rerun the sweep. Cleanup is not complete until all retained open-PR worktrees are intentionally retained and clean.

10. Final verification should explicitly report:

```bash
git status --short --branch
git worktree list
gh pr list --state open --json number,headRefName,title,url,updatedAt
```

## Reporting expectation

Final report should distinguish:

- root checkout path and branch
- whether root `main` is up to date with `origin/main`
- whether root working tree is clean
- number/kind of stale worktrees/branches removed
- intentionally retained worktrees and their open PR numbers

## Pitfalls

- A branch with upstream marked `[gone]` can still have meaningful local commits or dirty worktree payload; inspect before deleting.
- A branch with no PR can still matter; use net diff vs latest `origin/main` and dirty status before deleting.
- Do not delete open-PR worktrees merely because another PR with the same head branch name was previously merged; targeted lookup may show both a merged historical PR and a current open PR for the same branch name.
- If a repo-local detailed skill-pack index is missing, proceed using this reference and live Git/GitHub state rather than blocking the cleanup.
