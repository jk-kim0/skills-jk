# Gmail OAuth `gmail_refresh_token_missing` on reconnect

Use this reference when an Outbound Agent dev environment reports `Gmail connection failed` with `reason=gmail_refresh_token_missing` after the user appears to have completed Google OAuth successfully.

## Root cause pattern

Google OAuth can return a successful authorization-code token response without a `refresh_token` when the Google account has already authorized the same OAuth client/scope combination. This is common in reconnect flows and should be distinguished from a failed consent screen.

A fragile implementation fails in the callback boundary whenever `payload.refresh_token` is absent, even if:

- the token endpoint response is HTTP 200,
- granted scopes are present and valid,
- the identity token is present and valid,
- the Team already has a Gmail sender credential for the same sender address.

## Correct handling

1. Keep the authorization URL contract explicit: `access_type=offline` and a consent prompt.
2. At the token-exchange/callback boundary, treat missing `refresh_token` on an otherwise successful response as an optional value, not immediate failure.
3. At the sender persistence boundary:
   - if the callback includes a new refresh token, encrypt and store it as usual;
   - if the callback omits a refresh token and an existing Team-scoped Gmail sender credential exists for the same sender, update metadata such as Gmail user id, connected email, granted scopes, display name, and status while preserving the stored encrypted refresh token;
   - if no stored credential exists, fail with `gmail_refresh_token_missing` because first-time actual sends still require a refresh token.
4. Avoid overwriting `encryptedRefreshToken` with an empty/undefined value during reconnect.

## Regression tests to add

- Callback test: token endpoint returns HTTP 200 with `scope` and `id_token`, but no `refresh_token`; `completeGmailOAuthCallback` returns identity/scope data and `refreshToken` is `undefined`.
- Persistence test: reconnect path without `input.refreshToken` performs a lookup for the existing sender credential, updates non-secret Gmail metadata, and does not write `encryptedRefreshToken` in that branch.

## Sender-specific connect UX and mismatch handling

When the Email Senders page represents pre-registered Team sender addresses, do not use one generic page-level `Connect Gmail` CTA that starts OAuth without a sender address. Put the connect/reconnect action on each Gmail sender row and include that row's email address in the OAuth start request and signed state (for example `senderEmail` -> `state.senderEmailAddress`).

The OAuth start route should require the sender email and verify that it belongs to a registered Team-scoped Gmail sender before redirecting to Google. This prevents an OAuth callback from silently creating or updating a sender that the user did not explicitly choose.

If the Google account used during OAuth does not match the selected sender email, the callback boundary should fail with `gmail_alias_mismatch` (not `gmail_refresh_token_missing`). In UI copy, explain it as a sender-address authentication failure, e.g. "Use the same Google account as the selected Email Sender address," rather than exposing only the raw reason code.

## Reporting note

Explain the issue as a reconnect/token-response contract bug, not as a Google authentication failure. If the flow used a generic connect button, also report the UX/root-contract issue: OAuth was not bound to a specific registered Email Sender. The user-facing symptom can be the redirect query `gmail=failed&reason=gmail_refresh_token_missing` on the Email Senders page.
