# Behind-root stale deletion hunks during local sweep PR creation

Use this note when a `skills-jk` root checkout is dirty and behind `origin/main`, and the user asks to update main, inspect local changes, create a PR, and clean the workspace.

## Failure mode

A dirty root checkout can be one or more commits behind `origin/main`. If you copy tracked files directly from that root into a fresh latest-main worktree, the file content may be older than the latest main version plus local edits. In the fresh worktree this appears as deletion hunks that would revert recently merged guidance.

Typical symptoms:

- `git status -sb` in root shows `main...origin/main [behind N]` plus tracked edits.
- After copying files into a fresh `origin/main` worktree, `git diff` shows both desired additions and unexpected deletions of lines that exist on latest main.
- The deleted lines may be unrelated to the current local-sweep payload, for example profile cleanup guidance or E2E naming guidance that just landed upstream.

## Safe handling

1. Create the PR worktree from latest `origin/main` as usual.
2. Copy candidate files from the dirty root checkout into the worktree.
3. Inspect representative diffs before staging, especially for `.hermes/skills/**` files.
4. Treat unexpected deletions of latest-main guidance as stale root residue, not as intentional local changes.
5. Restore or manually re-add the latest-main lines so the final PR contains only the surviving additive/local guidance.
6. Run `git diff --check`, commit, push, and create the bot PR.
7. Only after the branch head is verified on the remote, restore/remove the same root-local changed files and fast-forward root `main`.

## Verification commands

```bash
git -C <fresh-worktree> diff --stat
git -C <fresh-worktree> diff -- <candidate-files>
git -C <fresh-worktree> diff --check
git -C <fresh-worktree> diff --name-only origin/main...HEAD | sort
```

If a deletion hunk is kept intentionally, the PR body should explain why. Otherwise, remove it before commit so the cleanup PR does not silently downgrade the skill library.
