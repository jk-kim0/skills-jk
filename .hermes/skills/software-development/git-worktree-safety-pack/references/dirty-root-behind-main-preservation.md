# Dirty root behind origin/main preservation during cleanup

Use this when a repo-local `workspace 정리` / `main 업데이트` sweep starts with the root checkout on `main`, local dirty skill/docs/config changes, and `main` behind `origin/main`.

## Durable pattern

`git merge --ff-only origin/main` or a root `reset` can be blocked or made unsafe by dirty tracked files and untracked files. Do not stash or discard first. Treat the dirty root as a preservation candidate.

1. Fetch and record state.
   ```bash
   git fetch --prune origin
   git status --short --branch
   git rev-parse HEAD origin/main
   git rev-list --left-right --count HEAD...origin/main
   git diff --stat
   git diff --name-status
   git ls-files --others --exclude-standard
   ```

2. Save the root tracked diff and untracked path list outside the repo.
   ```bash
   git diff --binary > /tmp/<repo>-root-dirty.patch
   git ls-files --others --exclude-standard > /tmp/<repo>-untracked.txt
   ```

3. Create a fresh repo-root worktree from latest `origin/main` for the preservation PR.
   ```bash
   git worktree add .worktrees/<topic> -b docs/<topic> origin/main
   ```

4. Do not blindly copy root files into the fresh worktree. A behind-root copy can revert files that changed on latest main. Either apply the root patch with `git apply --3way`, or selectively reapply only the meaningful additions while preserving the latest-main file shape.
   - If a previous preservation PR recently merged, prefer a root-vs-HEAD patch saved before cleanup (`git diff --binary > /tmp/...patch`) plus selected untracked files over an `origin/main` diff. A broad `git diff origin/main` from a stale root can include deletion hunks for files already added by the merged PR.
   - Compare both `git diff HEAD` and `git diff origin/main` before deciding what to preserve. If latest main already contains a related skill/reference change, rebuild the preservation branch from `origin/main` and apply only the still-missing incremental guidance; do not carry forward stale deletions or revert main-side additions.
   - Separate authored guidance/config changes from generated residue. In `skills-jk`, `.hermes/skills/.bundled_manifest` hash churn and bundled-skill script/test style-only rewrites (for example tuple-to-set literal churn) are usually generator/format residue; exclude them unless the user explicitly asked to preserve that generator output.
   - If `git apply --3way` leaves conflicts, resolve them by keeping latest-main canonical content plus the still-relevant root payload, then `git add` the resolved files before final validation. Do not treat marker-free files as resolved until the index no longer shows `UU`.

5. Copy only meaningful untracked payload into the preservation worktree. Exclude runtime/cache/backups such as `.hermes/lsp/`, `.hermes/pairing/`, profile caches/skills, sessions/logs, `.hermes/skills/.archive/`, `.hermes/skills/.curator_backups/`, and generated bundled-skill residue that was not intentionally authored.

6. Verify the preservation worktree before commit.
   ```bash
   git status --short --branch
   git diff --cached --check
   git diff --cached --name-status --find-renames
   ```
   Also scan changed/staged files for real conflict markers with a narrow pattern: `^(<<<<<<<|>>>>>>>)( |$)|^=======$`. Do not broad-scan every line containing `=======`, because skill docs may intentionally contain separators or examples. Confirm the staged diff contains no unintended `D` deletions before commit.

7. Commit, push, and create/update the PR using the repo's normal PR mechanism. Verify the PR head SHA matches the remote branch.

8. Only after PR/remote verification, clean the root checkout:
   ```bash
   git checkout main
   git reset --hard origin/main
   git clean -fd -- .hermes/skills   # or the relevant preserved untracked payload paths
   rm -rf .hermes/lsp .hermes/pairing .hermes/profiles/<profile>/.update_check .hermes/profiles/<profile>/skills .hermes/skills/.archive .hermes/skills/.curator_backups
   ```

9. Continue normal cleanup: delete clean merged worktrees/branches, preserve open PR worktrees, inspect unregistered `.worktrees/` children, and repeat final fetch/dirty-sweep verification.

## Pitfalls

- Do not report `main` updated while the fast-forward actually failed or was skipped due to dirty files.
- Do not let a behind-root copy delete guidance already present on latest `origin/main`; preserve latest main and reapply only useful local additions.
- Do not delete untracked skill/reference files from root until the preservation branch has been pushed and the PR head SHA has been verified.
- If all open PRs are merged but root still has new dirty skill guidance, create a new preservation PR before deleting merged branches/worktrees.
