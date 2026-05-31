# Outbound Agent Gmail OAuth env setup notes

Use this reference when configuring Gmail OAuth/client secrets for `querypie/outbound-agent` development deployments, especially issue/status work around Gmail actual send readiness.

## Scope

This note covers the operational pattern learned while configuring these environments:

- `dev-vercel`: Vercel project `querypie/outbound-dev`
- `dev-seoul`: Tencent VM `outbound-seoul.dev.querypie.io`
- `dev-tokyo`: Tencent VM `outbound-tokyo.dev.querypie.io`

Do not write OAuth client secrets, token encryption secrets, refresh tokens, or generated state secrets into repo files, issue comments, PR bodies, or assistant replies.

## Required app env keys

The app currently expects these Gmail OAuth env vars:

```text
GMAIL_OAUTH_CLIENT_ID
GMAIL_OAUTH_CLIENT_SECRET
GMAIL_TOKEN_ENCRYPTION_SECRET
GMAIL_OAUTH_STATE_SECRET
```

`GMAIL_OAUTH_STATE_SECRET` falls back to the token encryption secret in code, but set it explicitly for deployed environments when doing operational setup.

## Google OAuth redirect URIs to verify

For the Outbound Agent dev surfaces, check that the OAuth client accepts all relevant callback URLs:

```text
http://localhost:3000/api/gmail/oauth/callback
https://outbound-dev.vercel.app/api/gmail/oauth/callback
https://outbound-seoul.dev.querypie.io/api/gmail/oauth/callback
https://outbound-tokyo.dev.querypie.io/api/gmail/oauth/callback
```

A low-impact verification pattern is to call the Google OAuth authorization endpoint with each `redirect_uri` and check that the returned HTML/redirect does not contain `redirect_uri_mismatch` or `invalid_client`. Reaching the Google login/consent flow is enough for URI/client validation; it does not complete OAuth or send email.

## Vercel env pitfall and workaround

`vercel env add <name> preview` may prompt for a preview Git branch even with `--yes`, and stdin/value injection can return exit code 0 without saving the variable if the branch prompt is not answered as expected.

Safer pattern for all-preview-branches env insertion:

1. Use `vercel env add <name> production --force --sensitive --yes` for production.
2. For preview, verify with the Vercel API after insertion.
3. If the CLI prompt prevents reliable preview insertion, use Vercel API directly:

```bash
vercel api /v10/projects/<project_id>/env \
  --method POST \
  --input /path/to/body.json \
  --scope querypie \
  --silent
```

Example JSON shape, with the actual value only in a temporary 0600 file:

```json
{
  "key": "GMAIL_OAUTH_CLIENT_ID",
  "value": "<secret-or-id>",
  "type": "sensitive",
  "target": ["preview"]
}
```

Then verify via:

```bash
vercel api /v10/projects/<project_id>/env --scope querypie --raw
```

Check only key/target/type metadata in outputs; do not print secrets.

## Vercel redeploy caveat

Adding Vercel env vars does not change already-built deployments. After production env insertion, run a production redeploy from the repository root, not from `front/`, because the Vercel project root directory is already `front` and running inside `front/` can resolve to `front/front`.

```bash
cd /path/to/outbound-agent
vercel deploy --prod --scope querypie --yes
```

Verify the final alias and `/login` health:

```bash
curl -I https://outbound-dev.vercel.app/login
```

## Tencent VM pattern

The VM service reads `/etc/outbound-agent/front.env` via the container systemd unit. Preserve existing env lines and replace only the Gmail keys.

Recommended approach:

1. Generate per-VM token/state secrets with `openssl rand -base64 32`.
2. Copy a temporary env fragment to the VM without printing values.
3. On the VM, filter existing `front.env` with `grep -v -E '^(GMAIL_OAUTH_CLIENT_ID|GMAIL_OAUTH_CLIENT_SECRET|GMAIL_TOKEN_ENCRYPTION_SECRET|GMAIL_OAUTH_STATE_SECRET)='`.
4. Append the new fragment, install as `/etc/outbound-agent/front.env` with `root:root 600`.
5. `sudo systemctl daemon-reload` if unit files changed or systemd warns, then `sudo systemctl restart outbound-front`.
6. Verify both the file keys and running container env presence without printing values.

If the FQDN SSH route resolves to an internal `100.64.x.x` address and resets, use the documented public IPs from `infra/dev-seoul/README.md` and `infra/dev-tokyo/README.md` for SSH, then keep public HTTPS verification on the FQDN.

Verification commands should output only names/presence:

```bash
systemctl is-active outbound-front
sudo sh -c 'grep -E "^(GMAIL_OAUTH_CLIENT_ID|GMAIL_OAUTH_CLIENT_SECRET|GMAIL_TOKEN_ENCRYPTION_SECRET|GMAIL_OAUTH_STATE_SECRET)=" /etc/outbound-agent/front.env | cut -d= -f1 | sort'
sudo docker exec outbound-front sh -c 'for k in GMAIL_OAUTH_CLIENT_ID GMAIL_OAUTH_CLIENT_SECRET GMAIL_TOKEN_ENCRYPTION_SECRET GMAIL_OAUTH_STATE_SECRET; do if [ -n "$(printenv $k)" ]; then echo "$k=present"; else echo "$k=missing"; fi; done'
```

## Post-callback verification pattern

After the user completes Google OAuth consent and returns through the app callback, verify from three angles without printing secrets:

1. Browser/UI state
   - Re-open or inspect `/<teamSlug>/settings/email-senders` in the already-attached Chrome/CDP session.
   - Confirm the Gmail row shows the expected connected email, `active`, and `Ready for Gmail sending.`
   - If the callback URL still has `gmail=connected&reason=<senderIdentityId>`, record the sender identity ID as evidence.

2. Vercel/public server state
   - Public `/login` should return 200.
   - Unauthenticated protected routes should redirect to `/login` (commonly 307); treat that as expected auth behavior, not a failure.
   - `vercel inspect https://outbound-dev.vercel.app --scope querypie` should show the production deployment as `Ready` and list the alias.
   - `vercel logs --project outbound-dev --scope querypie --environment production --since 30m --no-follow --limit 200 --json` can confirm recent `/api/gmail/oauth/connect`, `/login`, and settings route statuses. Also run an error-only query (`--level error`) and report the count.

3. DB persistence evidence
   - Pull production env to a temporary `0600` file and delete it immediately after use.
   - Do not rely on `vercel env pull` to reveal sensitive Gmail values: sensitive variables may appear as placeholders or empty/unusable values locally. Use it only for key presence/metadata and non-sensitive DB connection lookup.
   - For `psql`, prefer `POSTGRES_URL_NON_POOLING`, then `POSTGRES_URL`, then `DATABASE_URL`. Avoid `POSTGRES_PRISMA_URL` for direct `psql`; its Prisma/pooler query parameters such as `pgbouncer` can make `psql` fail with `invalid URI query parameter`.
   - Query only safe columns and token presence, not token contents:

```sql
select
  si.id,
  si."providerType",
  si."emailAddress",
  si.status,
  gc."connectedEmailAddress",
  (gc."encryptedRefreshToken" is not null) as has_encrypted_refresh_token,
  gc."createdAt"::text as credential_created_at,
  gc."updatedAt"::text as credential_updated_at
from "SenderIdentity" si
left join "GmailSenderCredential" gc on gc."senderIdentityId" = si.id
where si."providerType" = 'gmail' or si."emailAddress" = '<expected sender email>'
order by si."createdAt" desc
limit 10;
```

## Issue evidence comment

For Gmail actual-send blocker/status issues, leave a neutral evidence comment after setup. Include:

- GCP project ID and OAuth client name, but not the secret.
- Gmail API enabled status.
- redirect URI validation status.
- each environment's env-key presence/redeploy/restart result.
- public `/login` smoke status.
- Gmail connect callback result: sender identity ID, connected email, `active` status, encrypted refresh-token presence, and relevant server log status counts.
- explicit remaining live smoke steps: Sales Person sender selection, test send or small actual SendRun, Gmail message/thread id evidence.

Do not use auto-close keywords unless the user explicitly asks to close the issue.