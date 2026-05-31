---
name: gmail-oauth-dev-environment-setup
description: Set up Gmail send-only OAuth for local/dev/stage environments without leaking secrets; map Google redirect URIs to runtime env injection and smoke evidence.
version: 1.0.0
metadata:
  hermes:
    tags: [gmail, oauth, gcp, vercel, vm, secrets, smoke]
---

# Gmail OAuth Dev Environment Setup

Use this skill when configuring Gmail send-only OAuth for an application environment, especially when the work spans Google Cloud/Auth Platform, Vercel/env vars, VM env files, and live OAuth/send smoke evidence.

## Core workflow

1. Read the repo's existing OAuth/env documentation and issue/status tracker first.
   - Identify the canonical callback route in code/docs.
   - Identify all target runtime URLs literally; do not substitute redirects or adjacent hosts.
   - Identify where each target stores runtime secrets: Vercel env, VM env file, GitHub environment secret, Kubernetes secret, etc.
2. Ask for missing external Google/Auth Platform decisions before mutating runtime state.
   - GCP Project ID.
   - Whether to reuse an existing OAuth client or create an app-specific Web OAuth client.
   - OAuth Client ID/Secret location, preferably 1Password or another secret store rather than chat.
   - Consent screen app name, support/developer email, Audience/Internal/External/Testing, and test users.
   - Sender account and smoke recipient addresses.
   - Whether token encryption secret is environment-specific or intentionally shared for early smoke.
3. Configure Google OAuth Web application client.
   - Register only backend callback URIs, not UI start routes.
   - For Team/tenant-scoped flows, tenant context should usually travel in OAuth state, not in the Google Console redirect URI.
   - Request only the needed Gmail scope for send-only MVP: `https://www.googleapis.com/auth/gmail.send`.
4. Inject runtime env vars without printing values.
   - Common names: `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`, `GMAIL_TOKEN_ENCRYPTION_SECRET`.
   - Optional names if the app supports them: `GMAIL_OAUTH_STATE_SECRET`, `GMAIL_OAUTH_REDIRECT_URI`.
   - Report only presence/target/environment, never secret values.
   - For Vercel sensitive env vars, verify with the Project Env API/list output after mutation. Some CLI versions reject `vercel env update` for sensitive keys; use remove + add for that target. If a Preview-scoped `vercel env add ... --sensitive` reports success but the key is missing from API/list output, create the key with `vercel api /v10/projects/<project-id>/env --input <json-file>` and treat the API/list output as source of truth.
   - If `vercel link` is needed inside a worktree, it may create a nested app-level `.gitignore`; remove that temporary file and add the generated `.vercel/` path to the repository's intended ignore file instead of committing the nested ignore by accident.
5. Restart/redeploy the affected runtime.
   - Vercel: set env for the correct project and targets, then redeploy if the current deployment must pick up new vars.
   - VM/systemd/container: update the env file read by the service/container and restart the app service/container.
6. Run staged smoke.
   - OAuth connect from the product UI.
   - Confirm credential/sender identity persisted, redacting email if needed.
   - Send a Gmail test message or the smallest approved batch allowed by the product flow.
   - Record that `sent` means provider API accepted unless delivery/open/reply tracking is explicitly implemented.
7. Record evidence in the durable tracker without secrets.
   - Include environment, app URL, callback URI, OAuth client identity label or secret-store item, sender/recipient redaction, timestamp, app revision, and message id/thread id presence if safe.

## Secret-handling rules

- Do not paste client secrets, refresh tokens, encryption secrets, DB URLs, private keys, or provider tokens into chat, issue bodies, PR bodies, logs, or repo files.
- Prefer 1Password item/field references, cloud secret manager names, or platform secret keys.
- When probing secret presence, output `present=true`, length, field labels, or env var names only.
- If a secret appears in tracked files or command output, stop and remove/redact before continuing.

## Common pitfalls

- `redirect_uri_mismatch` usually means the exact callback URL used by the app is missing from the OAuth client. Add the exact backend callback URI for each environment.
- Do not register tenant/team UI paths like `/{teamSlug}/settings/email-senders` as OAuth redirect URIs when the code uses a shared `/api/.../callback` route.
- Vercel Production/Preview names may still be development environments; decide env target by project policy, not by the word Production alone.
- VM docs may list public FQDNs while the runtime reads env from a local file such as `/etc/<app>/front.env`; confirm the service/container actually loads that file before reporting configured.
- A successful app deploy or login route smoke does not prove Gmail OAuth/send readiness. Run OAuth connect and a minimal provider send smoke separately.
- Google OAuth `invalid_client` after env injection can be caused by a copied `client_id` containing a trailing newline or whitespace, not only by a wrong/disabled client. Re-inject the value through an API or secret mechanism that preserves the exact value, verify only a redacted suffix/length, redeploy/restart, then retry from the product OAuth start route.

## References

- `references/outbound-agent-gmail-oauth-dev-envs.md` — QueryPie outbound-agent environment URI and secret-injection checklist captured from issue #145 setup work.
- `references/vercel-sensitive-env-gmail-oauth.md` — Vercel sensitive env replacement/verification pattern for Gmail OAuth client secrets, including Preview target API fallback and worktree `.vercel` ignore hygiene.
