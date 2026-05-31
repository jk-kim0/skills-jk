---
name: outbound-agent-dev-environment-operations
description: Operate querypie/outbound-agent development deployments across Vercel/Incheon and Tencent Seoul/Tokyo, including latest-version checks, DB migrations, schema checks, reset/seed escalation, and runtime smoke.
version: 1.0.0
metadata:
  hermes:
    tags: [outbound-agent, deployment, db-migration, db-seed, tencent-vm, vercel, runtime-smoke]
---

# Outbound Agent Dev Environment Operations

Use this skill when the user asks to verify, deploy, migrate, reset, seed, or smoke-test the three Outbound Agent development environments:

- Vercel/Incheon: `https://outbound-dev.vercel.app/login`
- Tencent Seoul: `https://outbound-seoul.dev.querypie.io/login`
- Tencent Tokyo: `https://outbound-tokyo.dev.querypie.io/login`

This skill is for environment operations, not feature implementation. Keep secrets out of chat, logs, docs, PR bodies, and skills.

When the task is to add or repair a GitHub Actions E2E workflow for these dev servers, treat “the three dev servers” as already-deployed targets unless the user explicitly asks to deploy or start servers. Use `workflow_dispatch`, a target choice input, deployed base URLs, and browser-only black-box checks by default; do not add PostgreSQL services, Next dev-server startup, Prisma setup, SSH tunnels, or DB secrets for that class of workflow. If the E2E needs authentication, prefer a pre-seeded E2E account and stop/skip at the Email Sender / Gmail OAuth boundary until a non-interactive sender-auth path exists. See `references/deployed-dev-e2e-workflow.md`.

## Core workflow

1. Establish the latest stable `origin/main` SHA.
   - Run `git fetch origin main --prune` and record `git rev-parse origin/main`.
   - During active merge/push windows, `origin/main` may move while workflows are running. Re-fetch repeatedly and wait for the latest SHA to stay stable for about a minute before reporting “latest”.

2. Prefer migrate-only first.
   - Dispatch DB migration workflows with reset disabled:
     - `Apply outbound-dev DB Migration` with `reset_database=false`
     - `Apply tencent/outbound-seoul DB Migration` with `branch=main`, `reset_database=false`
     - `Apply tencent/outbound-tokyo DB Migration` with `branch=main`, `reset_database=false`
   - Then dispatch schema checks:
     - `Check outbound-dev DB Schema` with `vercel_environment=production`, `check_mode=true`
     - `Check tencent/outbound-seoul DB Schema` with `branch=main`
     - `Check tencent/outbound-tokyo DB Schema` with `branch=main`

3. Verify exact deployed versions.
   - Vercel/Incheon: use the successful `Deploy outbound-dev Production` run, deployment ID, `vercel inspect <deployment-url> --scope querypie`, aliases, and runtime region.
   - Tencent Seoul/Tokyo: SSH and read:
     - `/opt/outbound-agent/deployments/current-image`
     - `/opt/outbound-agent/deployments/current-revision`
     - `/opt/outbound-agent/repo/.deployed-revision`
     - `systemctl is-active outbound-front`
     - `systemctl is-active nginx`

4. Smoke public and DB-backed behavior.
   - Check `/login` for all three public URLs.
   - For Tencent, verify a DB-backed authenticated route by reading the active `sales-demo` user id from the VM-local PostgreSQL container and calling `/<teamSlug>/home` with `Cookie: outbound_session=<uuid>`.
   - For Vercel, submit the rendered login form with `sales-demo` / `outbound-local-demo` and verify redirect to `/sales-demo/home`, session cookie creation, and deployment id in the response when available.

5. Escalate to reset only after evidence.
   - Reset is appropriate when migration/schema/runtime smoke proves incompatible data or seed drift.
   - Do not reset merely because reset is available.
   - For Tencent reset+seed, dispatch the target migration workflow with `reset_database=true`.

## Seed-data drift checklist

Migration-only does not apply seed fixtures. If a user reports a missing demo object, inspect the DB before assuming a UI bug.

For dev-seoul/dev-tokyo, use VM-local PostgreSQL in `outbound-agent-postgres` and check counts for relevant tables. For Email Template issues, specifically check:

- `EmailTemplate`
- `EmailTemplateVersion`
- `Team`
- `TeamMembership`

Important Outbound Agent seed behavior:

- Current seed resets local/dev data and then recreates all demo fixtures.
- Email Template fixtures are team-scoped to `querypie-jp`, `querypie-kr`, and `querypie-us`, not the `sales-demo` personal team.
- After a correct seed, expected Email Template data is 9 templates and 9 versions: 3 each for QueryPie JP/KR/US.
- `/sales-demo/email-templates` can legitimately show 0 templates even when seed is correct; verify `/querypie-jp/email-templates`, `/querypie-kr/email-templates`, and `/querypie-us/email-templates` before declaring failure.

## Gmail OAuth runtime config pitfalls

On Tencent container deployments, runtime Gmail OAuth config is sourced from the VM-local root-only file `/etc/outbound-agent/front.env`, not from Vercel project env. A successful main image/code deploy only replaces the container image; it does not update `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`, `GMAIL_TOKEN_ENCRYPTION_SECRET`, or state/redirect-related env values in that file. When Vercel/outbound-dev OAuth env is rotated or repaired, explicitly compare dev-seoul/dev-tokyo fingerprints, update runtime env through the dedicated GitHub Actions option if available, restart/deploy `outbound-front`, and verify authorization URLs. See `references/tencent-gmail-oauth-runtime-env-drift.md`.

For Tencent deployment workflow maintenance, keep Gmail OAuth env sync as an explicit opt-in option, not part of the default main image deploy. Prefer repo-level GitHub Actions secrets as the source consumed by the manual `Deploy Tencent container image` workflow. Keep common Google OAuth client values common only when fingerprints match; keep `GMAIL_TOKEN_ENCRYPTION_SECRET` and `GMAIL_OAUTH_STATE_SECRET` VM-specific if Seoul/Tokyo differ, otherwise one VM's existing encrypted tokens/state behavior can be broken. The workflow option must default off; dry-run should validate secret presence/syntax without changing `/etc/outbound-agent/front.env`; apply should update only Gmail OAuth keys and create a timestamped backup. See `references/tencent-gmail-oauth-gha-option.md` and `references/tencent-gmail-oauth-gha-secret-sync.md`.

On Tencent container deployments, `HOSTNAME=127.0.0.1` in `/etc/outbound-agent/front.env` can make Next.js derive `https://localhost:3000` for Gmail OAuth redirects unless the app derives origin from trusted ingress headers. Verify OAuth smoke through the public FQDN, not VM-local `localhost:3000`, before judging Google `redirect_uri_mismatch` errors.

## Workflow/status pitfalls

- A GitHub Actions top-level run can remain `in_progress` while individual jobs have already finished or while the Tokyo deploy job is still running. Inspect job steps with `gh run view <run-id> --json jobs` before declaring failure.
- Tencent image deployment may deploy Seoul before Tokyo; Tokyo can take longer because of registry/proxy/network path.
- During active merge windows, `origin/main` can move while deploy/migration runs are still executing. Re-fetch before final reporting, and if an older Tencent deploy is cancelled by a newer `main` push, follow the newest run rather than treating the cancelled run as a failure.
- Documentation-only or path-ignored changes can still move literal latest `main` without auto-deploying every environment. If the user asks for the exact latest version on all three servers, manually dispatch the missing deploy workflow and then rerun migrations/schema checks against the settled latest SHA.
- Avoid long passive waits. Poll once or twice, then report the exact in-progress job and reason if it is still running.
- Public HTTP 200 is not exact-version proof. Always pair runtime smoke with deployment metadata checks.
- Do not trust arbitrary hashes in rendered HTML as deployed git revision unless the app explicitly exposes them as build metadata.

See `references/latest-main-churn-and-dev-deploy-verification.md` for the full pattern from a session where several PRs moved `main`, cancelling older Tencent deploy runs and requiring a final latest-SHA deploy/migrate/schema/smoke pass.

## References

- `references/dev-seed-drift-and-email-templates.md` — Email Template seed drift investigation and reset verification pattern from a dev-seoul incident.
- `references/deployed-dev-e2e-workflow.md` — Pattern for manual GitHub Actions Playwright E2E against the already-deployed dev servers, including seed-user and Email Sender auth-boundary guidance.
- `references/latest-main-churn-and-dev-deploy-verification.md` — Pattern for verifying all three dev servers while `main` is moving, deploy runs are cancelled by concurrency, and migrate/schema/smoke must be repeated on the final latest SHA.
- `references/gmail-oauth-refresh-token-missing.md` — Pattern for debugging Email Senders OAuth reconnect failures where Google omits `refresh_token` after successful authorization.
- `references/tencent-gmail-oauth-gha-secret-sync.md` — Pattern for wiring Tencent Gmail OAuth runtime env updates through opt-in GitHub Actions repo secrets, including VM-specific token/state secrets.
