# Gmail OAuth token exchange diagnostics

Use this reference when Gmail OAuth callback failures are ambiguous between Google token endpoint errors and missing refresh-token persistence.

## Durable implementation pattern

- Do not classify token endpoint non-2xx responses as `gmail_refresh_token_missing`.
- Classify Google token endpoint 4xx/5xx as `gmail_oauth_token_exchange_failed`.
- Preserve provider diagnostics on the thrown error object, without storing secrets:
  - `providerError` from token payload `error` such as `invalid_grant`, `invalid_client`, or `redirect_uri_mismatch`
  - `tokenResponseStatus`
  - `hasRefreshToken`
- Parse the token response body before the `response.ok` check so the provider error and refresh-token presence can be logged even on 4xx.
- Reserve `gmail_refresh_token_missing` for the successful-token-response path where Google omitted `refresh_token` and no existing credential is available for the selected sender.
- When no refresh token is returned but an existing sender credential exists, treat the OAuth callback as usable and update non-secret identity/scope metadata while reusing the stored refresh token.

## Safe callback logging contract

Callback logs may include only this safelist:

- `environment`
- `origin`
- `senderEmail`
- `tokenResponseStatus`
- `providerError`
- `hasRefreshToken`
- `hasExistingCredential`

Do not log OAuth `code`, signed `state`, nonce/cookie values, client secret, refresh token, access token, id token, or raw token response body.

## Regression tests to add

Add/keep narrow tests for both layers:

1. Token exchange helper/service:
   - Google token endpoint 4xx with `{ error: "redirect_uri_mismatch" }` rejects with `code: "gmail_oauth_token_exchange_failed"`.
   - The rejected error carries `providerError`, `tokenResponseStatus`, and `hasRefreshToken`.
   - Successful token response without `refresh_token` still returns a connection input with `refreshToken: undefined` so the persistence layer can decide whether an existing credential is reusable.
2. Callback route:
   - Token-exchange failure redirects with `reason=gmail_oauth_token_exchange_failed`.
   - `console.warn("gmail_oauth_callback", ...)` receives only safelisted fields.
   - The serialized log calls do not contain OAuth code, signed state, nonce/cookie, or secrets.

## CI pitfall

Full CI may include repository contract tests that assert canonical docs contain operational semantics such as Gmail delivery meaning or suppression scope. If a CI failure is in a docs contract test unrelated to the OAuth source files, inspect the exact assertion before changing product code. Often the correct fix is to restore the canonical documentation sentence that matches already-existing OpenSpec/status docs, then rerun only the failing contract tests before pushing.
