# OAuth Callback Origin Verification for VM Deployments

## Durable lesson

For Next.js/Node apps deployed on Linux VMs behind nginx/container runtime, OAuth callback URLs should not depend on runtime request-origin inference unless the proxy and framework trust settings are explicitly verified.

A container or service environment can cause `request.nextUrl.origin` or equivalent request-origin logic to resolve to an internal host such as `https://localhost:3000`, even when the public site is served at `https://<fqdn>`.

## Symptom

- OAuth provider returns `redirect_uri_mismatch`, `Error 400`, or an equivalent invalid callback error.
- The app appears deployed and reachable, but the provider authorization URL contains a callback with `localhost`, internal port, wrong scheme, or wrong environment FQDN.

## Verification pattern

1. Inspect the generated provider authorization URL from the app endpoint that starts OAuth.
2. Decode/extract the `redirect_uri` query parameter.
3. Compare it to the environment's public callback URL and the provider console's Authorized redirect URI.
4. If it is wrong, set an explicit environment-specific callback URI in the host-managed service env, restart the service/container, and re-check the generated authorization URL.

Example for a dev VM:

```text
GMAIL_OAUTH_REDIRECT_URI=https://<dev-fqdn>/api/gmail/oauth/callback
```

## Operational notes

- Back up the host-managed env file before changing it.
- Keep client id/client secret checks secret-redacted; only report presence, suffixes, or mismatch indicators.
- After restart, verify both the app page/button state and the provider authorization endpoint behavior.
- If provider docs or runbooks specify a canonical OAuth client per environment, verify the VM env uses that same client in addition to verifying the callback URI.
