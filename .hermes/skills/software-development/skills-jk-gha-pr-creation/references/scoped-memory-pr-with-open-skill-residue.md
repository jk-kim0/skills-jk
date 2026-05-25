# Scoped memory PR with concurrent open skill-residue PR

Use this when the user repeatedly asks in `skills-jk` to update `main`, inspect local changes, make a PR for Hermes config/memory files, and clean the workspace, while an open skill-library residue PR already exists.

## Pattern

1. Refresh refs and inspect root before changing anything:
   ```bash
   git status --short --branch
   git diff --name-status
   git ls-files --others --exclude-standard
   git fetch origin --prune
   ```

2. Classify the requested scoped files directly against latest `origin/main`:
   ```bash
   for p in .hermes/config.yaml .hermes/memories/MEMORY.md .hermes/memories/USER.md; do
     cmp -s "$p" <(git show "origin/main:$p") && echo "$p identical" || echo "$p different"
   done
   ```

3. If one scoped file has a real diff, create a narrow latest-main PR for only that scoped file.
   - Example: if only `.hermes/memories/MEMORY.md` differs, create a fresh worktree/branch from `origin/main`, copy only that file, commit, push, and create the bot PR through `.github/workflows/create-pr.yml`.
   - In the PR body, explicitly list the scoped files that are unchanged/identical so reviewers understand why they are absent.

4. Keep unrelated `.hermes/skills/**` residue out of the scoped memory/config PR.
   - If an existing open skill-residue PR already owns this class of cleanup (for example `docs/local-skill-residue-notes`), update that PR instead of opening a duplicate.
   - Apply tracked root deltas to the PR worktree using `git apply --3way`.
   - Copy only genuinely new untracked support files/directories.
   - Amend the existing single cleanup commit and force-with-lease push.
   - Update the PR body to state that the real scoped memory change is handled in the separate PR.

5. After each root restore, re-run root status before fast-forwarding main.
   - Restoring the obvious tracked files can reveal additional untracked skill directories.
   - If they belong to the same skill-residue cleanup scope, amend the same skill PR again rather than leaving root dirty or creating another tiny PR.

6. Only fast-forward root `main` after the root checkout is clean.
   ```bash
   git status --short --branch
   git merge --ff-only origin/main
   git worktree prune
   ```

## Verification

- Scoped PR payload contains only the requested changed scoped file(s).
- Skill-residue PR payload contains only `.hermes/skills/**` skill/reference files.
- Both remote branch heads match local heads after push/force-push:
  ```bash
  git rev-parse HEAD
  git ls-remote origin refs/heads/<branch>
  ```
- `git diff --check` passes in each PR worktree.
- Conflict-marker scan passes over touched memory/skill files.
- Final root `main` is clean and aligned to `origin/main`.

## Reporting rule

Report the work as separate facts:

- which scoped config/memory files were identical vs changed;
- the PR number/URL for the real scoped memory/config payload;
- whether skill-library residue was added to an existing open skill PR instead of creating a duplicate;
- the final root `main` and worktree/branch cleanup state.
