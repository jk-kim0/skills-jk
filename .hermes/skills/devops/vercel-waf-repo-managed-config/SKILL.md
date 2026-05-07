---
name: vercel-waf-repo-managed-config
description: Manage Vercel WAF custom rules as a repo-committed source of truth, using vercel api for query/apply and documenting the operational caveats around first-time setup.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [vercel, waf, firewall, security, runtime-logs, operations]
---

# Vercel WAF as repo-managed config

Use this when a user wants Vercel Firewall / WAF custom rules stored in git, reviewed via PR, and applied later with `vercel api`.

## When to use

- "Store Vercel WAF rules in this repo"
- "Create a PR with firewall rules and docs"
- "Reduce runtime-log probe noise by blocking at the edge"
- "Document how to query and apply Vercel WAF config"

## Key findings

### 1. For probe suppression, edge `deny` is the practical outcome

If the user's goal is to stop runtime-visible 404 noise from probe paths, the clean approach is to block them in Vercel WAF before they reach the app runtime.

Important implication:
- `deny` returns `403 Forbidden` at the edge
- the request does **not** reach the hosting runtime
- this reduces runtime-log 404 noise, but does **not** preserve 404 for those probe paths

Be explicit about this tradeoff in the PR and README.

### 2. There is no simple repo-native `vercel.json` WAF config format

For custom WAF rules, use a committed JSON source-of-truth file that matches the Firewall API payload, then apply it with:

```bash
vercel api '/v1/security/firewall/config?projectId=<project_id>&teamId=<team_id>' \
  --scope <team-slug> \
  -X PUT \
  --input <path-to-json>
```

This is simpler for repo storage than introducing Terraform unless the repo already uses Terraform for Vercel resources.

### 3. First query can legitimately return `404 Config not found`

Querying the active firewall config with:

```bash
vercel api '/v1/security/firewall/config/active?projectId=<project_id>&teamId=<team_id>' --scope <team-slug> --raw
```

can return:
- `404 Config not found`

before the first successful custom config `PUT`.

Interpretation:
- this usually means no active custom firewall config exists yet
- do **not** assume the project lookup failed

Document this caveat so operators do not misread it.

### 4. Full-file `PUT` is safer than ad hoc `PATCH` for repo workflows

For a git-reviewed setup, prefer:
- committed full JSON config
- PR review
- full `PUT` apply

Why:
- keeps one authoritative source of truth in git
- avoids dashboard/API drift from partial emergency edits

But warn clearly:
- a full `PUT` can overwrite dashboard-only WAF edits not reflected in the repo
- if managed rulesets or IP rules are enabled later, add them to the committed file before the next `PUT`

## Recommended repo layout

Example:

```text
ops/vercel-firewall/
  README.md
  <project>.firewall.json
```

Recommended contents:
- `README.md`: query, apply, rollback, and caveats
- `<project>.firewall.json`: full Firewall API payload

## JSON payload shape

A minimal useful file can look like:

```json
{
  "firewallEnabled": true,
  "managedRules": {},
  "ips": [],
  "rules": [
    {
      "name": "Deny exploit probes",
      "description": "Block obvious exploit paths at the edge.",
      "active": true,
      "conditionGroup": [
        {
          "conditions": [
            { "type": "path", "op": "pre", "value": "/wp-admin/" }
          ]
        },
        {
          "conditions": [
            { "type": "path", "op": "pre", "value": "/.git/" }
          ]
        }
      ],
      "action": {
        "mitigate": {
          "action": "deny"
        }
      }
    }
  ]
}
```

Condition notes:
- each `conditionGroup` entry is OR'd with the others
- conditions inside a single group are AND'd
- useful path ops here are `eq`, `pre`, and when really needed `re`
- practical finding: Vercel WAF path matching documents regex (`re`) but does not document glob-style wildcard operators, so do not assume patterns like `/*/.env` or `/**/*.json` are supported

## Rule-count strategy on Pro

Practical pricing finding:
- Pro currently allows up to `40` custom firewall rules

Important operational interpretation:
- the meaningful limit is the number of custom rules, not the number of path conditions inside one rule
- therefore, it is usually better to group many related path conditions into a few operationally clear rules than to create one tiny rule per path

Recommended grouping pattern:
- one rule per noise family, for example:
  1. frontend/config discovery probes
  2. API/health probes
  3. env/secret file probes
  4. exploit/scanner prefixes

Why this works well:
- preserves large headroom under the Pro rule limit
- keeps review intent obvious
- avoids unnecessary regex/wildcard compression when explicit `eq` and `pre` conditions are already readable

Compression guidance:
- do not switch to regex only to reduce conditions inside a rule if the custom rule count is already low
- for example, several nested `.env` probe paths kept inside one existing env-probe rule do not materially pressure the Pro rule limit
- prefer explicit exact-path and prefix conditions unless the path list becomes large enough that readability clearly improves with a carefully scoped regex

## Query / apply / inspect commands

### Query active config

```bash
vercel api '/v1/security/firewall/config/active?projectId=<project_id>&teamId=<team_id>' \
  --scope <team-slug> --raw | jq .
```

### Apply committed config

```bash
vercel api '/v1/security/firewall/config?projectId=<project_id>&teamId=<team_id>' \
  --scope <team-slug> \
  -X PUT \
  --input ops/vercel-firewall/<project>.firewall.json
```

### Inspect firewall-side events

```bash
vercel api '/v1/security/firewall/events?projectId=<project_id>&teamId=<team_id>&limit=50' \
  --scope <team-slug> --raw | jq .
```

### Validate local JSON before apply

```bash
jq . ops/vercel-firewall/<project>.firewall.json >/dev/null
```

## Practical pattern for probe-noise reduction

When runtime logs are dominated by obvious bot/scanner probes, group them into a small number of WAF rules, for example:

1. frontend/config discovery probes
2. API/health probes
3. env/secret file probes
4. exploit/scanner prefixes

Examples of good prefix blocks:
- `/.env`
- `/wp-admin/`
- `/.git/`
- `/.ssh/`

Examples of good exact-path blocks:
- `/swagger.json`
- `/openapi.json`
- `/api/health`
- `/health`
- `/runtime-config.js`

## Workflow

1. Confirm Vercel project identifiers:
   - team slug
   - team ID
   - project name
   - project ID
2. Create a fresh branch/worktree.
3. Add `ops/vercel-firewall/README.md` and `<project>.firewall.json`.
4. Explain that `deny` means edge 403, not runtime 404.
5. Validate the JSON with `jq`.
6. Open PR.
7. After merge, apply with `vercel api ... -X PUT --input ...` from clean `main`.
8. Re-query active config and inspect firewall events.
9. Verify one blocked probe path externally and confirm it no longer appears in runtime logs.

## Post-apply verification pattern

After applying the config, verify one concrete blocked path such as `/.git/config`:

```bash
curl -sS -D - -o /tmp/probe-body.txt 'https://<production-domain>/.git/config' | sed -n '1,40p'
```

Expected edge-deny signs:
- HTTP status `403`
- `server: Vercel`
- `x-vercel-mitigated: deny`

Then immediately check recent runtime logs for the same path:

```bash
vercel logs --project <project-name> --environment production --since 10m --json --no-branch --limit 200
```

Filter for the tested `requestPath` and confirm the match count is `0`.

Interpretation:
- if the external request returns `403` with `x-vercel-mitigated: deny`
- and the same path is absent from recent runtime logs
- then the request is being stopped at the edge before it reaches the hosting runtime, which is the intended outcome for probe-noise reduction

## Pitfalls

- Assuming WAF rules should live in `vercel.json`
- Assuming query `404 Config not found` means the project is wrong
- Forgetting that `deny` changes the response from runtime 404 to edge 403
- Using full `PUT` without documenting that dashboard-only rules can be overwritten
- Forgetting to preserve `managedRules` / `ips` in the committed file if they later become non-empty
