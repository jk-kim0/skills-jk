# Tencent Gmail OAuth `invalid_client` and targeted restart

Use this reference when dev-seoul/dev-tokyo Gmail OAuth redirects back with `gmail=failed&reason=gmail_oauth_token_exchange_failed` after the Google consent screen.

## Root-cause signal

In the app callback, `gmail_oauth_token_exchange_failed` is emitted when the Google token endpoint returns non-OK during authorization-code exchange. Confirm with the Tencent Gmail OAuth diagnostic workflow and look for the structured callback log:

- `tokenResponseStatus: 401`
- `providerError: 'invalid_client'`
- `hasRefreshToken: false`

This means Google rejected the OAuth client credentials during token exchange. It is distinct from `redirect_uri_mismatch`, state verification failures, scope errors, alias mismatch, or missing refresh token handling.

## Evidence to collect without leaking secrets

Run `Diagnose tencent/outbound-seoul Gmail OAuth` or the Tokyo equivalent if present, passing the sender email and team slug. Confirm:

- `outbound_front=active`, `nginx=active`
- deployed revision/image
- redacted env presence/length for `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`, `GMAIL_TOKEN_ENCRYPTION_SECRET`, `GMAIL_OAUTH_STATE_SECRET`
- sender credential row state for the selected sender
- journal `gmail_oauth_callback` fields: `tokenResponseStatus`, `providerError`, `hasRefreshToken`

Do not print client secrets, refresh tokens, encrypted tokens, DB URLs, private keys, or raw callback `code`/state values.

## Fix pattern

1. Verify the Google Cloud/Auth Platform Web OAuth client is the intended Outbound client and is enabled.
2. Update repository secrets with the current client credentials:
   - `GMAIL_OAUTH_CLIENT_ID`
   - `GMAIL_OAUTH_CLIENT_SECRET`
3. Apply Tencent VM-local Gmail OAuth env through `Deploy Tencent container image` with:
   - `dry_run=false`
   - `confirm_apply=APPLY`
   - `update_gmail_oauth_config=true`
4. Re-run the diagnostic workflow and retry the browser OAuth connect.

If the client secret was pasted into chat, issue comments, docs, logs, or any durable transcript, treat it as exposed. Finish only the minimum smoke that is acceptable, then rotate/regenerate the secret in Google Console and repeat the GitHub Secret + VM env sync.

## Workflow pitfall: all-target deploy can block the intended VM

`Deploy Tencent container image` currently runs dev-tokyo before dev-seoul. A dev-tokyo deployment/runtime failure can prevent the dev-seoul job from running at all, even when the user only cares about dev-seoul Gmail OAuth config.

If the all-target workflow fails before the intended VM:

- Do not report that the intended VM was updated; inspect job order and skipped jobs first.
- Use diagnostics to confirm whether the intended VM's env/container actually changed.
- If only a restart/redeploy is needed for dev-seoul, the separate `Deploy tencent/outbound-seoul` workflow can restart/redeploy the app, but it does not apply Gmail OAuth env updates.
- After a restart workflow fails on an immediate public `/login` 502, run diagnostics and a fresh public `/login` curl/probe before declaring the environment broken; the 502 can be a transient readiness gap right after container replacement.

Long-term workflow improvement: add a target input or seoul-only Gmail OAuth env-sync path so dev-tokyo drift cannot block dev-seoul config repair.
