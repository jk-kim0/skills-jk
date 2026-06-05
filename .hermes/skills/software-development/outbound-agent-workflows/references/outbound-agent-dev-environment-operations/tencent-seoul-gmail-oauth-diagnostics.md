# Tencent Seoul Gmail OAuth diagnostics

Use this when investigating `gmail_refresh_token_missing` or Gmail connection failures on `outbound-seoul.dev.querypie.io`.

## Durable workflow

1. Confirm the relevant PR/commit has actually reached the Seoul VM before interpreting runtime logs.
   - Use the Tencent read-only diagnostics to capture `current_revision`, `current_image`, `outbound_front`, `nginx`, and container state.
   - A newly merged workflow can exist in GitHub before the app image using the same commit is deployed.

2. Run the dedicated Seoul Gmail OAuth diagnosis workflow when available.
   - Workflow: `Diagnose tencent/outbound-seoul Gmail OAuth`
   - Inputs to preserve evidence boundaries: `lookback_minutes`, `sender_email`, `team_slug`.
   - Treat it as read-only log/env/DB evidence collection; do not mutate OAuth state from this workflow.

3. If the dedicated diagnosis workflow cannot read Docker/Postgres because the VM user lacks Docker socket permissions, fall back to the schema-check workflow path that uses the repo's Tencent VM helper with sudo-capable Docker access.
   - Workflow: `Check tencent/outbound-seoul DB Schema`
   - Dispatch it on `main` after the diagnosis workflow has been merged.
   - Use this fallback to collect `SenderIdentity` and `GmailSenderCredential` state.
   - Follow-up fix for the dedicated diagnosis workflow: make remote Docker calls use `sudo docker` or the shared Tencent VM helper rather than plain `docker`.

4. Interpret OAuth callback evidence carefully.
   - nginx access logs can prove Google returned to `/api/gmail/oauth/callback` with `code`, `scope`, `hd`, and `prompt=consent`.
   - DB state proves whether a `GmailSenderCredential` was actually created.
   - App/journal logs must contain token endpoint status/provider error to distinguish `200 without refresh_token` from `4xx token exchange failure`. If those fields are absent, report that the current logs cannot distinguish those cases.

## Evidence shape to report

- Deployed revision/image on Seoul.
- Gmail OAuth env presence only, with lengths/suffixes; never print secrets.
- Sender row status for the exact `team_slug` and `sender_email`.
- `GmailSenderCredential` count and whether the target sender has a credential.
- Callback access-log sequence, with `code`, `state`, access token, and refresh token values redacted.
- Whether app journal contains token endpoint status/provider error.

## Common conclusion pattern

If Vercel succeeds but Seoul still has `GmailSenderCredential=0`, do not infer the Google account or app code is globally broken. Vercel and Seoul use separate databases; a refresh token stored in Vercel does not populate Seoul. The Seoul-specific question becomes whether the Seoul callback received no refresh token or whether token exchange failed and the app mapped that failure to `gmail_refresh_token_missing`.
