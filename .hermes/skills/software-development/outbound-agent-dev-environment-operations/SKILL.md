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

## Required user-visible progress reporting

For Dev Seoul/Tokyo/Vercel deployment or operations work, progress reporting must be visible to the user as normal chat messages. Tool calls, tool-call labels, hidden commentary, and a detailed final summary do not count as intermediate progress reports.

Use a strict one-step loop:

1. Send a short visible progress message before the operation step: what will be checked or changed, why it matters, expected wait, and whether it is read-only or has side effects.
2. Run only that single step, or a very small group of inseparable commands.
3. Stop and send a visible result message before any next tool call: outcome, evidence handle/run ID/URL/SHA/status, and the next proposed step.
4. Continue only by sending the next visible progress message first.

This is mandatory for deploy dispatches, migration/reset/schema workflows, SSH/TAT commands, service restarts, workflow polling, Vercel inspect/log queries, and smoke tests. Avoid “완료 보고” as the primary reporting pattern; final summaries are allowed only after the visible step-by-step reports have already happened. If a step is likely to wait or poll, state the expected wait, poll once or twice, then report status rather than leaving the user in a black-box wait.

When the task is to add or repair a GitHub Actions E2E workflow for these dev servers, treat “the three dev servers” as already-deployed targets unless the user explicitly asks to deploy or start servers. Use `workflow_dispatch`, a target choice input, deployed base URLs, and browser-only black-box checks by default; do not add PostgreSQL services, Next dev-server startup, Prisma setup, SSH tunnels, or DB secrets for that class of workflow. If the E2E needs authentication, prefer a pre-seeded E2E account and stop/skip at the Email Sender / Gmail OAuth boundary until a non-interactive sender-auth path exists. See `references/deployed-dev-e2e-workflow.md`.

## Core workflow

1. Establish the latest stable `origin/main` SHA.
   - Run `git fetch origin main --prune` and record `git rev-parse origin/main`.
   - During active merge/push windows, `origin/main` may move while workflows are running. Re-fetch repeatedly and wait for the latest SHA to stay stable for about a minute before reporting “latest”.

2. Prefer migrate-only first unless the user explicitly requests a reset.
   - Default path: dispatch DB migration workflows with reset disabled:
     - `Apply outbound-dev DB Migration` with `reset_database=false`
     - `Apply tencent/outbound-seoul DB Migration` with `branch=main`, `reset_database=false`
     - `Apply tencent/outbound-tokyo DB Migration` with `branch=main`, `reset_database=false`
   - Explicit reset request path: if the user says to reset the dev DBs, dispatch the same workflows with `reset_database=true` immediately; do not spend time arguing for migrate-only.
   - After either migration-only or reset+seed, dispatch schema checks:
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
   - For a full browser/runtime verification pass, dispatch `E2E - Runtime Smoke` three times with `base_url` set to each deployed dev URL; this is preferable to hand-rolling Next.js Server Action login POSTs from curl/scripts.
   - For Tencent, verify a DB-backed authenticated route by reading the active `sales-demo` user id from the VM-local PostgreSQL container and calling `/<teamSlug>/home` with `Cookie: outbound_session=<uuid>` when VM-local access is available.
   - For Vercel, submit the rendered login form with `sales-demo` / `outbound-local-demo` and verify redirect to `/sales-demo/home`, session cookie creation, and deployment id in the response when using browser automation or the runtime-smoke workflow.

5. Escalate to reset only after evidence.
   - Reset is appropriate when migration/schema/runtime smoke proves incompatible data or seed drift.
   - Do not reset merely because reset is available.
   - For Tencent reset+seed, dispatch the target migration workflow with `reset_database=true`.
   - For requested DB resets, do not report completion from the workflow conclusion alone. Verify the reset path actually ran (`migrate --reset-data`, `prisma migrate reset --force`, `Database reset successful`, `prisma db seed`, and `The seed command has been executed`), then run the schema check after the reset. When SSH is available, also verify seed row counts directly from the VM-local PostgreSQL container before declaring the DB reset complete.
   - If `origin/main` advances while the operation is in progress, re-record the new SHA and re-check deploy/schema status against that SHA before declaring “latest” complete. If the user requested a strict sequence such as “DB reset 후 최신 배포”, rerun/reconfirm deployment after the final reset+seed, even if the same image was deployed shortly before.
   - If the automatic Tencent main deploy is cancelled or only one VM finishes, rerun the manual `Deploy Tencent container image` workflow with the immutable image tag for the latest SHA. When Gmail OAuth config is part of the incident, set `update_gmail_oauth_config=true` so the VM-local env file and restarted container are refreshed as part of the redeploy.

## Baseline-only clean DB install cleanup

When the user asks to remove DB migration/backfill history and leave only a clean baseline install path, treat it as a repository artifact cleanup plus workflow simplification task, not as a shared-DB repair task.

- Keep only the current-schema Prisma baseline migration and `migration_lock.toml` under `front/prisma/migrations/`.
- Regenerate the baseline from `prisma/schema.prisma`, but preserve the repo-specific PostgreSQL 17-compatible `public.uuidv7()` helper that Prisma diff does not emit.
- Remove intermediate migration directories, one-off `front/prisma/repairs/**`, obsolete backfill SQL, and any SQL-file runner whose only remaining purpose was repair/backfill execution.
- Simplify DB mutation workflows so clean install/reset does not execute repair/backfill SQL: `prisma migrate deploy` for non-reset, `db:reset` + `db:seed` for approved reset, followed by schema drift check.
- Update tests from intermediate-migration assertions to baseline-contract assertions.
- In PR/docs, explicitly state that existing shared DBs that diverge from the baseline should use the approved `reset_database=true` reset/seed path instead of accumulating new repair/backfill artifacts.

See `references/baseline-only-db-install.md` for the exact implementation and verification pattern.

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

## Vercel runtime Prisma TLS pitfalls

When outbound-dev Vercel Preview or Production returns runtime 500 on `/login` with Prisma `P1011` and `Error opening a TLS connection: self-signed certificate in certificate chain`, inspect whether the deployment uses a Supabase pooled `DATABASE_URL` with `sslmode=require`. With `@prisma/adapter-pg` / `pg`, `sslmode=prefer|require|verify-ca` can be treated like stricter verification unless `uselibpqcompat=true` is present. The app runtime must normalize the Prisma pg adapter connection string the same way seed/SQL scripts do; otherwise build/deploy can be green while `/login` fails at runtime. Verification pattern: compare old/new deployment IDs in `vercel logs --project outbound-dev --environment preview --level error --json --no-branch`, check the latest deployment has zero P1011 rows, and run `E2E - Runtime Smoke` against the Preview URL using `--ref <PR branch>` when validating a PR-branch smoke-test change.

## Gmail OAuth runtime config pitfalls

For browser-based dev OAuth smoke, prefer a fresh browser context/profile when verifying a reset or config repair so cached Google sessions and stale app cookies do not mask the actual flow. Verify the product route, selected sender row, OAuth start URL, callback result, and final Email Senders table state. See `references/gmail-oauth-dev-browser-smoke.md`.

For Gmail OAuth token-exchange failures, preserve provider error precedence: report safe Google error/status evidence (`invalid_client`, `invalid_grant`, `redirect_uri_mismatch`) before collapsing to app-level `refresh_token_missing`. See `references/gmail-oauth-token-exchange-diagnostics.md` and `references/gmail-oauth-sender-specific-error-precedence.md`.

When intentionally testing a bad Gmail OAuth client secret on Tencent Seoul/Tokyo, use the same VM-local env-sync workflow path as a real repair: update the GitHub repo secret, dispatch `Deploy Tencent container image` with `update_gmail_oauth_config=true`, and verify each target job's `Upload Gmail OAuth config update` and `Run deployment` steps. To restore, pull the deployed Outbound client from 1Password item `Outbound - OAuth Client - Dev`, section `GCP OAuth Client` (not the local or Deck Dev fields), update `GMAIL_OAUTH_CLIENT_ID` / `GMAIL_OAUTH_CLIENT_SECRET`, and redeploy/restart both VMs. See `references/tencent-gmail-oauth-negative-test-and-restore.md`.

On Tencent container deployments, runtime Gmail OAuth config is sourced from the VM-local root-only file `/etc/outbound-agent/front.env`, not from Vercel project env. A successful main image/code deploy only replaces the container image; it does not update `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`, `GMAIL_TOKEN_ENCRYPTION_SECRET`, or state/redirect-related env values in that file. When Vercel/outbound-dev OAuth env is rotated or repaired, explicitly compare dev-seoul/dev-tokyo fingerprints, update runtime env through the dedicated GitHub Actions option if available, restart/deploy `outbound-front`, and verify authorization URLs. See `references/tencent-gmail-oauth-runtime-env-drift.md`.

For Tencent deployment workflow maintenance, keep Gmail OAuth env sync as an explicit opt-in option, not part of the default main image deploy. Prefer repo-level GitHub Actions secrets as the source consumed by the manual `Deploy Tencent container image` workflow. Keep common Google OAuth client values common only when fingerprints match; keep `GMAIL_TOKEN_ENCRYPTION_SECRET` and `GMAIL_OAUTH_STATE_SECRET` VM-specific if Seoul/Tokyo differ, otherwise one VM's existing encrypted tokens/state behavior can be broken. The workflow option must default off; dry-run should validate secret presence/syntax without changing `/etc/outbound-agent/front.env`; apply should update only Gmail OAuth keys and create a timestamped backup. For urgent repairs, the workflow should support a target choice (`all`, `dev-seoul`, `dev-tokyo`) so one VM's runtime/deploy failure does not block the intended VM's Gmail OAuth config update and restart. See `references/tencent-gmail-oauth-gha-option.md`, `references/tencent-gmail-oauth-gha-secret-sync.md`, and `references/tencent-targeted-gmail-oauth-env-sync.md`.

When `gmail_oauth_token_exchange_failed` is paired with callback diagnostics `tokenResponseStatus: 401` and `providerError: 'invalid_client'`, treat it as a Google token-exchange client credential mismatch, not as redirect URI/state/scope failure. Update `GMAIL_OAUTH_CLIENT_ID` / `GMAIL_OAUTH_CLIENT_SECRET` in GitHub Secrets, apply the Tencent Gmail OAuth env-sync workflow, then retry OAuth. If the workflow exposes a `target` input, use the intended VM directly (for example `target=dev-seoul`) for urgent repairs. If it does not, be careful: the manual `Deploy Tencent container image` workflow may run dev-tokyo before dev-seoul, so a dev-tokyo deploy/runtime failure can skip dev-seoul entirely. If the intended VM was skipped, do not claim its env was updated; verify with the diagnostic workflow. If only a dev-seoul container restart is needed after a prior successful env sync, `Deploy tencent/outbound-seoul` can restart/redeploy the app but does not apply Gmail OAuth env updates. See `references/tencent-gmail-oauth-invalid-client-and-targeted-restart.md` and `references/tencent-targeted-gmail-oauth-env-sync.md`.

If the user explicitly asks to deploy an intentionally wrong `GMAIL_OAUTH_CLIENT_SECRET` for failure-path testing, treat it as a deliberate negative test rather than a repair. Set only the requested GitHub Actions secret, keep values redacted, deploy/restart the current known-good Tencent image with `update_gmail_oauth_config=true`, then verify the config-upload and deployment steps for both requested targets plus public `/login` health. See `references/tencent-gmail-oauth-negative-secret-test.md`.

On Tencent container deployments, `HOSTNAME=127.0.0.1` in `/etc/outbound-agent/front.env` can make Next.js derive `https://localhost:3000` for Gmail OAuth redirects unless the app derives origin from trusted ingress headers. Verify OAuth smoke through the public FQDN, not VM-local `localhost:3000`, before judging Google `redirect_uri_mismatch` errors.

When the Email Senders page returns `gmail=failed&reason=gmail_oauth_token_exchange_failed`, inspect the `gmail_oauth_callback` journal diagnostic before changing config. If the callback reached the app with a Google `code` and the log shows `tokenResponseStatus: 401` plus `providerError: 'invalid_client'`, treat it as a client id/secret mismatch at the token-exchange boundary, not a redirect URI/state/scope problem. First compare Google Console's active Outbound Web OAuth client with the repository secrets and VM-local env fingerprints, then re-apply Tencent runtime env through the opt-in `Deploy Tencent container image` workflow (`update_gmail_oauth_config=true`, dry-run first, then apply). A dry-run only proves secrets are present and shell-parseable; it does not prove the secret matches Google Console. See `references/tencent-gmail-oauth-invalid-client.md`.

## Active Tencent Seoul deploy triage

When the user asks whether Dev Seoul is deploying the latest container image, lead with GitHub Actions evidence and then verify the VM.

- First identify the target `origin/main` SHA/image and inspect recent Tencent deploy/container-image workflow runs with `gh run list` and `gh run view <run-id> --json status,conclusion,headSha,jobs`.
- Base the “currently deploying vs completed” call on GitHub Actions job/step evidence, not only on VM state. When the JSON summary is ambiguous, inspect the relevant Seoul job logs (`gh run view <run-id> --job <job-id> --log`) for the image tag, checkout/revision, pull/restart steps, and smoke/check commands that actually ran.
- Do not infer from the top-level run status alone: inspect the Seoul job and step status. A run can be `in_progress` while Seoul already finished, while another target is still running, or while a newer `main` run supersedes an older one.
- If the Seoul deployment is complete, SSH to verify `/opt/outbound-agent/deployments/current-image`, `/opt/outbound-agent/deployments/current-revision`, `/opt/outbound-agent/repo/.deployed-revision`, service/container status, and only then run public/runtime smoke.
- If the deployment is still in progress or ambiguous, SSH immediately and report the currently served image/revision, container/service health, and recent container/journal errors instead of passively waiting.
- Separate exact-version proof from health proof: public `/login` 200 does not prove the latest image is deployed, and matching VM metadata does not by itself prove the app is smoke-clean.

See `references/tencent-seoul-active-deploy-triage.md` for the command pattern and concise reporting shape.

## Workflow/status pitfalls

- A GitHub Actions top-level run can remain `in_progress` while individual jobs have already finished or while the Tokyo deploy job is still running. Inspect job steps with `gh run view <run-id> --json jobs` before declaring failure.
- Tencent image deployment deploys Seoul before Tokyo in the main image workflow; top-level `in_progress` can mean Seoul is already successfully updated while Tokyo is still in `Run deployment`. Report Seoul and Tokyo job states separately instead of collapsing them into one deployment status.
- Tencent image deployment may deploy Seoul before Tokyo; Tokyo can take longer because of registry/proxy/network path.
- A Tencent deploy can fail after image build/publish but before the VM deployment script runs. If the deploy job log contains `scp: /tmp/outbound-registry.env: No space left on device`, classify the target as not deployed to that latest image; if the sibling target was skipped by job dependencies, classify it as skipped/not attempted rather than healthy. Public `/login` 200 is current-health evidence only, not exact-version proof. See `references/tencent-seoul-tokyo-container-deploy-status-and-disk-full.md`.
- When the disk-full failure needs immediate cleanup and direct SSH from the agent runtime times out, use Tencent TAT if the agent is online. Run `docker image prune -a -f` and `docker builder prune -f` through TAT, preserving existing containers and volumes, then verify disk usage, remaining images, service state, running containers, and public `/login`. See `references/tencent-vm-docker-image-cleanup-via-tat.md`.
- The manual `Deploy Tencent container image` workflow assumes each VM already has the current repo layout under `/opt/outbound-agent/repo`, including `infra/compose.yml`. If a container-image deploy fails on dev-tokyo with `/opt/outbound-agent/repo/infra/compose.yml is required`, first run the repo deploy workflow `Deploy tencent/outbound-tokyo` on `main` to refresh the VM checkout/runtime layout, then rerun `Deploy Tencent container image` with the same image and options. This fixes VM state; it is not a Gmail secret failure.
- For Tencent VM diagnostic workflows, prefer a repo-tracked script that the workflow installs under `/opt/outbound-agent/tools/` and then executes with arguments, rather than keeping long SSH heredocs inline in workflow YAML. This keeps quoting, psql variable interpolation, and shell validation manageable; verify with `bash -n`, `actionlint`, `git diff --check`, and a branch-dispatched workflow run.
- For dev-seoul/dev-tokyo container image disk hygiene, prefer a repo-tracked remote cleanup script plus a `workflow_dispatch`/`workflow_call` GitHub Actions workflow. Keep the newest 10 `ireg.querypie.io/ci/outbound-front` images by default, protect any image referenced by existing containers, delete only old unused image refs, and prune image/build cache without pruning volumes. Wire the cleanup workflow after successful per-target deployments and propagate deploy dry-run into cleanup dry-run. See `references/tencent-container-image-retention-workflow.md`.
- If `#alerts-outbound-dev` receives no deploy Slack message, inspect the `Notify Slack - main deploy started` job before assuming deploy failure or Slack channel problems. A log error like `Missing input! A token must be provided` means repository Actions secret `SLACK_BOT_TOKEN` is missing/empty; verify with `gh secret list --repo querypie/outbound-agent --app actions`, restore the secret from 1Password Dev vault item `Slack App OAuth Token (Ironman)` without printing it, validate `auth.test`/`conversations.info`, then post a short diagnostic message. Already-running deploys whose start notification failed may not send a final update because the result job depends on the start message timestamp. See `references/tencent-dev-deploy-slack-notification-secret.md`.
- During active merge windows, `origin/main` can move while deploy/migration runs are still executing. Re-fetch before final reporting, and if an older Tencent deploy is cancelled by a newer `main` push, follow the newest run rather than treating the cancelled run as a failure.
- If direct SSH from the operator workstation times out while GitHub Actions can still deploy through its runner, classify the SSH result as a local network/security-group ingress limitation rather than app/container failure. Use GHA deploy logs plus public smoke for completion evidence, and use QueryPie ACP seamless SSH or Tencent TAT only when VM-local container/log evidence is still required.
- Documentation-only or path-ignored changes can still move literal latest `main` without auto-deploying every environment. If the user asks for the exact latest version on all three servers, manually dispatch the missing deploy workflow and then rerun migrations/schema checks against the settled latest SHA.
- Avoid long passive waits. Poll once or twice, then report the exact in-progress job and reason if it is still running.
- Public HTTP 200 is not exact-version proof. Always pair runtime smoke with deployment metadata checks.
- For deployed Tencent runtime smoke from `front/playwright.runtime-smoke.config.ts`, use `E2E_BASE_URL` or `PLAYWRIGHT_BASE_URL`; `BASE_URL` is ignored by that config and will fail before tests run.
- Do not trust arbitrary hashes in rendered HTML as deployed git revision unless the app explicitly exposes them as build metadata.

See `references/latest-main-churn-and-dev-deploy-verification.md` for the full pattern from a session where several PRs moved `main`, cancelling older Tencent deploy runs and requiring a final latest-SHA deploy/migrate/schema/smoke pass.

## References

- `references/tencent-targeted-gmail-oauth-env-sync.md` — Target-aware Tencent Gmail OAuth env sync workflow pattern so Seoul/Tokyo can be updated independently when the other VM is unhealthy.
- `references/dev-seed-drift-and-email-templates.md` — Email Template seed drift investigation and reset verification pattern from a dev-seoul incident.
- `references/deployed-dev-e2e-workflow.md` — Pattern for manual GitHub Actions Playwright E2E against the already-deployed dev servers, including seed-user and Email Sender auth-boundary guidance.
- `references/latest-main-churn-and-dev-deploy-verification.md` — Pattern for verifying all three dev servers while `main` is moving, deploy runs are cancelled by concurrency, and migrate/schema/smoke must be repeated on the final latest SHA.
- `references/gmail-oauth-refresh-token-missing.md` — Pattern for debugging Email Senders OAuth reconnect failures where Google omits `refresh_token` after successful authorization.
- `references/tencent-gmail-oauth-gha-secret-sync.md` — Pattern for wiring Tencent Gmail OAuth runtime env updates through opt-in GitHub Actions repo secrets, including VM-specific token/state secrets.
- `references/tencent-gmail-oauth-negative-test-and-restore.md` — Pattern for intentionally deploying a bad Gmail OAuth client secret to validate token-exchange failure, then restoring the correct Outbound client secret from 1Password and redeploying Seoul/Tokyo.
- `references/dev-vercel-reset-after-main-advance.md` — Vercel dev DB reset + latest-main redeploy verification pattern when `origin/main` advances during operations.
- `references/gmail-oauth-dev-browser-smoke.md` — browser-based Gmail OAuth smoke pattern for dev environments after reset/config repair.
- `references/gmail-oauth-token-exchange-diagnostics.md` — preserve Google token endpoint error/status evidence before app-level missing-refresh-token handling.
- `references/gmail-oauth-sender-specific-error-precedence.md` — sender-specific Gmail OAuth error precedence and row/account mismatch guidance.
- `references/gmail-refresh-token-missing-after-dev-db-reset.md` — diagnostics when DB reset removes stored Gmail credentials and Google omits a new refresh token.
- `references/outbound-dev-supabase-seed-tls-compat.md` — Supabase seed/TLS compatibility note for outbound-dev reset workflows.
- `references/tencent-seoul-gmail-oauth-diagnostics.md` — Tencent Seoul Gmail OAuth runtime diagnostics and evidence pattern.
- `references/tencent-vm-ubuntu-docker-group.md` — Tencent VM docker group/user maintenance via TAT/SSH.
- `references/tencent-gmail-oauth-negative-secret-test.md` — Pattern for intentionally deploying a wrong Gmail OAuth client secret to Tencent dev VMs for negative failure-path testing without exposing secret values.
- `references/tencent-seoul-active-deploy-triage.md` — Pattern for determining whether Dev Seoul is actively deploying the latest container image, verifying VM image/container/log state, and choosing smoke vs live-state reporting.
- `references/tencent-container-image-retention-workflow.md` — Repo-tracked GitHub Actions pattern for routine dev-seoul/dev-tokyo image retention cleanup after deployments, keeping newest 10 images and protecting active container images.
- `references/tencent-dev-deploy-slack-notification-secret.md` — Debugging pattern for missing `#alerts-outbound-dev` deploy notifications caused by absent `SLACK_BOT_TOKEN`, including safe secret restoration and Slack API validation.
