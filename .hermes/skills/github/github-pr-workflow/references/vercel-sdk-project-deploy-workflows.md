# Vercel SDK project deploy workflows

Use this when adding GitHub Actions workflows that deploy an existing Vercel project via `@vercel/sdk`, especially when matching a sibling repo such as corp-web-japan.

## Pattern

1. Keep the deploy script in a small standalone workspace such as `scripts/deploy/` with its own `package.json` and `package-lock.json`.
2. Use `@vercel/sdk` and `dotenv` only in that deploy workspace.
3. Create deployments with:
   - `name`: the Vercel project name, for example `outbound-dev`.
   - `gitSource.type`: `github`.
   - `gitSource.org`: the GitHub organization.
   - `gitSource.repo`: the repository name.
   - `gitSource.ref`: the branch from workflow env/input.
   - `target`: omit/undefined for preview; set `production` for production.
4. Poll `getDeployment()` until `READY`, treating `QUEUED`, `INITIALIZING`, `ANALYZING`, `BUILDING`, and `DEPLOYING` as in progress.
5. Handle transient Vercel auto-cancel/removal: if polling gets HTTP 404 or final status `CANCELED`, retry once or twice before failing.
6. Validate required env vars in the script (`VERCEL_TOKEN`, `VERCEL_TEAM_ID`, `TARGET_ENV`, `BRANCH`) so misconfigured workflows fail clearly.

## Workflow naming

When one Vercel project has both Preview and Production workflows, make the Actions workflow names visibly distinguish both the target environment and project name:

- `Vercel Preview Deploy (<project-name>)`
- `Vercel Production Deploy (<project-name>)`

Use matching job/step names such as `Deploy Preview to <project-name>` and `Deploy Production to <project-name>`.

## Workflow shape

Preview workflow:

- `pull_request` trigger for `opened`, `synchronize`, and `reopened`.
- Optional `workflow_dispatch` with a `BRANCH` input.
- `BRANCH: ${{ github.event_name == 'pull_request' && github.head_ref || inputs.BRANCH }}`.
- `TARGET_ENV: preview`.
- concurrency group scoped to project + preview + PR number/branch.

Production workflow:

- `workflow_dispatch` only unless the user explicitly asks for automatic production deploys.
- `BRANCH` input with default `main` when the user wants manual branch selection.
- `TARGET_ENV: production`.
- `environment: production` if the repo uses GitHub environment protection.

Both workflows:

- `permissions: contents: read`.
- `defaults.run.working-directory: scripts/deploy`.
- `actions/setup-node` with `cache: npm` and `cache-dependency-path: scripts/deploy/package-lock.json`.
- `npm ci` followed by `npm run deploy`.

## Verification

For workflow-only deploy changes, prefer lightweight static validation:

```bash
git diff --check
node --check scripts/deploy/index.js
python3 - <<'PY'
import pathlib, sys, yaml
for p in pathlib.Path('.github/workflows').glob('*.yml'):
    yaml.safe_load(p.read_text())
    print(f'OK {p}')
PY
actionlint .github/workflows/*.yml
```

After push/PR creation, verify the PR head SHA and that the expected workflow run is attached:

```bash
gh pr view <pr> --json headRefOid,statusCheckRollup
 gh run list --branch <branch> --limit 5 --json workflowName,status,conclusion,headSha,url
```

Do not wait passively for deploy completion unless the user asked you to watch it.
