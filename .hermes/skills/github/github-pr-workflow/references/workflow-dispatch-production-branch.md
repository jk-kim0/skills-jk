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
2. Set the deployment branch env to the workflow-dispatch selected ref. Prefer the sibling repo's exact dispatch shape. If the sibling uses a `BRANCH` input with default `main`, keep that contract:

```yaml
on:
  workflow_dispatch:
    inputs:
      BRANCH:
        description: "Branch to Deploy"
        required: true
        default: "main"
        type: "string"

env:
  BRANCH: ${{ inputs.BRANCH }}
  TARGET_ENV: production
```

If the sibling workflow has no branch input and intentionally hardcodes main, keep the hardcode:

```yaml
env:
  BRANCH: main
  TARGET_ENV: production
```

Avoid substituting `${{ github.ref_name }}` when the requested contract is "workflow input branch, default main"; for manual dispatch that expression reflects the workflow run ref, not an explicit deploy-target input.

3. Lower permissions if no remaining step writes repository contents:

```yaml
permissions:
  contents: read
```

4. Preserve repo-specific secrets/vars unless the user explicitly asks to normalize them against a sibling repo.
   - Example: if current repo uses `secrets.VERCEL_TEAM_ID`, do not silently change it to `vars.VERCEL_TEAM_ID` just because a sibling repo does.
5. For sibling-parity requests, leave the deploy script's existing env-reading pattern unchanged unless script changes are explicitly required.
   - If sibling scripts read `process.env.BRANCH` and `process.env.TARGET_ENV`, and pass `branch` to Vercel SDK `gitSource.ref`, do the same.
   - Do not add new `requireEnv`, target allowlist, or target-normalization helpers merely because you are "checking" the script. Such hardening can create preview/secret compatibility failures and diverges from the requested implementation order.
   - Also do not make a previously optional deploy env var mandatory just because it is present in sibling repos. In `corp-web-app`, `VERCEL_TEAM_ID` can be empty in the Preview workflow while Vercel SDK deployment still works without it; adding a hard `requireEnv('VERCEL_TEAM_ID')` can break PR preview deploys even though production workflow changes are correct.
5. If the target behavior is "workflow-selected branch or default main", prefer an explicit `workflow_dispatch.inputs.BRANCH` with `default: "main"` and pass `BRANCH: ${{ inputs.BRANCH }}`. Avoid `${{ github.ref_name }}` for manual production deploys when the desired deploy branch is an operator-selected input rather than the workflow file's checked-out ref.
6. When touching the deploy script as supporting work, keep `gitSource.ref` wired to the workflow-provided branch and add only checks that match current workflow behavior. Validate `VERCEL_TOKEN`, `BRANCH`, and `TARGET_ENV`; validate supported target env strings (`preview`, `staging`, `production`); treat team/project identifiers as repo-specific optional/required based on observed workflows and CI evidence.

## Verification checklist

- `git diff --check`
- `node --check scripts/deploy/index.js` (or the equivalent syntax check) when the deploy script is modified.
- YAML parse or workflow linter when available.
- Grep the production workflow for removed branch-mutation remnants: `release`, `git checkout`, `git push origin release`, and stale `${{ github.ref_name }}` when dispatch input should be authoritative.
- Confirm the PR diff touches only the intended workflow/script files unless the user requested broader supporting changes.
- Verify local branch head, remote branch head, PR head SHA, base branch, and changed file list after PR creation/update.
- If CI fails after adding deploy-script env validation, inspect the failed deploy logs before assuming workflow logic is wrong; empty optional env vars often surface only in Preview workflow logs.
- Report in-progress CI/check status without passively waiting unless the user asked to watch.

## PR body wording

State the final behavior directly:

- Production deploy now uses the branch selected when manually dispatching the workflow.
- The workflow no longer rebases or pushes a `release` branch.
- Repository write permission was lowered to read-only because the workflow no longer mutates branches.
