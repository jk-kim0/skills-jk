---
name: vercel-project-env-parity-copy
description: Copy Vercel project environment variables from a reference project to a target project across production, preview, development, and custom environments such as staging, including sensitive values via vercel env pull.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [vercel, env, secrets, staging, preview, production, api]
---

# Vercel project env parity copy

Use this when a user wants one Vercel project to match another project's environment-variable setup, especially when the source contains both plain and sensitive variables and a custom environment like `staging`.

## When to use

- A new Vercel project should mirror an existing project's runtime env configuration
- A target project has no env vars yet and needs parity with a reference project
- Sensitive env vars must be copied without manually exposing them in chat output
- A custom Vercel environment such as `staging` exists and must be handled separately from `preview`

## Key findings

1. `vercel env ls` shows the env layout, but not always enough structure for exact replication.
2. The Vercel API endpoint `GET /v10/projects/{projectId}/env` returns the exact per-entry structure needed for copying:
   - `key`
   - `type` (`plain` or `sensitive`)
   - `target`
   - `customEnvironmentIds`
3. Sensitive values are not returned by the API.
4. `vercel env pull --environment=preview --git-branch main` is a practical way to inspect values that apply to a custom `staging` environment when that custom environment is matched to the `main` branch.
5. Custom environments do not inherit standard `preview` env vars automatically. If the source project has separate entries with `customEnvironmentIds`, create matching separate entries on the target.
6. Built-in Vercel runtime vars in pulled `.env.*` files should be ignored. Only recreate project-defined vars from the source project's env API listing.
7. Before bulk creation, verify the target project does not already contain env vars, or you may create duplicates/conflicts.
8. Do NOT blindly copy raw values from `vercel env pull` files into another project. Plain vars in pulled files may be shell-quoted, and if you reuse them literally you can poison the target project with values like `"C083Y0300M7"` or `"https://..."`.
9. `vercel env pull` / `vercel env run` are not reliable sources for recovering sensitive secret contents for parity copy. In practice, sensitive vars may appear masked or empty even when they are configured and working in the source project. For sensitive values, use a trusted original source (for example a local `.env` file or another approved secret source) rather than assuming Vercel CLI can reveal them.
10. For target custom environments such as `staging`, `vercel env update <NAME> staging ...` may fail to match existing entries even though they exist in the project.
11. For simple single-variable edits, prefer pure Vercel CLI over Python/API when possible: inspect with `vercel env ls` plus `vercel env pull`, then change with `vercel env rm/add/update`.
12. If one env var is currently shared across multiple targets (for example `Development, Preview, Production, staging`) and you need different values by environment, a reliable CLI-only pattern is:
   - `vercel env rm <NAME>` to remove the shared entry
   - re-add separate entries per target with `vercel env add <NAME> production --value ... --yes`, `development`, and `preview`
   - for a preview-wide value, `vercel env add <NAME> preview "" --value ... --yes` avoids the interactive Git branch prompt and applies to all preview branches
13. In projects where `staging` is a custom environment matched to `main`, `vercel env pull --environment preview --git-branch main` is a practical CLI verification that the staging deployment will see the preview value/override for that branch.

## Prerequisites

Required env in the local shell:

- `VERCEL_TOKEN`
- `VERCEL_TEAM_ID`

Useful tools:

- `vercel`
- Python 3 for API scripting

## Safe workflow

### 1) Inspect both projects

Get both project IDs and inspect custom environments:

```bash
python3 - <<'PY'
import os, json, urllib.request
team=os.environ['VERCEL_TEAM_ID']
token=os.environ['VERCEL_TOKEN']
headers={'Authorization': f'Bearer {token}'}
for pid in ['SOURCE_PROJECT_ID', 'TARGET_PROJECT_ID']:
    url=f'https://api.vercel.com/v9/projects/{pid}?teamId={team}'
    req=urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        data=json.load(r)
    print(json.dumps({
      'name': data['name'],
      'id': data['id'],
      'customEnvironments': data.get('customEnvironments'),
      'link': data.get('link'),
    }, indent=2))
PY
```

Capture the target custom environment ID for `staging` if present.

### 2) Read source env structure

```bash
python3 - <<'PY'
import os, json, urllib.request
team=os.environ['VERCEL_TEAM_ID']
token=os.environ['VERCEL_TOKEN']
pid='SOURCE_PROJECT_ID'
url=f'https://api.vercel.com/v10/projects/{pid}/env?teamId={team}&limit=100'
req=urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as r:
    data=json.load(r)
for e in data['envs']:
    print(json.dumps({
      'key': e['key'],
      'type': e['type'],
      'target': e.get('target'),
      'customEnvironmentIds': e.get('customEnvironmentIds'),
    }))
PY
```

This is the source of truth for what to recreate.

### 3) Pull actual values from the source project

Because API reads do not reveal sensitive values, link a temporary directory to the source project and pull env files.

Production:

```bash
TMP=$(mktemp -d)
vercel link --yes --project SOURCE_PROJECT_NAME --team "$VERCEL_TEAM_ID" --token "$VERCEL_TOKEN" --cwd "$TMP"
vercel env pull "$TMP/.env.production.local" --environment production --token "$VERCEL_TOKEN" --scope "$VERCEL_TEAM_ID" --cwd "$TMP"
```

Preview:

```bash
vercel env pull "$TMP/.env.preview.local" --environment preview --token "$VERCEL_TOKEN" --scope "$VERCEL_TEAM_ID" --cwd "$TMP"
```

Development:

```bash
vercel env pull "$TMP/.env.development.local" --environment development --token "$VERCEL_TOKEN" --scope "$VERCEL_TEAM_ID" --cwd "$TMP"
```

Staging matched to `main`:

```bash
vercel env pull "$TMP/.env.staging.local" --environment preview --git-branch main --token "$VERCEL_TOKEN" --scope "$VERCEL_TEAM_ID" --cwd "$TMP"
```

Parse only the vars you intend to copy. Ignore built-in Vercel vars such as `VERCEL_*`, `TURBO_*`, `NX_DAEMON`.

### 4) Refuse unsafe duplicate creation

Before creating anything on the target, check whether target envs already exist:

```bash
python3 - <<'PY'
import os, json, urllib.request
team=os.environ['VERCEL_TEAM_ID']
token=os.environ['VERCEL_TOKEN']
pid='TARGET_PROJECT_ID'
url=f'https://api.vercel.com/v10/projects/{pid}/env?teamId={team}&limit=100'
req=urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as r:
    data=json.load(r)
print(len(data['envs']))
PY
```

If non-zero, do not blindly create duplicates. Switch to diff/update logic instead.

### 5) Create target envs through the API

For normal targets:

```json
{
  "key": "SALESFORCE_ENDPOINT",
  "value": "...",
  "type": "plain",
  "target": ["production"]
}
```

For custom environments:

```json
{
  "key": "SALESFORCE_ENDPOINT",
  "value": "...",
  "type": "plain",
  "customEnvironmentIds": ["TARGET_STAGING_ENV_ID"]
}
```

POST to:

```text
https://api.vercel.com/v10/projects/{TARGET_PROJECT_ID}/env?teamId={VERCEL_TEAM_ID}
```

## Recommended automation pattern

Use one Python script that:

1. reads source project metadata
2. reads target project metadata
3. reads source env entry structure from API
4. pulls source env values for `production`, `preview`, `development`, and `preview --git-branch main`
5. aborts if the target already has env vars
6. recreates each source env entry on the target, mapping source staging custom-environment ID to target staging custom-environment ID
7. prints only keys/types/targets created, never raw secret values

## Verification

After creation:

```bash
python3 - <<'PY'
import os, json, urllib.request
team=os.environ['VERCEL_TEAM_ID']
token=os.environ['VERCEL_TOKEN']
pid='TARGET_PROJECT_ID'
url=f'https://api.vercel.com/v10/projects/{pid}/env?teamId={team}&limit=100'
req=urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req) as r:
    data=json.load(r)
for e in data['envs']:
    print(json.dumps({
      'key': e['key'],
      'type': e['type'],
      'target': e.get('target'),
      'customEnvironmentIds': e.get('customEnvironmentIds'),
    }))
PY
```

Then test a runtime path that previously failed due to missing env. Example: if a form handler used to return `503` when `SALESFORCE_ENDPOINT` was missing, POST invalid input and confirm it now reaches validation logic instead of config-missing logic.

## Pitfalls

- `vercel env pull` requires a linked local directory; use a temp directory and `vercel link --yes --project ...`.
- `vercel pull` / `vercel env pull` do not support a `--project` flag in this workflow. Link first, then pull.
- Running `vercel env ls` or other CLI env commands from an unlinked repo/worktree can fail with “Your codebase isn’t linked to a project on Vercel.” Prefer API reads or a temp linked directory.
- Before concluding `VERCEL_TOKEN` or `VERCEL_TEAM_ID` is absent, verify which shell is executing the tool command. On macOS/user setups where credentials are exported from `~/.zshrc`, Hermes terminal commands may run under a non-interactive shell that does not load them. Use `zsh -ic '...'` or explicitly source the profile, then re-run the read-only API probe. Report this as a shell-loading issue, not as missing Vercel credentials.
- When checking whether a token is present, print only boolean/length signals such as `${VERCEL_TOKEN:+set}` or `${#VERCEL_TOKEN}`; never print token contents.
- `vercel env pull` downloads built-in Vercel vars too. Do not recreate those in the target project.
- Sensitive vars cannot be read through the env API; if you skip the pull step, you cannot clone them.
- A custom environment like `staging` may not appear via normal preview pulls unless you specify the matching branch.
- The source and target custom environment IDs will differ. Never copy source IDs directly to the target.
- If the target already has env vars, creating all source vars again can duplicate keys across targets or create ambiguous state.

## Evidence to report

- source project name/id
- target project name/id
- target production branch
- target staging branch matcher
- list of env keys created with type and environment placement
- proof that the previously env-blocked runtime path no longer fails for missing configuration
