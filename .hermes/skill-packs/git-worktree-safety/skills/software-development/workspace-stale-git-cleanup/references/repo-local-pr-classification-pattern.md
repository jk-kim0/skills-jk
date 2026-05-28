# Repo-local PR-based stale worktree classification pattern

Pattern observed during corp-web-app cleanup sessions (2026-05-16 ~ 05-18).

## Context

- User says `workspace 정리해줘` while inside a PR-heavy repo
- 100+ worktrees and branches accumulated across many PRs
- Standard Vercel + Next.js + GitHub PR workflow

## Classification flow (works even with 100+ worktrees)

### Step 1: Fetch remote to expose [gone] upstreams

```bash
git fetch --prune origin
```

This is critical: without `--prune`, squash-merged PR branches may still show `[ahead N, behind M]` instead of the correct `[gone]`.

### Step 2: Query open PRs from GitHub

```bash
env -u GITHUB_TOKEN gh pr list --repo <owner>/<repo> \
  --state open --json number,headRefName --limit 100
```

Collect `headRefName` into an `open_branches` set.

### Step 3: Collect all worktrees + local branches

```bash
git worktree list --porcelain   # gives path, HEAD, branch, detached status
git branch -vv                  # gives upstream tracking + [gone] signal
git branch --format '%(refname:short)'   # all local branches
```

### Step 4: Classify each worktree/branch

| Condition | Action | Why |
|---|---|---|
| branch in `open_branches` | **KEEP** | Active PR |
| detached clean (not in any open branch) | **REMOVE** | Helper scratch/work artifact |
| detached dirty | INSPECT | May contain meaningful uncommitted work |
| branch-backed, `[gone]` upstream, clean | **REMOVE** | Merged/closed PR leftover |
| branch-backed, `[gone]` upstream, dirty | INSPECT | May contain uncommitted changes |
| branch-backed, has upstream, not in open PRs, clean | INSPECT | Could be meaningful unpublished branch |

### Step 5: Verify merged state for `[gone]` branches

For `[gone]` branches where branch deletion might fail (`-d` refuses due to non-ancestor merge):

```bash
env -u GITHUB_TOKEN gh pr view <number> --repo <owner>/<repo> --json mergedAt
```

If `mergedAt` is set, `git branch -D <branch>` is safe.

### Step 6: Remove in batches

```bash
git worktree remove --force <path>
git worktree prune
git branch -D <branch>
```

### Step 7: Fast-forward root main

Only after stale items are removed:

```bash
git status --short --branch
git pull --ff-only origin main
```

## Practical signal hierarchy (fastest → slowest)

1. `[gone]` after `fetch --prune` → strong stale signal
2. branch not in open PR list and worktree clean → stale candidate
3. PR `mergedAt` from `gh pr view` → definitive stale confirmation
4. `git diff --stat origin/main..branch` → residual meaningful work check
5. detached helper name pattern (`pr*-rebase`, `*-followup`, `*-assets`) → strong stale signal

## Handling disappearing worktrees

After `git fetch --prune`, some worktrees may already be "orphan" registered paths whose directories no longer exist. Use `git worktree prune` after removals. If a `git worktree remove` fails with "is not a working tree", the worktree may already have been cleaned by a prior operation.

## Dirty detached worktrees

Session finding: most `/private/tmp/` helper worktrees (named `*-assets-*`, `*-audit-*`, `*-mergecheck-*`, `*-rebase-*`) are **clean** and safe to remove. If one is dirty, it warrants brief inspection before deletion.
