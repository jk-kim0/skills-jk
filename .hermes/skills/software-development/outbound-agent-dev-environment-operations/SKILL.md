---
name: outbound-agent-dev-environment-operations
description: Operate querypie/outbound-agent development deployments across Vercel/Incheon and Tencent Seoul/Tokyo, including latest-version checks, DB migrations, schema checks, reset escalation, and runtime smoke.
version: 1.0.0
metadata:
  hermes:
    tags: [outbound-agent, deployment, db-migration, tencent-vm, vercel, runtime-smoke]
---

# Outbound Agent Dev Environment Operations

Use this skill when the user asks to verify, deploy, migrate, reset, or smoke-test the three Outbound Agent development environments, or to update development-environment runtime configuration such as Gmail OAuth credentials/redirects:

- Vercel/Incheon: `https://outbound-dev.vercel.app/login`
- Tencent Seoul: `https://outbound-seoul.dev.querypie.io/login`
- Tencent Tokyo: `https://outbound-tokyo.dev.querypie.io/login`

This skill is for environment operations, not feature implementation. Keep secrets out of chat, logs, docs, PR bodies, and skill references. If a credential value appears in the user's message or prior context, treat it as compromised/redacted in all durable artifacts and recommend rotation after smoke verification.

## Operating principles

1. Start from latest remote `main`.
   - Run `git fetch origin main --prune` and use `git rev-parse origin/main` as the target SHA.
   - Do not assume the local root checkout is current; it may be behind `origin/main`.

2. Prefer migrate-only first.
   - Run DB migration workflows with `reset_database=false` first.
   - Run schema checks after migration.
   - Only escalate to reset when migration, schema check, or runtime smoke proves an environment is broken.
   - Do not reset merely because reset is available.

3. Verify deployment with authoritative environment-specific signals.
   - Vercel: use the production deployment workflow log, deployment ID, `vercel inspect <deployment-id> --scope querypie`, aliases, and runtime region.
   - Tencent VMs: read `/opt/outbound-agent/deployments/current-image` and `/opt/outbound-agent/deployments/current-revision` over SSH.
   - `curl -I /login` confirms public runtime health but not the exact deployed git revision.

4. Check all three DBs and runtimes.
   - Vercel DB is Supabase-backed and checked by the Vercel DB workflows.
   - Seoul/Tokyo DBs are VM-local PostgreSQL containers and checked by Tencent DB workflows.

## Canonical GitHub Actions workflows

Migration:

```text
Apply outbound-dev DB Migration
Apply tencent/outbound-seoul DB Migration
Apply tencent/outbound-tokyo DB Migration
```

Schema drift check:

```text
Check outbound-dev DB Schema
Check tencent/outbound-seoul DB Schema
Check tencent/outbound-tokyo DB Schema
```

Deployment:

```text
Deploy outbound-dev Production
PR Cache-Only Build Validation / Main Deploy outbound-front image
Deploy Tencent container image
```

Notes:

- `Deploy outbound-dev Production` creates the Vercel production deployment for `main`.
- Main-push Tencent image deployment builds/pushes `ireg.querypie.io/ci/outbound-front:<7-char-sha>`, deploys Seoul, then deploys Tokyo.
- Manual `Deploy Tencent container image` runs Tokyo first, then Seoul.

## Recommended sequence for “check latest + migrate all + reset broken envs”

1. Fetch and record target SHA.
2. Check recent Actions runs for the target SHA.
3. Dispatch the three DB migration workflows with reset disabled.
4. Dispatch the three DB schema check workflows.
5. Confirm deployment workflows for the target SHA.
6. Verify Vercel with deployment ID and `vercel inspect`.
7. Verify Tencent VMs with SSH:
   - `cat /opt/outbound-agent/deployments/current-image`
   - `cat /opt/outbound-agent/deployments/current-revision`
   - `systemctl is-active outbound-front`
   - `systemctl is-active nginx`
8. Smoke public `/login` on all three URLs.
9. If any migration/schema/runtime check fails, investigate the failed environment first; rerun that environment with reset only when the failure indicates drift or incompatible data/state.

## Gmail OAuth runtime configuration

When updating Gmail OAuth for development environments:

1. Keep the OAuth callback path Team-slug-free: `/api/gmail/oauth/callback`. Team context and return path should be carried in OAuth `state`, not encoded into redirect URIs.
2. Register/check the local and three dev redirect URIs as a set:
   - `http://localhost:3000/api/gmail/oauth/callback`
   - `https://outbound-dev.vercel.app/api/gmail/oauth/callback`
   - `https://outbound-seoul.dev.querypie.io/api/gmail/oauth/callback`
   - `https://outbound-tokyo.dev.querypie.io/api/gmail/oauth/callback`
3. Treat GCP OAuth client secret values as non-durable secrets. Do not write them to docs, PR bodies, skills, or logs. If an actual secret value was pasted into chat or another durable transcript, recommend rotating it after smoke verification. Do not infer secret exposure or rotation work from placeholder text, env key names, or a prior mistaken note unless the user confirms an actual value was exposed.
4. For Vercel `querypie/outbound-dev`, update both Production and Preview targets when the config is shared by dev preview/prod aliases. Confirm key presence without printing values.
5. Vercel env changes are not retroactive. Require a new deployment after env updates before judging live OAuth behavior.
6. For Tencent VM dev environments, document/apply env names in root-only runtime env files (for example `/etc/outbound-agent/front.env`) rather than repository files.
7. Smoke in order: local callback, `outbound-dev`, `outbound-seoul`, `outbound-tokyo`; verify `gmail.send` scope, encrypted refresh-token persistence, sender identity upsert, and actual send evidence when applicable.

## Pitfalls

- When adding or fixing a GitHub Actions E2E workflow for the three development environments, interpret the environments as already deployed targets (`outbound-dev`, `tencent/outbound-seoul`, `tencent/outbound-tokyo`). The workflow should test the selected public URL and any needed dev DB test hooks only; it should not deploy, mutate server revisions, run migrations/resets, or start an Actions-local Next dev server unless the user explicitly asks for that.
- If an existing Playwright E2E config starts `next dev` through `webServer`, add a deployed-target mode such as `E2E_SKIP_WEB_SERVER=true` and `E2E_BASE_URL=<dev URL>` rather than reusing the local config unchanged. Keep production/stage safety guards in place, and allow shared dev DB helper access only for the known dev targets with an explicit opt-in variable.
- Do not trust arbitrary 40-character hashes scraped from rendered `/login` HTML as the deployed git revision. They may be bundled asset or content hashes.
- Do not confuse public HTTP 200 with exact version verification.
- Do not proactively reset shared/dev databases. Reset is an escalation path after a confirmed problem.
- If a GitHub Actions top-level run appears stuck while public runtime is healthy, inspect job steps with `gh run view <run-id> --json jobs` and check VM state over SSH before declaring failure. Run status can lag behind job completion briefly.
- Tencent deploy job steps include pull, migration, service replacement, and smoke; Tokyo may take longer due to registry/proxy/network path.
- On Tencent container deployments, `HOSTNAME=127.0.0.1` in `/etc/outbound-agent/front.env` can make Next.js `request.nextUrl.origin` resolve to `https://localhost:3000` when building Gmail OAuth URLs. Always set `GMAIL_OAUTH_REDIRECT_URI` explicitly per VM (`https://outbound-seoul.dev.querypie.io/api/gmail/oauth/callback` or `https://outbound-tokyo.dev.querypie.io/api/gmail/oauth/callback`) and restart `outbound-front` before judging Google `redirect_uri_mismatch` errors.
- To smoke Gmail OAuth without completing consent, create/use a valid dev session cookie, call `/api/gmail/oauth/connect?teamSlug=sales-demo&returnPath=%2Fsales-demo%2Fsettings%2Femail-senders`, inspect the 307 `Location`, and verify the encoded `redirect_uri` plus a Google authorization fetch that does not contain `redirect_uri_mismatch` or `Error 400`. Do not print OAuth secrets while checking env presence.

## References

- `references/three-dev-environment-deploy-and-db-readiness.md` — session-derived checklist and verification signals for the three development environments.
- `references/gmail-oauth-dev-runtime-config.md` — Gmail OAuth redirect URI, env, Vercel, Tencent VM, secret-rotation, and smoke checklist for development environments.
- `references/gmail-oauth-production-deploy-smoke.md` — exact-version Vercel deployment evidence, manual post-merge Production deploy, Google Console access checks, and pre-consent Gmail OAuth-start smoke pattern.
- `references/gmail-oauth-console-evidence-handoff.md` — how to update repo records when the user/operator confirms Google Console redirect URI registration or OAuth consent outside the agent session, including wording to avoid overclaiming send evidence.
