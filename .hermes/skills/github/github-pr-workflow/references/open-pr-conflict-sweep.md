# Open PR conflict sweep pattern

Use when the user asks to review all open PRs and resolve code conflicts.

## Scan

1. Fetch first:

```bash
git fetch origin --prune
```

2. List open PRs with merge/conflict state, head branch, head SHA, files, and checks:

```bash
env -u GITHUB_TOKEN gh pr list --repo <owner>/<repo> --state open --limit 100 \
  --json number,title,headRefName,baseRefName,headRefOid,mergeStateStatus,mergeable,url,files,statusCheckRollup \
  --jq '.[] | {number,title,headRefName,baseRefName,headRefOid,mergeStateStatus,mergeable,url,files:[.files[].path],checks:[.statusCheckRollup[]? | {name:.name,status:.status,conclusion:.conclusion}]}'
```

Treat `mergeStateStatus=DIRTY` as the primary conflict target. `BLOCKED` may mean required checks/reviews are pending, not a code conflict; verify with `gh pr view <n> --json mergeable,mergeStateStatus,statusCheckRollup` after branch updates.

## Resolve each conflicted PR

1. Use the existing PR worktree if present; otherwise create a repo-local `.worktrees/<branch-flat-name>` worktree from `origin/<headRefName>`.
2. Rebase onto latest `origin/main`:

```bash
git -C <worktree> fetch origin --prune
git -C <worktree> rebase origin/main || true
git -C <worktree> diff --name-only --diff-filter=U
```

3. Resolve conflicts by preserving the intent of merged `origin/main` and reapplying only the open PR's scoped delta. For docs conflicts, do not blindly choose one side; keep newer status/current-state sections from main and integrate the PR's additive section where it now belongs.
4. Verify no conflict markers remain, run lightweight checks, continue the rebase, and force-push with an explicit lease:

```bash
python3 - <<'PY'
from pathlib import Path
for p in [Path(x) for x in '<touched files>'.split()]:
    text = p.read_text()
    if any(m in text for m in ['<<<<<<<','=======','>>>>>>>']):
        raise SystemExit(f'conflict marker remains in {p}')
PY

git diff --check
git add <resolved files>
GIT_EDITOR=true git rebase --continue
old=$(git ls-remote origin refs/heads/<head-branch> | cut -f1)
git push --force-with-lease=refs/heads/<head-branch>:$old origin HEAD:refs/heads/<head-branch>
```

## Important race: main can advance during the sweep

When several PRs are open, `origin/main` can advance while you are resolving another PR (for example, another PR merges). After every rebase/push and before final reporting:

```bash
git fetch origin --prune
git rev-list --left-right --count origin/main...HEAD
```

If the result is not `0 <expected-ahead-count>`, rebase the same PR branch onto the new `origin/main` again and push again. Do not report a PR as conflict-free just because the first rebase succeeded against an older main.

## Final verification

After all pushes, wait briefly for GitHub state refresh, then re-scan all open PRs:

```bash
env -u GITHUB_TOKEN gh pr list --repo <owner>/<repo> --state open --limit 100 \
  --json number,title,headRefName,headRefOid,mergeable,mergeStateStatus,url \
  --jq '.[] | [.number,.mergeStateStatus,.mergeable,.headRefName,.headRefOid,.title,.url] | @tsv'
```

For any PR that still shows `BLOCKED`, run targeted `gh pr view` before assuming conflict remains. The reliable code-conflict terminal state is `mergeable=MERGEABLE` and `mergeStateStatus=CLEAN`.

If the root checkout is on `main` and clean, fast-forward it to `origin/main` at the end so the repository baseline matches the PR scan evidence.
