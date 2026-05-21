# Multi-bucket root residue PR split during skills-jk cleanup

Use this reference when a dirty root `main` contains several unrelated `.hermes/skills/**` updates and the user asks to validate local branches/worktrees against latest main and open PRs for meaningful residue.

## Observed pattern

A single root dirty checkout can contain multiple valid payload buckets at once:

1. files that belong to an existing open PR branch
2. files that are a coherent new docs/skill note PR
3. additional skill/reference files that only become obvious after the first transplant/PR pass
4. stale deletion hunks caused by root `main` being behind latest `origin/main`
5. merged worktree residue that can be deleted only after all meaningful root dirt is preserved

Do not reset root `main` after the first successful PR. Re-run `git status --short --branch` and classify the remaining tracked/untracked files until the root checkout is genuinely clean or all remaining dirt is intentionally excluded.

## Safe sequence

1. Fetch and inspect live state:
   - `git fetch origin --prune`
   - `git status --short --branch`
   - `git branch -vv --no-abbrev`
   - `git worktree list --porcelain`
   - `env -u GITHUB_TOKEN gh pr list --state open --json number,title,headRefName,headRefOid,url`
2. Split root dirty paths by scope before copying:
   - Existing open PR scope: copy into that PR worktree, amend/commit, push, and verify remote SHA.
   - New coherent scope: create a fresh `.worktrees/<topic>` branch from latest `origin/main` and copy only that bucket.
   - Unclear/newly revealed scope: inspect representative diffs before deciding whether to create another small PR.
3. In each fresh latest-main worktree, inspect residual diff before commit:
   - `git status --short --branch`
   - `git diff --stat`
   - `git diff --check`
   - representative `git diff` output
4. Drop stale deletion hunks that are only artifacts of an old root checkout.
   - If copying a root file would delete guidance already present on latest `origin/main`, restore that file from `origin/main` in the fresh worktree and reapply only the still-valid block.
5. After every PR push, verify preservation before touching root:
   - `git ls-remote origin refs/heads/<branch>` equals local `HEAD`
   - `gh pr list --head <branch> --state all ...` shows the expected PR
6. Before resetting root or deleting stale worktrees, run one more root status loop.
   - If more meaningful tracked/untracked `.hermes/skills/**` files appear, split them into an existing open PR or another narrow PR.
   - Only reset root after all meaningful local files are represented by verified remote branches/PRs.
7. Then remove merged residue worktrees/branches after a fresh PR-state check.

## Reporting

Report these as separate facts:

- existing open PRs updated
- new PRs created, with branch/commit/URL and payload file list
- stale worktrees/branches deleted, with merged/gone evidence
- root `main` alignment and cleanliness
- any open PRs whose GitHub `mergeStateStatus` is `BLOCKED` but `statusCheckRollup` is empty; do not call that a CI failure without attached checks
