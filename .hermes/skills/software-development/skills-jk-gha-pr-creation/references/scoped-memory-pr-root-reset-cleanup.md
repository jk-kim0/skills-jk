# Scoped memory/config PR followed by root reset cleanup

Use this when the user asks in `skills-jk` to update `main`, turn local Hermes config/memory changes into a PR, and clean the workspace.

## Situation

The root checkout is on `main`, behind `origin/main`, and dirty with a mix of:
- requested scoped files such as `.hermes/config.yaml`, `.hermes/memories/MEMORY.md`, `.hermes/memories/USER.md`
- broad generated `.hermes/skills/**` residue
- stale local branches whose upstream PR branches were already deleted after merge

## Safe pattern

1. Fetch first.
   - `git fetch origin --prune`

2. Classify the requested scoped files by direct equality against `origin/main`, not by root `git status` alone.
   - `cmp -s <file> <(git show origin/main:<file>)`
   - For missing top-level names like `MEMORY.md` / `USER.md`, explicitly report `ABSENT_BOTH` if neither local nor remote has them.

3. Distinguish local dirt from remote advancement.
   - `git diff HEAD..origin/main -- .hermes/memories/USER.md`
   - If a scoped file differs only because `origin/main` already has a newer entry, do not copy the stale local file into the PR.

4. Create a fresh latest-main worktree for the real surviving scoped payload.
   - `git worktree add .worktrees/<topic> -b <branch> origin/main`
   - Copy only the scoped file(s) that still differ from `origin/main`.
   - Verify the worktree diff before commit.

5. Commit, push, and create the PR through `.github/workflows/create-pr.yml`.
   - Verify PR payload with `gh pr view <branch> --json files,headRefOid`.
   - Verify remote branch ref with `git ls-remote origin refs/heads/<branch>`.

6. Only after the PR branch is safely pushed and verified, clean root `main`.
   - If broad `.hermes/skills/**` residue is not part of the requested PR and representative diffs show generated/stale bundle churn, reset root main to latest remote:
     - `git reset --hard origin/main`
   - This is safe only after the scoped payload is preserved on the pushed PR branch.

7. Delete stale merged local branches whose upstream refs are gone.
   - Confirm with `gh pr list --state all --head <branch>` showing `MERGED`.
   - Then `git branch -D <branch>`.

8. Final verification.
   - Root `git status --short --branch` is clean.
   - `git rev-parse HEAD origin/main` matches.
   - Remaining worktrees are only active PR worktrees.

## Reporting notes

Report these as separate facts:
- which requested scoped files became PR payload
- which scoped files were unchanged or only differed because remote main was newer
- that broad skill residue was discarded from root after scoped PR preservation
- stale merged local branches deleted
- final root `main` clean/aligned status
