# Vercel sensitive env replacement for Gmail OAuth

Captured from an Outbound Agent Gmail OAuth setup session where Vercel `querypie/outbound-dev` needed `GMAIL_OAUTH_CLIENT_ID` and `GMAIL_OAUTH_CLIENT_SECRET` replaced for Production and Preview.

## Durable pattern

1. Keep secrets out of logs, docs, PR bodies, and chat summaries.
2. For sensitive Vercel env vars, try the narrow target mutation but verify afterward with the Project Env API.
3. Treat `vercel api /v10/projects/<project-id>/env --scope <team>` or equivalent list output as source of truth, not only the `vercel env add/update` success message.
4. Existing deployments do not pick up env changes retroactively; redeploy after env mutation before OAuth smoke.

## Useful verification command

```bash
vercel api /v10/projects/<project-id>/env --scope <team> \
  | jq -r '.envs[] | select(.key|startswith("GMAIL_")) | [.key, (.target|join(",")), .type] | @tsv' \
  | sort
```

Expected evidence shape:

```text
GMAIL_OAUTH_CLIENT_ID      preview      sensitive
GMAIL_OAUTH_CLIENT_ID      production   sensitive
GMAIL_OAUTH_CLIENT_SECRET  preview      sensitive
GMAIL_OAUTH_CLIENT_SECRET  production   sensitive
GMAIL_OAUTH_STATE_SECRET   preview      sensitive
GMAIL_OAUTH_STATE_SECRET   production   sensitive
GMAIL_TOKEN_ENCRYPTION_SECRET preview    sensitive
GMAIL_TOKEN_ENCRYPTION_SECRET production sensitive
```

## CLI/API quirks observed

- `vercel env update <key> <target> --sensitive` can fail for existing sensitive keys with `You cannot change the key of a Sensitive Environment Variable`.
- Remove + add can work for Production-scoped sensitive keys.
- A Preview-scoped `vercel env add <key> preview --sensitive` may print success but still be absent from API/list output. If so, create the Preview key with the Project Env API JSON body and verify again.
- `vercel link` from a worktree can create an app-local `.gitignore` such as `front/.gitignore`; remove it if the repository owns ignore rules at the root, and add `/front/.vercel/` to the intended ignore file.

## JSON body shape for API creation

```json
{
  "key": "GMAIL_OAUTH_CLIENT_ID",
  "value": "<secret-or-client-id>",
  "type": "sensitive",
  "target": ["preview"]
}
```

Invoke with a temp file and do not echo the value:

```bash
vercel api /v10/projects/<project-id>/env --scope <team> -X POST --input /tmp/vercel-env.json
```
