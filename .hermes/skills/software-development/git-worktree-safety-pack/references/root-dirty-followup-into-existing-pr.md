# Root dirty follow-up into an existing preservation PR

Use this when a repo-local `main 업데이트` / `workspace 정리` sweep starts with root `main` cleanly at `origin/main` but dirty from newly generated authored skill/docs guidance, while an existing open preservation PR already covers the same local-guidance bucket.

## Pattern

1. Do not create a duplicate PR just because root is dirty again.
   - Re-list open PRs and run targeted branch lookup for every local branch.
   - If an open PR branch already covers the same guidance/config bucket, update that PR branch.

2. Separate authored payload from runtime residue.
   - Preserve tracked `.hermes/memories/**`, `.hermes/skills/**`, repo-tracked profile/config changes, and intentionally authored `references/**` files.
   - Exclude runtime/cache/dependency residue such as `.hermes/lsp/**`, node_modules, logs, sessions, caches, and generated package-locks unless the user explicitly asks to track them.

3. Prefer patch application over blind file copying when the open PR branch already changes some of the same files.
   - Naively copying root files into the PR worktree can overwrite earlier PR-only changes in overlapping `SKILL.md` files.
   - Safer sequence:
     ```bash
     # in root, collect authored paths excluding runtime residue
     python3 - <<'PY'
     from pathlib import Path
     import subprocess
     root = Path.cwd()
     tracked = subprocess.check_output(['git','diff','--name-only'], text=True).splitlines()
     untracked = subprocess.check_output(['git','ls-files','--others','--exclude-standard'], text=True).splitlines()
     auth = [p for p in tracked + untracked if not p.startswith('.hermes/lsp/')]
     if untracked:
         subprocess.run(['git','add','-N','--'] + [p for p in untracked if not p.startswith('.hermes/lsp/')], check=True)
     patch = subprocess.check_output(['git','diff','--binary','--'] + auth)
     Path('/tmp/root-authored.patch').write_bytes(patch)
     subprocess.run(['git','reset','--mixed','--'] + [p for p in untracked if not p.startswith('.hermes/lsp/')], check=False)
     print(len(auth), 'authored paths')
     PY

     # in the open PR worktree
     git reset --hard origin/<open-pr-branch>
     git clean -fd -- .hermes/skills .hermes/memories
     git apply --3way /tmp/root-authored.patch
     ```

4. Resolve documentation conflicts by preserving both sides when both are class-level guidance.
   - Common conflict shape: an existing PR added one top-level section while the new root diff adds another top-level section near the same anchor.
   - Resolve by keeping both sections, deduplicating headings, and removing conflict markers.
   - For numbered pitfall lists, merge unique bullets and renumber once.

5. Verify before commit/push.
   - Run a narrow conflict-marker scan on touched markdown:
     ```bash
     python3 - <<'PY'
     from pathlib import Path
     bad=[]
     for p in Path('.').glob('.hermes/**/*.md'):
         for i,line in enumerate(p.read_text(errors='ignore').splitlines(),1):
             if line.startswith('<<<<<<<') or line.startswith('>>>>>>>') or line == '=======':
                 bad.append(f'{p}:{i}:{line}')
     print('\n'.join(bad) if bad else 'no conflict markers')
     PY
     ```
   - Run `git diff --check`.
   - Amend the existing PR commit and push with `--force-with-lease`.
   - Update the existing PR body to reflect the expanded scope.

6. Clean root only after verifying the PR branch remote head.
   - `git ls-remote origin refs/heads/<branch>` must match local PR worktree `HEAD`.
   - Then reset root to `origin/main` and clean only preserved authored paths plus excluded runtime residue:
     ```bash
     git reset --hard origin/main
     git clean -fd -- .hermes/lsp .hermes/memories .hermes/skills
     ```

7. Final report verification should prove both preservation and cleanup.
   - Re-query the PR with at least `number,state,title,url,headRefName,headRefOid,baseRefName,baseRefOid,mergeStateStatus,statusCheckRollup,files`.
   - If `statusCheckRollup` is empty, report it explicitly as "checks: none" rather than implying pending or green checks.
   - Run a final registered-worktree and residue sweep: `git status --short --branch`, `git worktree list --porcelain`, direct children of `.worktrees/`, and root untracked files.
   - Keep the open PR worktree intentionally; cleanup is complete when root `main` is clean/up to date and only retained open-PR worktrees remain.

## Pitfalls

- A dirty root at `origin/main` can still contain meaningful authored guidance; do not discard it just because main is not behind.
- Do not preserve `.hermes/lsp/node_modules/**` or similar runtime residue in a docs/skill PR.
- Do not use direct copy as the first strategy when the existing open PR branch has already modified overlapping files; it can silently delete earlier PR-only additions.
- A successful force-push is not enough: re-query the PR head SHA and run one more retained-worktree dirty sweep before reporting cleanup complete.
- Do not delete a clean retained worktree just because workspace cleanup is requested if it is the live worktree for an open preservation PR; report it as intentionally retained.
