# Root checkout on stale merged branch with dirty authored payload

Use this when a repo-local `main 업데이트` / `workspace 정리` sweep starts with the root checkout not on `main`, the branch's PR is already merged/closed, and the root contains dirty authored skill/docs/config changes plus runtime residue.

## Durable pattern

A stale merged root branch can still contain meaningful uncommitted work. Do not delete or reset it just because the branch PR is merged. Preserve authored payload first, then return root to clean `main`.

1. Fetch and classify the root branch before cleanup.
   ```bash
   git fetch --prune origin
   git status --short --branch
   git rev-parse --abbrev-ref HEAD
   gh pr list --state all --head "$(git rev-parse --abbrev-ref HEAD)" --json number,state,title,url,mergedAt,closedAt
   git rev-list --left-right --count HEAD...origin/main
   git diff --stat
   git diff --name-status
   git ls-files --others --exclude-standard
   ```

2. Treat dirty authored files as a preservation candidate even when the branch's PR is already merged. Save payload outside the repo:
   ```bash
   git diff --binary > /tmp/<repo>-root-dirty.patch
   git ls-files --others --exclude-standard | grep -v '^\.hermes/lsp/' > /tmp/<repo>-untracked.txt
   ```
   Exclude runtime/cache residue such as `.hermes/lsp/`, sessions, logs, pairing, archives, and curator backups.

3. Create a fresh repo-root worktree from latest `origin/main` with a new preservation branch.
   ```bash
   git worktree add .worktrees/<topic> -b docs/<topic> origin/main
   ```

4. Apply the tracked root patch with `git apply --3way`, then copy only meaningful untracked authored files into the preservation worktree. Do not copy the stale root tree wholesale; it can reintroduce already-merged/stale hunks or delete latest-main files.

5. Stage the intended skill/docs/config payload and verify before commit:
   ```bash
   git add <authored paths>
   git diff --cached --check
   git grep -n -E '^(<<<<<<<|>>>>>>>)( |$)|^=======$' -- $(git diff --cached --name-only --diff-filter=ACMR)
   git diff --cached --name-status | awk '$1=="D"{print}'
   ```
   Resolve whitespace/conflict-marker/deletion findings before committing.

6. Commit, push, and create the PR using the repo's normal mechanism. For skills-jk, prefer `.github/workflows/create-pr.yml` via `workflow_dispatch` and verify the PR by head branch after the workflow completes.

7. Only after PR head verification, clean the root checkout:
   ```bash
   git reset --hard
   git clean -fd <runtime-residue-and-preserved-untracked-paths>
   git checkout main
   git merge --ff-only origin/main
   ```

8. Delete the stale root branch after switching to `main`, then continue normal worktree cleanup and final dirty sweeps.

## Pitfalls

- A merged PR branch at the root can still have uncommitted authored follow-up files. Preserve those files into a new latest-main PR instead of treating the branch as disposable.
- `git clean -fd .hermes/skills` after PR verification is safe only when the newly added untracked authored files have been copied, committed, pushed, and PR-verified on the preservation branch.
- Keep the final report explicit: root is now `main`, root is clean/current, one preservation PR worktree remains, and stale merged/closed worktrees/branches were removed.
