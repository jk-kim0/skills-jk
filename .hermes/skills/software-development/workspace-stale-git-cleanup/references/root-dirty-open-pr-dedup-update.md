# Dirty root changes that overlap an existing open PR

Use this when repo-local cleanup/main-update starts with meaningful dirty files in the protected root `main` checkout, and an existing open PR already covers part or all of the same skill/docs payload.

## Pattern

1. Fetch/prune and inspect root status before changing anything:
   ```bash
   git fetch origin --prune
   git status --short --branch
   git diff --stat
   git diff --name-status
   gh pr list --state open --json number,title,headRefName,url,headRefOid
   ```
2. Build two sorted file inventories:
   - root meaningful files: tracked diff plus untracked authored files, excluding runtime/cache residue such as `.hermes/lsp/` and `.hermes/kanban.db-*`.
   - existing PR diff files: `git diff --name-only origin/main...<open-pr-branch>`.
3. Compare them with `comm` or equivalent.
   - If the PR file list is a subset of the dirty root payload, do **not** create a duplicate PR. Update the existing PR branch/worktree instead.
   - If the overlap is partial but the topic is clearly the same follow-up skill/docs preservation payload, still prefer updating the existing PR after verifying it is open and clean.
4. Preserve a safety backup before copying root state:
   ```bash
   BACKUP=/tmp/<repo>-root-local-$(date +%Y%m%d-%H%M%S)
   mkdir -p "$BACKUP"
   git diff --binary > "$BACKUP/tracked.diff"
   <meaningful-file-list> > "$BACKUP/files.txt"
   tar -czf "$BACKUP/meaningful-files.tgz" -T "$BACKUP/files.txt"
   ```
5. Rebase the open PR worktree/branch onto latest `origin/main` before copying files.
6. Copy only meaningful files from root into the PR worktree; exclude runtime/cache residue.
7. Run `git diff --check`, commit, and push the existing PR branch.
8. Verify:
   - worktree `HEAD` equals `git ls-remote origin refs/heads/<branch>`.
   - PR `headRefOid` equals the pushed commit.
   - PR file list matches the intended meaningful payload.
9. After verified preservation, clean the root copies and runtime residue so root `main` is clean and still equals `origin/main`.
10. Continue stale worktree/branch cleanup, removing merged PR worktrees/branches only after PR state is verified.

## Pitfall

Do not satisfy “local changes are meaningful, create a PR” by blindly opening a new PR when an existing open PR is already a subset of the local dirty payload. In skill-library repos this creates duplicate preservation PRs and leaves root cleanup ambiguous. Update the existing open PR unless the root-only files clearly belong to a separate topic.
