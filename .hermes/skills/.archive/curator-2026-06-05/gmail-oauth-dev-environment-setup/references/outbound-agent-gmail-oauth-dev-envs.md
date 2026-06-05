# QueryPie outbound-agent Gmail OAuth dev environment checklist

Captured from a setup session around `querypie/outbound-agent` issue #145, where Gmail actual-send release readiness depended on Google OAuth client setup plus env injection across three dev environments.

## Target environments

- `infra/dev-vercel`
  - Vercel project: `querypie/outbound-dev`
  - Runtime URL: `https://outbound-dev.vercel.app`
  - Env injection: Vercel project env, likely Production + Preview targets because both are development deploy targets in this repo.
- `infra/dev-seoul`
  - Tencent VM runtime URL: `https://outbound-seoul.dev.querypie.io`
  - Env injection: VM app env file used by `outbound-front.service` / container runbook, documented as `/etc/outbound-agent/front.env` in the container image runbook.
- `infra/dev-tokyo`
  - Tencent VM runtime URL: `https://outbound-tokyo.dev.querypie.io`
  - Env injection: VM app env file used by `outbound-front.service` / container runbook, documented as `/etc/outbound-agent/front.env` in the container image runbook.

## Google OAuth Web client redirect URIs

Register these exact backend callback URIs for the Outbound Agent Gmail flow:

```text
http://localhost:3000/api/gmail/oauth/callback
https://outbound-dev.vercel.app/api/gmail/oauth/callback
https://outbound-seoul.dev.querypie.io/api/gmail/oauth/callback
https://outbound-tokyo.dev.querypie.io/api/gmail/oauth/callback
```

Do not register `/{teamSlug}/settings/email-senders`; that is the product UI start/return area. Team context is carried in OAuth state and restored by the shared callback route.

## Required scope

```text
https://www.googleapis.com/auth/gmail.send
```

Do not add read/modify/calendar scopes for the send-only MVP unless a separate product decision and consent copy update exist.

## Runtime env vars

Required:

```text
GMAIL_OAUTH_CLIENT_ID
GMAIL_OAUTH_CLIENT_SECRET
GMAIL_TOKEN_ENCRYPTION_SECRET
```

Optional, depending on app defaults and environment needs:

```text
GMAIL_OAUTH_STATE_SECRET
GMAIL_OAUTH_REDIRECT_URI
```

Use 1Password or platform secret stores. Never place secret values in repo docs, GitHub issues, PR bodies, or chat transcripts.

## Questions to ask the user before applying

1. Which GCP Project ID should hold the OAuth client?
   - Existing repo docs mention `querypie-deck-dev` as an initial reference, but the user may prefer an Outbound Agent specific client/project.
2. Should the work reuse an existing OAuth client, add redirect URIs to the Deck Dev client, or create/use a dedicated Outbound Agent Web OAuth client?
3. Where are the OAuth Client ID/Secret stored?
   - Prefer a 1Password item with field labels rather than pasted secret values.
4. OAuth consent screen values:
   - App name.
   - User support email.
   - Developer contact email.
   - Audience: Internal vs External/Testing.
   - Test users.
5. Smoke sender and recipient:
   - Gmail account that will OAuth-connect as the sender.
   - Recipient address for minimal send smoke.
   - Whether to run only Gmail test send or a small Contact List + SendRun actual batch.
6. Should `GMAIL_TOKEN_ENCRYPTION_SECRET` be distinct per environment or temporarily shared for smoke?
7. For Tencent VMs, what SSH/bastion/VPN path should be used if direct SSH to the public host resets or is IP-restricted?

## Vercel env injection and retry note

When configuring `infra/dev-vercel`, if Google returns `invalid_client` after clicking `Connect Gmail`, check for invisible whitespace in `GMAIL_OAUTH_CLIENT_ID` before assuming the OAuth client itself is wrong. In one setup pass, a newline at the end of the client id survived the initial Vercel env update and caused `invalid_client`; replacing the Vercel production `GMAIL_*` env values through an API-backed update with the exact trimmed values, then redeploying production, allowed the flow to reach the Google login/password screen.

Safe evidence for this class of fix:

- Redacted client id suffix and length only, never the secret.
- Vercel project/environment target updated.
- Deployment id or URL after redeploy.
- OAuth flow progressed from `invalid_client` to Google login/consent.

## Evidence to record after setup

Record only non-secret evidence, for example:

- Environment and URL.
- OAuth client label or secret-store item reference, not the client secret.
- Redirect URI registered: yes/no.
- Runtime env keys present: yes/no.
- App revision/deployment id.
- OAuth connect result and sender identity persisted, with email redacted if needed.
- Gmail API accepted result; message/thread id presence if safe to store.
- Explicit note that Gmail API accepted does not prove delivery/open/reply tracking.

For issue #145 specifically, the durable tracker is the GitHub issue plus `docs/feature/status-gmail.md` in the repo. Do not close the issue unless the user explicitly asks.
