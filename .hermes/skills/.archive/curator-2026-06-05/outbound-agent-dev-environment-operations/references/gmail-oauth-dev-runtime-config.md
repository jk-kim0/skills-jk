# Gmail OAuth dev runtime configuration

Use this reference when updating Outbound Agent Gmail OAuth settings for local and development deployments.

## Durable configuration pattern

- Use an Outbound-specific Google OAuth Web client for shared development/deployment smoke rather than a personal/client-specific credential.
- Keep callback route shared and Team-slug-free: `/api/gmail/oauth/callback`.
- Carry Team context and return path through OAuth `state` instead of adding Team-specific redirect paths.
- Required scope for send-only smoke: `https://www.googleapis.com/auth/gmail.send`.

## Redirect URI set for current dev environments

Register/check these together for the shared development client:

- `http://localhost:3000/api/gmail/oauth/callback`
- `https://outbound-dev.vercel.app/api/gmail/oauth/callback`
- `https://outbound-seoul.dev.querypie.io/api/gmail/oauth/callback`
- `https://outbound-tokyo.dev.querypie.io/api/gmail/oauth/callback`

Do not add customer production hosts until a production environment exists and the production callback policy is decided.

## Runtime env names

Repository files should mention names only, never values:

- `GMAIL_OAUTH_CLIENT_ID`
- `GMAIL_OAUTH_CLIENT_SECRET`
- `GMAIL_TOKEN_ENCRYPTION_SECRET`
- `GMAIL_OAUTH_STATE_SECRET`
- Optional override: `GMAIL_OAUTH_REDIRECT_URI`

Prefer keeping `GMAIL_OAUTH_STATE_SECRET` separate from `GMAIL_TOKEN_ENCRYPTION_SECRET`, even if code has a fallback.

## Vercel notes

- For `querypie/outbound-dev`, update both Production and Preview targets if both are used for development validation.
- Confirm env key presence without printing values.
- Vercel environment updates do not affect existing deployments. Trigger or wait for a new deployment before live OAuth smoke.
- Local `.vercel` link state should not be committed; ensure the repo ignores the Vercel runtime state path used by the app workspace.

## Tencent VM notes

- Put actual values in root-only runtime env files, e.g. `/etc/outbound-agent/front.env`.
- Repository docs/runbooks should list the required keys and permission expectations, not secret values.

## Secret handling

If an OAuth client secret was pasted into chat or another durable transcript, treat it as exposed. Finish the planned smoke only if acceptable, then rotate/regenerate the secret in Google Cloud Console and update Vercel/VM secret stores. Never copy the secret into markdown docs, PR bodies, skills, or final summaries.

## Verification checklist

- Redirect URI registration confirmed in Google Console with an account that can access `querypie-saas-dev`; do not substitute a personal/Deck project account as live evidence.
- Local callback smoke works.
- New deployment has picked up updated env.
- Exact Vercel deployment evidence is captured from the GitHub run and `vercel inspect <dpl_...>`, especially if `main` advanced after the target PR merged.
- Pre-consent OAuth-start smoke reaches Google sign-in/consent with the expected `redirect_uri` and `gmail.send` scope and does not show `redirect_uri_mismatch`.
- Dev environment connect smoke works for Vercel, Seoul, and Tokyo.
- `gmail.send` scope granted.
- Refresh token is encrypted/stored as expected.
- Sender identity upsert occurs.
- Actual send smoke records provider evidence such as message/thread IDs, if the test scope includes sending.

See `references/gmail-oauth-production-deploy-smoke.md` for the post-merge Production deploy and pre-consent smoke pattern.
