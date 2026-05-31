# Preserve dirty cleanup payloads by moving them into the right open PR

Use this reference during repo-local `workspace 정리` sweeps when a local worktree is dirty but not itself attached to an open PR.

## Pattern

Sometimes cleanup finds useful local residue in a PR-less branch/worktree while a related open PR already exists. Do not delete the dirty worktree just because it has no PR, and do not automatically open a duplicate PR.

Instead:

1. Identify the owner PR by scope and file paths.
   - Run targeted PR lookup for every local branch.
   - Inspect open PR file lists, not only branch names.
   - If a dirty worktree contains generated/assets/docs that clearly belong to an existing open PR, prefer updating that PR.

2. Preserve the payload in the open PR branch.
   - For ordinary tracked modifications, stage/commit them in the worktree whose branch should back the open PR, or push the dirty worktree HEAD explicitly to the open PR branch if it is the same base.
   - For untracked generated/assets/docs in a separate source worktree, copy only the intended files into the open PR worktree, commit them there, and push to the open PR branch.
   - Use explicit refspecs when branch names differ: `git push origin HEAD:refs/heads/<open-pr-head>`.

3. Align branch/worktree identity when needed.
   - If a local dirty branch was just used to update an open PR head with a different name, rename the local branch to the open PR branch after pushing, set upstream, and remove the duplicate local branch ref.
   - Example sequence:
     ```bash
     git -C <dirty-wt> push origin HEAD:refs/heads/<open-pr-head>
     git -C <repo> branch -D <open-pr-head>  # only if it is a stale duplicate local ref
     git -C <dirty-wt> branch -m <open-pr-head>
     git -C <dirty-wt> branch --set-upstream-to=origin/<open-pr-head>
     ```

4. Verify before deleting the source worktree.
   - If copied untracked files were preserved elsewhere, compare the exact copied file set before force-removing the source worktree.
   - Avoid broad directory comparisons when the destination contains additional sibling content; compare only the file glob that was copied.
   - Example:
     ```bash
     python3 - <<'PY'
     from pathlib import Path
     import filecmp, sys
     src=Path('<source-wt>/docs/brand')
     dst=Path('<open-pr-wt>/docs/brand')
     errors=[]
     for s in sorted(src.glob('*.svg')):
         d=dst/s.name
         if not d.exists():
             errors.append(f'missing {d}')
         elif not filecmp.cmp(s,d,shallow=False):
             errors.append(f'diff {s.name}')
     print('\n'.join(errors) if errors else 'all copied files match')
     raise SystemExit(1 if errors else 0)
     PY
     ```

5. Only then delete the now-redundant dirty source worktree/branch.
   - Use `git worktree remove --force <source-wt>` only after the payload is committed/pushed in the retained branch and file equality was verified.
   - Final cleanup still requires `git worktree prune`, root `git status --short --branch`, `git worktree list`, and a dirty summary over all remaining worktrees.

## Pitfalls

- A PR-less dirty worktree can be the only local copy of useful generated assets or tests; inspect and preserve before deletion.
- If the source and destination directories are not identical by design, a recursive `diff -qr` may fail because of extra destination subdirectories. Compare the intended payload glob instead.
- Do not leave a duplicate local branch name pointing at the same or older commit than an open PR branch; it will confuse later cleanup sweeps.
- If a dirty change extends an existing open PR, updating that PR is usually better than creating a parallel PR for the same scope.
