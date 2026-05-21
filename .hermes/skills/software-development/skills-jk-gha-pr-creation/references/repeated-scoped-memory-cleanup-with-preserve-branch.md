# Repeated scoped memory/config cleanup with stale preserve branch

Use this reference during repeated `skills-jk` cleanup requests when the user asks for:

- update root `main`
- inspect local changes
- create a PR for `.hermes/config.yaml`, `.hermes/memories/MEMORY.md`, and `.hermes/memories/USER.md`
- clean local branches/worktrees

## Observed pattern

A repeated cleanup turn can differ from the immediately previous one:

1. Earlier follow-up PRs may have merged and their remote branches may be deleted.
2. Root `main` may be behind by those merged commits.
3. The requested scoped files can be mixed:
   - `.hermes/config.yaml` identical to latest `origin/main`
   - `.hermes/memories/MEMORY.md` still carrying one real local diff
   - `.hermes/memories/USER.md` identical in root but a meaningful stale-preserve-branch variant exists
4. A local-only `preserve/*` branch can contain a broad stale diff: useful new skill notes plus old deletion/revert hunks against files now present on latest main.

Do not PR the preserve branch directly.

## Safe workflow

1. Fetch and classify live state:

```bash
git fetch origin --prune
git status --short --branch
git status --short -- .hermes/config.yaml .hermes/memories/MEMORY.md .hermes/memories/USER.md
env -u GITHUB_TOKEN gh pr list --state open --json number,title,headRefName,headRefOid,url
git branch -vv --no-abbrev
git worktree list --porcelain
```

2. For the requested scoped files, compare directly to latest main:

```bash
for p in .hermes/config.yaml .hermes/memories/MEMORY.md .hermes/memories/USER.md; do
  cmp -s "$p" <(git show "origin/main:$p") && echo "$p identical" || echo "$p different"
done
```

3. If only one requested file has a real diff, create a narrow latest-main PR for only that file.

4. If a stale `preserve/*` branch exists, inspect it separately:

```bash
gh pr list --head preserve/<name> --state all --json number,state,mergedAt,url,title
git rev-list --left-right --count origin/main...preserve/<name>
git diff --name-status origin/main..preserve/<name> -- | sed -n '1,160p'
```

5. Promote only meaningful latest-main-portable subsets from the preserve branch:
   - copy or patch new skill/reference files onto fresh latest-main branches
   - preserve durable memory/user preference additions additively, not by replacing unrelated existing preferences
   - drop stale deletion hunks that would remove files already merged into latest main
   - split unrelated subsets into separate narrow PRs

6. After each PR is pushed, verify:

```bash
git ls-remote origin refs/heads/<branch>
gh pr list --head <branch> --state all --json number,state,url,title,headRefOid
```

7. Fast-forward root `main`, re-check open PRs, then delete only stale merged/gone worktrees and branches.

8. Once all meaningful preserve-branch payload has been promoted, delete the stale local-only `preserve/*` branch.

## Reporting

Report separately:

- requested scoped files that were identical and therefore not included
- the actual scoped PR payload, if any
- additional PRs created from meaningful non-scoped residue
- stale merged worktrees/branches removed
- stale preserve branch deleted after promotion
- final root `main` clean/aligned state
