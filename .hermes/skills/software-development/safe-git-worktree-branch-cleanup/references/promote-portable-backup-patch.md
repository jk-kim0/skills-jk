# Promote a portable backup patch during repeated workspace cleanup

Use this reference when a repeated repo-local `workspace 정리` request finds an old `backup/*` branch/worktree that is far behind `origin/main` but still has a small meaningful net patch.

## Signal pattern

- Open PR count is zero or prior follow-up PRs have just merged.
- Root `main` is behind `origin/main` and may show lots of tracked dirt because merged PR content is present in the working tree while local `main` is stale.
- A `backup/*` branch/worktree shows a huge raw `git diff origin/main..<backup>` due to old generated/bundled files.
- Synthetic squash of the backup branch reduces to a small focused diff and rebases cleanly onto latest `origin/main`.

## Safe handling

1. Build a synthetic squash from the backup branch tree and its merge-base:

   ```bash
   base=$(git merge-base origin/main <backup-branch>)
   tree=$(git rev-parse <backup-branch>^{tree})
   squash=$(printf 'TEMP SQUASH %s\n' <backup-branch> | git commit-tree "$tree" -p "$base")
   git diff --stat --find-renames origin/main...$squash --
   ```

2. If the diff is small and rebase was already proven clean, preserve that payload on a fresh branch.

3. Prefer direct patch application first when paths are few:

   ```bash
   git diff --binary origin/main...$squash -- <paths...> > /tmp/payload.patch
   git worktree add -b <new-branch> <new-worktree> origin/main
   git -C <new-worktree> apply /tmp/payload.patch
   ```

4. If `git apply` fails because latest main context drifted, fall back to creating the worktree at the synthetic squash commit, then rebase it:

   ```bash
   git worktree remove --force <new-worktree> || true
   git branch -D <new-branch> || true
   git worktree add -b <new-branch> <new-worktree> $squash
   git -C <new-worktree> rebase origin/main
   git -C <new-worktree> commit --amend -m "<real message>"
   ```

5. Push and verify the remote branch ref:

   ```bash
   git -C <new-worktree> push -u origin <new-branch>
   git ls-remote origin refs/heads/<new-branch>
   ```

6. Only after the payload is preserved remotely, remove the stale old worktree and branch:

   ```bash
   git worktree remove --force <old-worktree>
   git branch -D <backup-branch>
   git reset --hard origin/main
   git worktree prune
   ```

## Reporting

Report three separate facts:

- old backup worktree/branch was removed
- portable payload was preserved on the new branch/PR, with branch SHA/URL if available
- root `main` is now clean and aligned with `origin/main`
