# Gmail `refresh_token` Missing Diagnostics

Use this reference when an OAuth callback redirects with a product error like `gmail_refresh_token_missing`, especially in sender-scoped Gmail connection flows.

## What the error usually means

In Google OAuth, the token endpoint may return an access token and ID token without returning a new `refresh_token`. This commonly happens when the same Google account has already granted the same OAuth client/scope combination before.

If the application DB has no existing stored Gmail credential for the selected sender, the app cannot persist or reuse a refresh token and should fail with a refresh-token-missing error.

Diagnostic interpretation:

1. The OAuth callback reached the application.
2. The Google token exchange succeeded enough to produce an ID token and scopes.
3. If the app validates the selected sender email against `id_token.email` before saving credentials, an email mismatch should fail earlier with a distinct alias/account mismatch error.
4. A refresh-token-missing error after that validation usually means:
   - selected sender email and Google identity matched, or at least mismatch validation did not fail;
   - Google did not include `refresh_token` in the token response;
   - no existing credential was found for that sender/team/provider in the DB.

## How to distinguish from wrong-account errors

For sender-scoped Gmail connection UX, treat these as separate cases:

- Wrong Google account for the selected sender: selected sender email differs from Google `id_token.email`; report an alias/account mismatch and tell the user to authenticate with the same Google account as the selected sender.
- Missing sender state: the callback cannot identify which sender row started OAuth; report a sender-state-missing error and tell the user to restart from the row-level Connect Gmail button.
- Missing refresh token: selected sender is known and identity validation passed, but the token response has no refresh token and the DB has no reusable credential; tell the user to revoke the app consent in Google Account access and retry from the intended sender row.

## Suggested evidence to collect

Do not log secrets. Safe structured fields:

- environment and app revision
- service/container restart time and image/revision
- team slug or team id, if safe
- selected sender email, if acceptable for the environment
- normalized Google identity email, if acceptable for the environment
- OAuth callback reached app: `hasCode`, callback HTTP status/redirect reason, and redacted requested scopes
- token endpoint response class: HTTP status and provider `error` string only, not tokens/code/secret
- `hasRefreshToken` boolean
- `hasExistingCredential` boolean
- OAuth failure reason

If direct DB access is available, verify the selected sender has or lacks a provider credential by joining sender identity/credential tables for the target team, provider type, and normalized email. Also check whether the credential table is globally empty and whether sender rows were recreated recently as `auth_required`; a recent dev/stage `migrate reset` + seed can delete stored refresh tokens while leaving Google-side grants intact. Do not print encrypted refresh tokens or connection strings.

## Distinguish token exchange failure from missing refresh token

Do not map every Google token endpoint failure to `refresh_token_missing`. Split these cases in code, logs, and user/admin messages:

- `!response.ok`: token exchange failed. Record a safe provider error such as `invalid_client`, `invalid_grant`, or `redirect_uri_mismatch`, plus HTTP status. Use a reason like `gmail_oauth_token_exchange_failed`.
- `response.ok` but no `refresh_token`, and no existing sender credential in DB: Google omitted a refresh token for an already-approved client/scope or similar consent state. Use `gmail_refresh_token_missing` and tell the user to revoke app consent and retry.
- `response.ok` but no `refresh_token`, and an existing sender credential is present: reuse/update metadata without replacing the stored refresh token, if the product supports that behavior.

This distinction is especially important after dev/stage DB resets: Google may still consider the user to have granted the OAuth client, while the app DB no longer has the prior refresh token.

## User-facing recovery copy

Good recovery message shape:

`Selected Email Sender: <email>. Google did not return a refresh token. If this is not the Email Sender you intended to connect, start again from the correct row. Otherwise revoke the app consent in Google Account access and try again.`

## UX recommendation

For products with multiple Email Senders, prefer row-level `Connect Gmail` actions over a single global button. The OAuth start request should include a signed/validated sender identifier, and callback handling should validate that Google `id_token.email` matches the selected sender before credential persistence. This prevents a global connect action from silently attaching a credential to the wrong sender and makes failure messages actionable.
