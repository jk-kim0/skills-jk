# Unregistered `.worktrees/` directories during cleanup

Use this reference when a repo-local cleanup finds directories under `.worktrees/` that do not appear in `git worktree list --porcelain`.

## Why this matters

`git worktree list` only reports linked worktrees known to the root repository. A directory under `.worktrees/` can still be a standalone checkout or nested repository with its own `.git` directory and meaningful dirty work. Treating it as residue and deleting it can lose work.

## Detection

After the normal registered-worktree sweep, also inspect direct children of `.worktrees/`:

```bash
root=$(pwd)
git worktree list --porcelain | awk '/^worktree /{print $2}' | sort > /tmp/registered-worktrees.txt
find "$root/.worktrees" -maxdepth 1 -mindepth 1 -type d -print | sort > /tmp/all-worktrees-dirs.txt
comm -13 /tmp/registered-worktrees.txt /tmp/all-worktrees-dirs.txt
```

For each unregistered directory:

```bash
wt=/absolute/path/to/repo/.worktrees/<name>
if git -C "$wt" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git -C "$wt" status --short --branch
  git -C "$wt" remote -v
  git -C "$wt" branch -vv --format='%(refname:short)%09%(upstream:short)%09%(subject)'
  git -C "$wt" diff --stat
  git -C "$wt" diff --check
fi
```

## Preservation path

If the unregistered checkout has meaningful dirty changes or ahead commits:

1. Do not delete it as empty residue.
2. Commit the meaningful local diff in that checkout.
3. Push explicitly to the real GitHub remote if its `origin` points to the local root repository, for example:
   ```bash
   git -C "$wt" push git@github.com:<owner>/<repo>.git HEAD:refs/heads/<branch>
   ```
4. Open a normal preservation PR with a human-readable title/body.
5. Verify the remote branch head equals the local commit:
   ```bash
   git -C "$wt" rev-parse HEAD
   git -C "$wt" ls-remote git@github.com:<owner>/<repo>.git refs/heads/<branch>
   ```
6. Only after `git status --porcelain` is clean and the commit is present on the remote PR branch, remove the unregistered directory with `rm -rf`/filesystem deletion. Do not use `git worktree remove` for a directory not registered with the root repo.

## Reporting

Final cleanup reports should distinguish:

- registered linked worktrees retained for open PRs;
- unregistered `.worktrees/` directories discovered and either preserved or deleted;
- any preserved PR numbers/URLs created from unregistered directories.
