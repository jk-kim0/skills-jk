# skills-jk local sweep: requested subset collapses, other payload survives

Use this reference for repeated `skills-jk` cleanup requests where the user asks to update `main`, inspect local Hermes changes, and create PRs for a named subset such as `.hermes/config.yaml`, `.hermes/memories/MEMORY.md`, and `.hermes/memories/USER.md`.

## Observed session pattern

- Root checkout was dirty/stale while `origin/main` had advanced.
- User explicitly named Hermes config and memory files as requested PR scope.
- After fetching/pruning and comparing against latest `origin/main`, the requested subset had no surviving unique diff:
  - `.hermes/config.yaml`: no unpublished diff
  - `.hermes/memories/MEMORY.md`: apparent diff was already absorbed by latest `origin/main`
  - `.hermes/memories/USER.md`: no unpublished diff
- Other meaningful repo-managed `.hermes/skills/**` and reference-file changes still survived on top of latest `origin/main`.
- Those surviving skill/reference changes were moved to a fresh latest-main worktree/branch and opened as a bot-authored PR via `.github/workflows/create-pr.yml`.
- Root `main` was then restored, fast-forwarded, and cleaned of runtime residue such as `.hermes/kanban.db*`.

## Reusable decision rule

When a named requested subset collapses to no diff on latest `origin/main`, do not manufacture a PR for that subset.
But if the user also asked to inspect local changes generally, continue classifying the remaining local changes and create a separate PR for any meaningful surviving repo-managed payload.

Report these as separate facts:
1. `main` is now aligned to latest `origin/main`.
2. The named requested subset had no surviving unpublished diff.
3. A separate PR was created only for the other surviving payload, with the file list taken from the fresh worktree diff, not the stale root candidate list.
4. Root cleanup was rechecked after PR creation because Hermes/runtime commands can recreate `.hermes/kanban.db*`.

## Verification anchors

Use these checks before final reporting:

```bash
git status --short --branch
git worktree list --porcelain
git branch -vv --no-abbrev
env -u GITHUB_TOKEN gh pr list --state open --json number,title,headRefName,headRefOid,url,author
git ls-remote origin refs/heads/<new-branch>
```

For the requested subset, compare directly against latest main when possible:

```bash
git fetch origin --prune
cmp -s .hermes/config.yaml <(git show origin/main:.hermes/config.yaml) || echo config-diff
cmp -s .hermes/memories/MEMORY.md <(git show origin/main:.hermes/memories/MEMORY.md) || echo memory-diff
cmp -s .hermes/memories/USER.md <(git show origin/main:.hermes/memories/USER.md) || echo user-diff
```
