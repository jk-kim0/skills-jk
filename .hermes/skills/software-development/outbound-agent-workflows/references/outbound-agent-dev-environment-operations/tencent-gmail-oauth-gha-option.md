# Tencent Gmail OAuth env update via GitHub Actions

Use this when rotating or repairing Gmail OAuth credentials for the Outbound Agent Tencent dev VMs (`dev-seoul`, `dev-tokyo`).

## Durable lesson

Tencent VM runtime Gmail OAuth values are sourced from the VM-local root-only file `/etc/outbound-agent/front.env`, not from Vercel project env.
Normal image/code deployment must not silently mutate that file.
When credential rotation is needed, use an explicit opt-in workflow option so regular deployments remain low-risk.

## Workflow pattern

The manual `Deploy Tencent container image` workflow should include an opt-in boolean such as `update_gmail_oauth_config`, defaulting to `false`.

When false:

- deploy the selected immutable image only
- do not modify `/etc/outbound-agent/front.env`

When true:

- require the relevant GitHub repo secrets to exist
- upload a temporary env file over SSH
- replace only the Gmail OAuth keys in `/etc/outbound-agent/front.env`
- create a timestamped backup before replacement, e.g. `/etc/outbound-agent/front.env.bak-gmail-oauth-<timestamp>`
- upload any temporary dotenv file over SSH/SCP, remove it after use, and generate shell-readable values with safe quoting such as `printf '%s=%q\n' NAME VALUE`
- restart/redeploy the app so the container reads the new env values

Required secret shape used by the current workflow pattern:

- common repo secrets when Seoul/Tokyo share the same Google OAuth client: `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`;
- VM-specific token/state secrets when fingerprints differ: `SEOUL_GMAIL_TOKEN_ENCRYPTION_SECRET`, `SEOUL_GMAIL_OAUTH_STATE_SECRET`, `TOKYO_GMAIL_TOKEN_ENCRYPTION_SECRET`, `TOKYO_GMAIL_OAUTH_STATE_SECRET`;
- avoid `secrets: inherit` for this path when explicit mapping can document which secret reaches which VM.

## Dry-run behavior

A dry-run with the option enabled should validate secret presence and the uploaded env syntax, but must not mutate VM files.
This gives operators a safe way to prove the secret path is ready before applying. Validate workflow YAML with `actionlint`, extracted shell with `bash -n`, and the final patch with `git diff --check`.

## Security notes

- Never print secret values in logs or PR bodies.
- If reporting verification, use presence, length, or short cryptographic fingerprints only.
- Do not reuse Vercel env as an implicit source of truth for Tencent VMs unless a deliberate sync mechanism exists.
