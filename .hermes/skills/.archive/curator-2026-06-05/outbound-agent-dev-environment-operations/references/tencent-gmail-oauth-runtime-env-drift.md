# Tencent Gmail OAuth runtime env drift

Use this note when Gmail OAuth works on `outbound-dev` (Vercel/Incheon) but fails or uses stale client metadata on Tencent dev servers.

## Durable lesson

Tencent dev servers do not consume Vercel environment variables at runtime. They run the container with:

- systemd unit: `/etc/systemd/system/outbound-front.service`
- container env source: `/etc/outbound-agent/front.env`
- deploy script: `infra/tencent-vm/deploy-image.sh`

The main container deployment path pulls and starts a new immutable `outbound-front` image, but it preserves `/etc/outbound-agent/front.env`. Therefore a successful latest-version deploy can still leave stale OAuth runtime config on dev-seoul/dev-tokyo.

## Investigation pattern

1. Compare Vercel env presence/age without printing values.
   - `cd front && vercel env ls --scope querypie`
   - Confirm `GMAIL_OAUTH_CLIENT_ID` and `GMAIL_OAUTH_CLIENT_SECRET` exist for Production/Preview.
2. Check GitHub repo/environment secrets for an automated Tencent env source.
   - `gh secret list --repo querypie/outbound-agent`
   - `gh variable list --repo querypie/outbound-agent`
   - If Gmail keys are absent, the Tencent deploy workflow cannot be syncing them from GitHub.
3. Inspect deployment scripts for env-file behavior.
   - `.github/workflows/reusable-deploy-tencent-container-image.yml`
   - `infra/tencent-vm/deploy-image.sh`
   - `infra/tencent-vm/outbound-front.service`
   - Look for `--env-file /etc/outbound-agent/front.env` and absence of writes to Gmail OAuth keys.
4. On each Tencent VM, print only metadata/fingerprints, never secret values.
   - `stat` `/etc/outbound-agent/front.env` and list recent backups.
   - Source the file under sudo and print `present`, length, and sha256 prefix for keys such as `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`, `GMAIL_TOKEN_ENCRYPTION_SECRET`, `GMAIL_OAUTH_REDIRECT_URI`, and `DATABASE_URL`.
   - Check backup files the same way to prove whether a stale value survived previous deploys.
5. After updating VM env, restart `outbound-front` and verify through the public FQDN OAuth start route.
   - Validate the Google authorization URL contains the expected `client_id` fingerprint and `redirect_uri` for the exact public host.
   - A Google authorization endpoint HTTP 200 with no `redirect_uri_mismatch` is start-route evidence; callback token exchange still depends on matching `GMAIL_OAUTH_CLIENT_SECRET`.

## Reporting pattern

Separate these causes clearly:

- Vercel/outbound-dev env rotation status.
- Tencent VM-local `/etc/outbound-agent/front.env` status.
- Whether GitHub Actions has any source secret/variable from which it could sync Gmail keys.
- Whether the deploy workflow updates secrets or only the container image.
- Current and backup fingerprints, using hashes only.

The root cause phrase to use when supported by evidence:

“Latest app image/code deployment succeeded, but Gmail OAuth values are runtime secrets in Tencent VM-local `/etc/outbound-agent/front.env`. The current CD path preserves that file and has no GitHub/Vercel env sync step, so Vercel OAuth rotation did not propagate to dev-seoul/dev-tokyo.”
