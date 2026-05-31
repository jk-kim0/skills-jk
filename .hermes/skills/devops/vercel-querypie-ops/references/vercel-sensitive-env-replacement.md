# Vercel sensitive env replacement and verification

Use this reference when rotating or replacing sensitive environment variables in a Vercel project, especially OAuth client credentials.

## Durable lessons

- Treat OAuth client secrets or provider tokens pasted into chat/logs as exposed. Regenerate the upstream secret and replace all deployment copies after smoke, or immediately if the value is no longer needed.
- Vercel env changes affect new deployments only. After changing runtime env, trigger or wait for a fresh deployment before testing behavior that reads those values.
- For Vercel `sensitive` env vars, `vercel env update <KEY> <target>` may fail with an error like `You cannot change the key of a Sensitive Environment Variable`. A safe replacement pattern is remove then add the same key for the intended target.
- Do not trust a mutating CLI command by itself. Verify key presence, target, and type through a fresh project env listing/API response before reporting completion.
- If CLI add/update behavior and listing disagree, use the Vercel Project Env API directly and verify again.

## Safe replacement pattern

```bash
# Run from a linked project directory, or pass --cwd/--scope as needed.
# Never print values in logs.
printf '%s' "$NEW_VALUE" | vercel env remove <KEY> production --yes >/dev/null
printf '%s' "$NEW_VALUE" | vercel env add <KEY> production --sensitive >/dev/null

printf '%s' "$NEW_VALUE" | vercel env remove <KEY> preview --yes >/dev/null
printf '%s' "$NEW_VALUE" | vercel env add <KEY> preview --sensitive >/dev/null
```

If the key may not exist, a failing remove can be acceptable only after confirming the failure is `not found`; still require the subsequent add and final verification.

## Verification shape

```bash
vercel api /v10/projects/<project-id>/env --scope <team> |
  jq -r '.envs[] | [.key, (.target|join(",")), .type] | @tsv' |
  sort
```

Report only key/target/type presence. Do not print values.

Example expected shape for an OAuth-backed Gmail smoke environment:

```text
GMAIL_OAUTH_CLIENT_ID         production/preview sensitive
GMAIL_OAUTH_CLIENT_SECRET     production/preview sensitive
GMAIL_OAUTH_STATE_SECRET      production/preview sensitive
GMAIL_TOKEN_ENCRYPTION_SECRET production/preview sensitive
```
