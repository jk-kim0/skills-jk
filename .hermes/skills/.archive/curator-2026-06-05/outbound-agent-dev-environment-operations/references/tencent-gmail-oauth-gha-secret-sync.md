# Tencent Gmail OAuth GitHub Actions secret sync

Session learning: Tencent dev VM runtime Gmail OAuth values are not inherited from Vercel env. They live in `/etc/outbound-agent/front.env` and must be updated through the Tencent deployment workflow when OAuth client/secrets rotate.

Recommended source of truth for workflow-driven updates:

- Use repo-level GitHub Actions secrets for the values consumed by `Deploy Tencent container image`.
- Keep `GMAIL_OAUTH_CLIENT_ID` and `GMAIL_OAUTH_CLIENT_SECRET` as common repo secrets when Seoul/Tokyo share the same Google OAuth client.
- Keep token/state secrets VM-specific if their current fingerprints differ, to avoid invalidating existing encrypted Gmail tokens or state validation behavior:
  - `SEOUL_GMAIL_TOKEN_ENCRYPTION_SECRET`
  - `SEOUL_GMAIL_OAUTH_STATE_SECRET`
  - `TOKYO_GMAIL_TOKEN_ENCRYPTION_SECRET`
  - `TOKYO_GMAIL_OAUTH_STATE_SECRET`

Workflow shape:

- Add a manual `workflow_dispatch` boolean such as `update_gmail_oauth_config`, default `false`.
- Default/main-push deploys must not mutate VM-local secrets.
- When the option is true, map VM-specific secrets explicitly in the caller workflow instead of `secrets: inherit`.
- In dry-run mode, validate secret presence and uploaded dotenv syntax only; do not change `/etc/outbound-agent/front.env`.
- In apply mode, require the existing deploy confirmation gate, backup `/etc/outbound-agent/front.env`, replace only the Gmail OAuth keys, then deploy/restart.

Safe implementation notes:

- Never print secret values; compare only length and hash prefixes if needed.
- Upload a temporary dotenv file over SSH/SCP and remove it after use.
- Use `printf '%s=%q\n' NAME VALUE` when generating shell-readable env files in bash.
- Validate with `actionlint`, `bash -n` on extracted workflow shell blocks, and `git diff --check`.
