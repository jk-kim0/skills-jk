---
name: vercel-production-branch-audit
description: Audit whether a repository still depends on a Vercel production tracking branch (for example `release`) after GitHub Actions or manual deploy workflows are changed to main-only.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [vercel, github-actions, deployment, branch-strategy, audit]
    related_skills: [github-pr-workflow]
---

# Vercel Production Branch Audit

Use this when a repo is migrating away from a `release` branch and you need to verify whether Vercel still references it.

## Why this skill exists

Changing GitHub Actions alone is not enough. A repo can stop using `release` in workflow YAML while Vercel still has:
- a linked Git production branch set to `release`
- old production deployments created from `release`
- branch aliases that still reflect `release`

This creates a false sense that the migration is complete when it is only partially complete.

## When to use

- User asks whether `release` is still needed
- You changed deploy workflows from `release` to `main`
- You need to compare GitHub Actions behavior vs Vercel project behavior
- You suspect production deployments are still sourced from an old branch

## Audit flow

### 1. Check repository-side references first

Inspect workflows and scripts:

```bash
search_files(path=<repo>, pattern="release", target="content")
search_files(path=<repo>/.github/workflows, pattern="release", target="content")
```

Also check whether the remote branch still exists:

```bash
git branch -a | grep -E '(^release$|origin/release$)' || true
```

And whether there are open PRs based on it:

```bash
env -u GITHUB_TOKEN gh pr list --state open --search "head:release" --json number,title,url,headRefName,baseRefName
```

### 2. Check local Vercel config

Read `vercel.json`:

```bash
read_file(path="vercel.json")
```

Important finding:
- `"git": { "deploymentEnabled": false }` only disables Vercel git-triggered deployments
- it does **not** prove the linked Vercel project no longer tracks `release`

Do not stop here.

### 3. Confirm Vercel CLI access

```bash
vercel --version
printenv | grep -E '^VERCEL_' || true
vercel project inspect <project-name>
```

If the repo is linked and authenticated, continue to direct API inspection.

### 4. Query the Vercel project link settings directly

Use the Vercel REST API because `vercel project inspect` may not show the production branch clearly.

```bash
python3 - <<'PY'
import json, os, urllib.request
project='<project_id>'
team=os.environ['VERCEL_TEAM_ID']
token=os.environ['VERCEL_TOKEN']
url=f'https://api.vercel.com/v9/projects/{project}?teamId={team}'
req=urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as r:
    data=json.load(r)
print(json.dumps(data.get('link'), indent=2, ensure_ascii=False))
PY
```

The key field to inspect is:
- `link.productionBranch`

If it says `release`, Vercel still considers `release` the production tracking branch.

### 5. Inspect recent production deployments

```bash
vercel list <project-name> --environment production --status READY --format json
```

Look at deployment metadata fields:
- `meta.githubCommitRef`
- `meta.branchAlias`

Useful API form for summarizing refs:

```bash
python3 - <<'PY'
import json, os, urllib.request
project='<project_id>'
team=os.environ['VERCEL_TEAM_ID']
token=os.environ['VERCEL_TOKEN']
url=f'https://api.vercel.com/v6/deployments?projectId={project}&teamId={team}&target=production&limit=20'
req=urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as r:
    data=json.load(r)
items=[]
for d in data.get('deployments', []):
    meta=d.get('meta') or {}
    items.append({
        'url': d.get('url'),
        'ref': meta.get('githubCommitRef'),
        'branchAlias': meta.get('branchAlias')
    })
print(json.dumps(items[:10], indent=2, ensure_ascii=False))
print('release_refs=', sum(1 for x in items if x.get('ref')=='release'))
print('main_refs=', sum(1 for x in items if x.get('ref')=='main'))
PY
```

## Interpretation rules

### Case A — GitHub Actions no longer use `release`, but Vercel still does

This means the migration is incomplete.

Report clearly:
- GitHub Actions side: `release` dependency removed
- Vercel project side: `release` still configured or still visible in deployment metadata
- Conclusion: do **not** say `release` is fully unnecessary yet

### Case B — Vercel `link.productionBranch=release`, but new production deploys are manually forced from another branch

This can happen when GitHub Actions call Vercel directly with an explicit branch/ref.

Interpretation:
- Vercel default tracking branch is stale
- actual recent deploy source may differ
- cleanup is still recommended so defaults match reality

### Case C — No workflow references, no Vercel project reference, no recent deployment refs

Then you can safely say `release` appears unused and can likely be removed, subject to branch protection or human process checks.

## Recommended final answer structure

1. Repo/workflow status
2. Vercel project setting status
3. Recent production deployment evidence
4. Bottom-line conclusion
5. Optional next step: update Vercel production branch to `main`

## Pitfalls

- Do not assume `vercel.json` tells you the linked production branch
- Do not assume old deployment history means the branch is still actively used now
- Do not assume workflow cleanup alone finishes the migration
- `vercel project inspect` may omit the critical branch field; use the API when needed
- Production deployments can show refs other than the default tracking branch if they were created explicitly by API/workflow
