# Gmail OAuth dev-environment parity checks

Use this reference when Outbound Agent Gmail OAuth works in one dev environment but fails, redirects incorrectly, or may be misconfigured in another.

## Durable parity pattern

1. Choose the authoritative OAuth configuration source first.
   - For Outbound Agent dev environments, `outbound-dev`/Vercel is commonly the source of truth for the current Google OAuth web client.
   - Treat `client_id` as non-secret enough to compare in redacted/fingerprinted form, but never print `client_secret`.

2. Compare runtime OAuth start URLs, not only env files.
   - Trigger the app's Gmail OAuth start endpoint in each environment.
   - Parse the first redirect `Location` to `accounts.google.com`.
   - Verify at least:
     - `client_id` fingerprint matches the authoritative environment.
     - `redirect_uri` is the exact public callback URL for that environment.
     - expected scopes include Gmail send.
     - Google authorization endpoint returns an auth page, not `redirect_uri_mismatch` or `Error 400`.

3. Use fingerprints for chat/log evidence.
   - Example: hash the `client_id` and report only a short prefix such as `95525beca188`.
   - Report the redirect URI and scope because they are operational routing data, not secrets.
   - Do not print `GMAIL_OAUTH_CLIENT_SECRET`, refresh tokens, DB URLs, or encrypted credential values.

4. If a VM environment has a stale `GMAIL_OAUTH_CLIENT_ID`, update the VM runtime env, keep a timestamped backup of the env file, and restart only the app service.
   - Re-check the effective OAuth start URL after restart.
   - Do not rely on the edited env file alone.

5. Be precise about what was proven.
   - OAuth start parity and Google authorization-page acceptance proves client id + redirect URI configuration is accepted.
   - It does not prove callback token exchange unless a real callback completes.
   - If the client secret cannot be read from the authoritative platform because it is encrypted/sensitive, say that directly and require the same secret source to be applied to the VM before claiming callback exchange readiness.

## Common pitfall

A deployment can be on the latest code and pass DB migration/schema checks while still having stale OAuth runtime env values.
Keep provider-configuration parity as a separate post-deploy smoke step for Gmail OAuth tasks.
