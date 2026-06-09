# Tencent Gmail OAuth `invalid_client` token exchange diagnosis

Use this reference when a Tencent dev environment redirects back to Email Senders with `gmail=failed&reason=gmail_oauth_token_exchange_failed` after the user completes Google OAuth.

## Symptom signature

- Browser lands on a URL like:
  - `/querypie-kr/settings/email-senders?gmail=failed&reason=gmail_oauth_token_exchange_failed&senderEmail=<email>`
- Nginx/access logs show the callback reached the app with a Google authorization `code` and `gmail.send` scope:
  - `/api/gmail/oauth/callback?...&code=...&scope=...https://www.googleapis.com/auth/gmail.send...`
- App journal logs from `gmail_oauth_callback` show:
  - `tokenResponseStatus: 401`
  - `providerError: 'invalid_client'`
  - `hasRefreshToken: false`

This distinguishes the issue from `redirect_uri_mismatch`, state/cookie mismatch, missing scope, or refresh-token omission. The failure happens at the server-side authorization-code-to-token exchange boundary.

## Likely root cause

Google rejected the OAuth client credentials used by the running Tencent app. Check the `GMAIL_OAUTH_CLIENT_ID` / `GMAIL_OAUTH_CLIENT_SECRET` pair first.

Common causes:

- VM-local `/etc/outbound-agent/front.env` has a stale client id or secret.
- GitHub repository secret `GMAIL_OAUTH_CLIENT_SECRET` is stale or copied from a different OAuth client.
- Google Console secret was rotated/regenerated but GitHub/VM runtime was not updated.
- The OAuth client was deleted/disabled or the app is using a client id from a different GCP project.
- The secret has hidden whitespace/newline corruption.

## Evidence collection pattern

1. Run the dedicated diagnosis workflow for the target environment/sender/team, or execute the equivalent VM diagnostic script:
   - `Diagnose tencent/outbound-seoul Gmail OAuth`
   - input examples: `lookback_minutes=180`, `sender_email=<selected sender>`, `team_slug=<team slug>`
2. Read only redacted evidence:
   - service state and deployed image/revision
   - Gmail env key presence/length/suffix, never values
   - sender DB state and whether a `GmailSenderCredential` exists
   - nginx callback/access snippets
   - `outbound-front` journal `gmail_oauth_callback` diagnostics
3. If the journal has `401 invalid_client`, do not spend time on redirect URI registration unless the authorization URL itself never reached callback.

## Remediation order

1. In Google Cloud Console, verify the Outbound Web OAuth client in the intended GCP project:
   - client id matches the runtime `GMAIL_OAUTH_CLIENT_ID` fingerprint/suffix;
   - client is enabled/not deleted;
   - secret is the current value;
   - authorized redirect URIs still include the shared callback for the environment.
2. Update repository secrets without printing values:
   - common: `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`;
   - VM-specific: `SEOUL_GMAIL_TOKEN_ENCRYPTION_SECRET`, `SEOUL_GMAIL_OAUTH_STATE_SECRET`, and Tokyo equivalents only if needed.
3. Re-apply Tencent runtime env through the opt-in workflow:
   - `Deploy Tencent container image`
   - same current image if only env sync is needed;
   - `update_gmail_oauth_config=true`;
   - `dry_run=true` first to validate secret presence/syntax;
   - then `dry_run=false` with `confirm_apply=APPLY` to mutate VM env and restart/deploy.
4. Re-run diagnosis and then ask the user to retry OAuth, or perform a browser smoke if an authenticated session is available.

## Important distinction

A successful dry-run proves GitHub Secrets are present and shell-parseable; it does not prove the secret matches the Google OAuth client. If `invalid_client` persists after a fresh env sync, treat the source secret or Google Console client state as the next source of truth.

## Targeted restart / all-target workflow pitfall

`Deploy Tencent container image` may run dev-tokyo before dev-seoul. A dev-tokyo deploy/runtime failure can prevent the dev-seoul job from running, even if the user only needs dev-seoul Gmail OAuth config repair.

- Do not report that the intended VM was updated until job order, skipped jobs, diagnostics, and VM-local env/container state prove it.
- If only a restart/redeploy is needed after a prior successful env sync, the target-specific `Deploy tencent/outbound-seoul` or Tokyo workflow can restart the app, but it does not apply Gmail OAuth env updates.
- After a restart workflow shows an immediate public `/login` 502, run diagnostics and a fresh public `/login` probe before declaring the environment broken; it may be a transient readiness gap.
- Prefer a target input or target-specific env-sync path so one VM's deploy drift cannot block the intended VM's config repair.
