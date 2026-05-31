# Dirty root behind origin/main preservation during cleanup

Use this when a repo-local `workspace 정리` / `main 업데이트` sweep starts with the root checkout on `main`, local dirty skill/docs/config changes, and `main` behind `origin/main`.

## Durable pattern

`git merge --ff-only origin/main` can fail because local dirty files or untracked files would be overwritten by the fast-forward. Do not stash or discard first. Treat the dirty root as a preservation candidate.

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
   git -C .worktrees/<topic> apply --3way /tmp/<repo>-root-dirty.patch
   ```

4. If `git apply --3way` leaves conflicts, keep the latest-main structure and add only the still-useful local guidance. For skill/library conflicts, this usually means combining compatible `ours` and `theirs` bullets instead of choosing one side wholesale.

5. Copy only meaningful untracked payload into the preservation worktree. Exclude runtime/cache/backups such as `.hermes/lsp/`, `.hermes/pairing/`, profile caches/skills, sessions/logs, `.hermes/skills/.archive/`, and `.hermes/skills/.curator_backups/`.

6. Verify the preservation worktree before commit.
   ```bash
   git diff --check
   git status --short --branch
   ```
   Also scan changed files for real conflict markers with a narrow pattern: `^(<<<<<<<|>>>>>>>)( |$)|^=======$`. Do not broad-scan every line containing `=======`, because skill docs may intentionally contain separators or examples.

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

- Do not report `main` updated while the fast-forward actually failed due to dirty files.
- Do not let a behind-root copy delete guidance already present on latest `origin/main`; preserve latest main and reapply only useful local additions.
- Do not delete untracked skill/reference files from root until the preservation branch has been pushed and the PR head SHA has been verified.
- If all open PRs are merged but root still has new dirty skill guidance, create a new preservation PR before deleting merged branches/worktrees.
