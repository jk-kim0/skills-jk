# Post-reset skill/reference residue after scoped local sweep

Use this note for repeated `skills-jk` cleanup sessions where the user asks to update `main`, turn scoped Hermes memory/config changes into PRs, and clean the workspace.

Observed pattern:
- The dirty root checkout can initially show a large `.hermes/skills/**` and `.hermes/memories/**` candidate set because local `main` is behind `origin/main`.
- Direct equality checks can show the explicitly requested scoped file (for example `.hermes/config.yaml`) is already identical to latest `origin/main`, while sibling requested files (`.hermes/memories/MEMORY.md`, `.hermes/memories/USER.md`) still have a real diff.
- After creating the narrow scoped PR and resetting root `main` to `origin/main`, additional tracked skill reference files can appear as modified because the current session itself loaded or wrote skill-library content.
- A temporary `preserve/...` branch can be a no-op if the broader candidate set was already absorbed by latest `main`; do not report it as preservation evidence unless it actually has an ahead commit or non-empty diff.

Safe handling:
1. Split requested scoped files from the broader local candidate set before creating the first PR.
2. For named files, compare root file content directly against `origin/main:<path>` after `git fetch --prune`; do not infer from stale root diffs.
3. After pushing and verifying the first PR branch, reset/switch root to latest `origin/main`, then run `git status --short --branch` again.
4. If new tracked skill/reference residue remains:
   - inspect representative diffs before deciding whether it is meaningful;
   - if it is meaningful and the user asked to PR local changes broadly, create a separate narrow PR rather than widening the scoped memory/config PR;
   - if it is stale generated bundle churn, restore it instead of PR-ing a broad revert.
5. Only delete local branches/worktrees after the remote PR branch head is verified with `git ls-remote origin refs/heads/<branch>`.
6. Final report should separate:
   - updated/clean local `main`;
   - the scoped memory/config PR;
   - any additional local-change PR;
   - local cleanup result.

Verification commands:

```bash
git fetch origin --prune
for p in .hermes/config.yaml .hermes/memories/MEMORY.md .hermes/memories/USER.md; do
  if git cat-file -e origin/main:$p 2>/dev/null && test -f "$p"; then
    cmp -s "$p" <(git show origin/main:$p) && echo "$p identical" || echo "$p differs"
  fi
done

git status --short --branch
git diff --name-status origin/main -- .hermes

git rev-parse HEAD
git ls-remote origin refs/heads/<branch>
```
