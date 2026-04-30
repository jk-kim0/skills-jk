---
name: vercel-project-git-branch-settings
description: Inspect and change a Vercel project's linked Git production branch safely, including the unlink/relink workaround required when direct updates do not change link.productionBranch.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [vercel, github, deployment, branch, api]
---

# Vercel project git branch settings

Use this when you need to verify or change which Git branch a Vercel project treats as its production branch.

## When to use

- A repository is moving from `release` to `main`
- Vercel production deploys still reference an old branch
- You need to confirm whether Vercel project settings, not just GitHub Actions, still depend on a branch

## Core findings

1. `vercel.json` can have `git.deploymentEnabled: false` and the Vercel project may still retain a linked Git repo with `link.productionBranch` set.
2. `vercel project inspect` does not necessarily show `productionBranch`.
3. `vercel target ls` shows branch tracking, but running it in an unlinked worktree can create/link a `.vercel` project for that directory. Do not use it casually in a fresh worktree.
4. `vercel project inspect --yes` can also create/link a local `.vercel` directory when the repo is not already linked. Treat it as a side-effecting inspection command and clean up `.vercel/` afterward if you only needed read-only inspection.
5. Direct project PATCH attempts like `PATCH /v9/projects/{id}` with `productionBranch` or `link.productionBranch` are rejected.
5. Re-POSTing to `/v9/projects/{id}/link` with `productionBranch` while already linked can return 200 without actually changing `link.productionBranch`.
6. Reliable workaround: unlink the repo, then relink the same GitHub repo. The relink resets `link.productionBranch` to the repo default branch (for GitHub repos, usually `main`).

## Safe inspection steps

Prereqs: `VERCEL_TOKEN` and `VERCEL_TEAM_ID` available in env.

Get the project id:

```bash
vercel project inspect <project-name>
```

Inspect full project JSON via API:

```bash
python3 - <<'PY'
import json, os, urllib.request
project='prj_xxx'
team=os.environ['VERCEL_TEAM_ID']
token=os.environ['VERCEL_TOKEN']
url=f'https://api.vercel.com/v9/projects/{project}?teamId={team}'
req=urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as r:
    data=json.load(r)
print(json.dumps({
  'link': data.get('link'),
  'customEnvironments': data.get('customEnvironments'),
  'targets': data.get('targets'),
}, indent=2, ensure_ascii=False))
PY
```

Important fields:
- `link.productionBranch`
- `customEnvironments[].branchMatcher`
- recent `targets.production.meta.githubCommitRef`

Check whether recent production deployments used `release`:

```bash
vercel list <project-name> --environment production --status READY --format json
```

Look at:
- `meta.githubCommitRef`
- `meta.branchAlias`

## Failed approaches to avoid

These did not work for an already-linked project:

```text
PATCH /v9/projects/{id} with {"productionBranch":"main"}
PATCH /v9/projects/{id} with {"link":{"productionBranch":"main"}}
PATCH /v9/projects/{id}/link with productionBranch
POST  /v9/projects/{id}/link with productionBranch while already linked
```

The POST may return success but not change `link.productionBranch`.

## Working branch-change procedure

If the goal is to switch the linked production branch to the repo default branch (`main`):

```bash
python3 - <<'PY'
import json, os, urllib.request
project='prj_xxx'
team=os.environ['VERCEL_TEAM_ID']
token=os.environ['VERCEL_TOKEN']
base=f'https://api.vercel.com/v9/projects/{project}/link?teamId={team}'
headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 1) unlink
req=urllib.request.Request(base, method='DELETE', headers=headers)
with urllib.request.urlopen(req) as r:
    print('DELETE', r.status)

# 2) relink same repo
body=json.dumps({'type':'github','repo':'owner/repo'}).encode()
req=urllib.request.Request(base, data=body, method='POST', headers=headers)
with urllib.request.urlopen(req) as r:
    print('POST', r.status)
PY
```

Then verify:

```bash
python3 - <<'PY'
import json, os, urllib.request
project='prj_xxx'
team=os.environ['VERCEL_TEAM_ID']
token=os.environ['VERCEL_TOKEN']
url=f'https://api.vercel.com/v9/projects/{project}?teamId={team}'
req=urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as r:
    data=json.load(r)
print(data.get('link', {}).get('productionBranch'))
PY
```

Expected result:

```text
main
```

## Release-branch retirement checklist

After switching to `main`:

1. Update GitHub Actions workflows to deploy from `main`
2. Verify Vercel `link.productionBranch == 'main'`
3. Confirm staging/custom environments still have the intended `branchMatcher`
4. Check recent production deployments for lingering `githubCommitRef: release`
5. Delete remote `release` branch if no longer needed:

```bash
git ls-remote origin refs/heads/release
git push origin --delete release
env -u GITHUB_TOKEN gh api repos/<owner>/<repo>/branches/release
```

Interpretation:
- empty `git ls-remote` output = deleted
- GitHub API returns 404 = deleted

## Pitfalls

- Running `vercel target ls --yes` in a fresh worktree can create/link a local `.vercel` project for that directory name. Remove accidental `.vercel/` afterward if it is unrelated.
- Do not assume a successful API response changed `link.productionBranch`; always re-read the project JSON.
- `git.deploymentEnabled: false` does not mean the project has no linked Git branch metadata.
- Keep track of the old remote branch SHA before deleting `release`.

## Evidence to collect in reports

- old `link.productionBranch`
- new `link.productionBranch`
- old `release` SHA
- confirmation that `customEnvironments` still match intended branches
- confirmation that remote `release` is gone
