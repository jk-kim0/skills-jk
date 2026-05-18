# Workflow-dispatch production branch deployment

Use this reference when a manual GitHub Actions production deploy workflow should deploy the branch selected in `workflow_dispatch` directly, rather than creating/updating a separate `release` branch.

## Recognition pattern

Existing workflow often contains:

```yaml
permissions:
  contents: write

on:
  workflow_dispatch:

jobs:
  deploy:
    env:
      BRANCH: release
      TARGET_ENV: production
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Rebase release onto main and push
        run: |
          git fetch origin main release
          git checkout release
          git pull origin release
          git rebase origin/main
          git push origin release
```

And the deployment script uses `BRANCH` as the provider git source ref, e.g. Vercel SDK `gitSource.ref`.

## Migration recipe

1. Remove the release-branch mutation step entirely.
   - Delete `git fetch/checkout/pull/rebase/push release` and any `fetch-depth: 0` kept only for that step.
   - Do not keep a hidden branch-promotion phase if the requested behavior is direct deployment of the selected branch.
2. Set the deployment branch env to the workflow-dispatch selected ref:

```yaml
env:
  BRANCH: ${{ github.ref_name }}
  TARGET_ENV: production
```

3. Lower permissions if no remaining step writes repository contents:

```yaml
permissions:
  contents: read
```

4. Preserve repo-specific secrets/vars unless the user explicitly asks to normalize them against a sibling repo.
   - Example: if current repo uses `secrets.VERCEL_TEAM_ID`, do not silently change it to `vars.VERCEL_TEAM_ID` just because a sibling repo does.

## Verification checklist

- `git diff --check`
- YAML parse or workflow linter when available.
- Confirm the PR diff touches only the intended workflow file unless the user requested supporting script changes.
- Verify local branch head, remote branch head, PR head SHA, base branch, and changed file list after PR creation.
- Report in-progress CI/check status without passively waiting unless the user asked to watch.

## PR body wording

State the final behavior directly:

- Production deploy now uses the branch selected when manually dispatching the workflow.
- The workflow no longer rebases or pushes a `release` branch.
- Repository write permission was lowered to read-only because the workflow no longer mutates branches.
