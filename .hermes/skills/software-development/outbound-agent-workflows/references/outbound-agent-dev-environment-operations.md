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
   - Current baseline-only migration policy: clean installs should be reproducible from the single committed current-schema baseline plus seed. Do not reintroduce one-off repair/backfill workflow steps for the normal path; if an existing shared dev DB diverges from the baseline, use the explicit reset path and then schema-check. See `references/baseline-only-db-migration-cleanup.md`.

3. Verify exact deployed versions.
   - Vercel/Incheon: use the successful `Deploy outbound-dev Production` run, deployment ID, `vercel inspect <deployment-url> --scope querypie`, aliases, and runtime region. If the workflow log does not print a deployment URL, find the exact production deployment by commit metadata with `vercel ls outbound-dev --scope querypie --prod --meta githubCommitSha=<full-sha> --no-color`, then inspect that URL.
   - Tencent Seoul/Tokyo: SSH and read:
     - `/opt/outbound-agent/deployments/current-image`
     - `/opt/outbound-agent/deployments/current-revision`
     - `/opt/outbound-agent/repo/.deployed-revision`
     - `systemctl is-active outbound-front`
     - `systemctl is-active nginx`

4. Smoke public and DB-backed behavior.
   - Check `/login` for all three public URLs.
   - For a full browser/runtime verification pass, dispatch `E2E - Runtime Smoke` three times with `base_url` set to each deployed dev URL; this is preferable to hand-rolling Next.js Server Action login POSTs from curl/scripts. Do not assume the main Tencent deploy workflow smokes every target: verify which smoke jobs actually appeared, and manually dispatch the runtime-smoke workflow for any deployed target that lacks a smoke result, especially dev-tokyo.
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

See `references/baseline-only-db-install.md` for the exact implementation and verification pattern, including legacy repair/backfill removal and UUID/schema verification checks.

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

When querying a specific Vercel deployment URL with filters such as `--limit`, `--since`, or `--level`, add `--no-follow`. The Vercel CLI implicitly enables follow mode for deployment URL/ID arguments, and follow mode rejects filters.

## Gmail OAuth runtime config pitfalls

For browser-based dev OAuth smoke, prefer a fresh browser context/profile when verifying a reset or config repair so cached Google sessions and stale app cookies do not mask the actual flow. Verify the product route, selected sender row, OAuth start URL, callback result, and final Email Senders table state. See `references/gmail-oauth-dev-browser-smoke.md`.

For Gmail OAuth token-exchange failures, preserve provider error precedence: report safe Google error/status evidence (`invalid_client`, `invalid_grant`, `redirect_uri_mismatch`) before collapsing to app-level `refresh_token_missing`. See `references/gmail-oauth-token-exchange-diagnostics.md` and `references/gmail-oauth-sender-specific-error-precedence.md`.

When intentionally testing a bad Gmail OAuth client secret on Tencent Seoul/Tokyo, use the same VM-local env-sync workflow path as a real repair: update the GitHub repo secret, dispatch `Deploy Tencent container image` with `update_gmail_oauth_config=true`, and verify each target job's `Upload Gmail OAuth config update` and `Run deployment` steps. To restore, pull the deployed Outbound client from 1Password item `Outbound - OAuth Client - Dev`, section `GCP OAuth Client` (not the local or Deck Dev fields), update `GMAIL_OAUTH_CLIENT_ID` / `GMAIL_OAUTH_CLIENT_SECRET`, and redeploy/restart both VMs. See `references/tencent-gmail-oauth-negative-test-and-restore.md`.

On Tencent container deployments, runtime Gmail OAuth config is sourced from the VM-local root-only file `/etc/outbound-agent/front.env`, not from Vercel project env. A successful main image/code deploy only replaces the container image; it does not update `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`, `GMAIL_TOKEN_ENCRYPTION_SECRET`, or state/redirect-related env values in that file. When Vercel/outbound-dev OAuth env is rotated or repaired, explicitly compare dev-seoul/dev-tokyo fingerprints, update runtime env through the dedicated GitHub Actions option if available, restart/deploy `outbound-front`, and verify authorization URLs. See `references/tencent-gmail-oauth-runtime-env-drift.md`.

For Tencent deployment workflow maintenance, keep Gmail OAuth env sync as an explicit opt-in option, not part of the default main image deploy. Prefer repo-level GitHub Actions secrets as the source consumed by the manual `Deploy Tencent container image` workflow. Keep common Google OAuth client values common only when fingerprints match; keep `GMAIL_TOKEN_ENCRYPTION_SECRET` and `GMAIL_OAUTH_STATE_SECRET` VM-specific if Seoul/Tokyo differ, otherwise one VM's existing encrypted tokens/state behavior can be broken. The workflow option must default off; dry-run should validate secret presence/syntax without changing `/etc/outbound-agent/front.env`; apply should update only Gmail OAuth keys and create a timestamped backup. For urgent repairs, the workflow should support a target choice (`all`, `dev-seoul`, `dev-tokyo`) so one VM's runtime/deploy failure does not block the intended VM's Gmail OAuth config update and restart. See `references/tencent-gmail-oauth-gha-option.md` and `references/tencent-targeted-gmail-oauth-env-sync.md`.

When `gmail_oauth_token_exchange_failed` is paired with callback diagnostics `tokenResponseStatus: 401` and `providerError: 'invalid_client'`, treat it as a Google token-exchange client credential mismatch, not as redirect URI/state/scope failure. Update `GMAIL_OAUTH_CLIENT_ID` / `GMAIL_OAUTH_CLIENT_SECRET` in GitHub Secrets, apply the Tencent Gmail OAuth env-sync workflow, then retry OAuth. If the workflow exposes a `target` input, use the intended VM directly (for example `target=dev-seoul`) for urgent repairs. If it does not, be careful: the manual `Deploy Tencent container image` workflow may run dev-tokyo before dev-seoul, so a dev-tokyo deploy/runtime failure can skip dev-seoul entirely. If the intended VM was skipped, do not claim its env was updated; verify with the diagnostic workflow. If only a dev-seoul container restart is needed after a prior successful env sync, `Deploy tencent/outbound-seoul` can restart/redeploy the app but does not apply Gmail OAuth env updates. See `references/tencent-gmail-oauth-invalid-client.md` and `references/tencent-targeted-gmail-oauth-env-sync.md`.

If the user explicitly asks to deploy an intentionally wrong `GMAIL_OAUTH_CLIENT_SECRET` for failure-path testing, treat it as a deliberate negative test rather than a repair. Set only the requested GitHub Actions secret, keep values redacted, deploy/restart the current known-good Tencent image with `update_gmail_oauth_config=true`, then verify the config-upload and deployment steps for the requested targets plus public `/login` health. See `references/tencent-gmail-oauth-negative-test-and-restore.md`.

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

- When editing DB migration workflow summary/copy in `.github/workflows/apply-outbound-dev-db-migration.yml`, check source-based tests that assert workflow text before pushing. In particular, `front/src/__tests__/schema-migration-artifacts.test.ts` may assert the exact run-summary wording. If CI fails in `Front app CI` after a wording-only workflow change, inspect the assertion before changing workflow behavior; update the test expectation to the new intended contract and rerun the focused test (`npm test -- --run src/__tests__/schema-migration-artifacts.test.ts`).
- A GitHub Actions top-level run can remain `in_progress` while individual jobs have already finished or while the Tokyo deploy job is still running. Inspect job-level state with `gh run view <run-id> --json jobs` before declaring failure. If `gh run view` is slow/hangs during active runs, switch to lightweight REST polling with `gh api repos/querypie/outbound-agent/actions/runs/<run-id>` and `/jobs --paginate` rather than waiting silently.
- `gh run view --job <job-id> --log` may refuse logs for an in-progress job (`logs will be available when it is complete`). Treat that as a GitHub log-availability limitation, not as deploy failure; use job state, public health, and later completed logs instead.
- Tencent image deployment deploys Seoul before Tokyo in the main image workflow; top-level `queued` or `in_progress` can mean Seoul is already successfully updated and smoke-clean while Tokyo is still queued or in `Run deployment`. Report Seoul and Tokyo job states separately instead of collapsing them into one deployment status.
- During an active sequential main deploy, pair job-level GitHub Actions state with VM metadata (`current-image`, `current-revision`, `.deployed-revision`, services, containers) and public `/login` health. Classify a target with `/login` 200 but an older VM revision as `healthy but not latest yet`, not as failure or success. See `references/tencent-sequential-main-deploy-live-status.md`.
- Tencent image deployment may deploy Seoul before Tokyo; Tokyo can take longer because of registry/proxy/network path.
- A Tencent deploy can fail after image build/publish but before the VM deployment script runs. If the deploy job log contains `scp: /tmp/outbound-registry.env: No space left on device`, classify the target as not deployed to that latest image; if the sibling target was skipped by job dependencies, classify it as skipped/not attempted rather than healthy. Public `/login` 200 is current-health evidence only, not exact-version proof. See `references/tencent-seoul-tokyo-container-deploy-status-and-disk-full.md`.
- A Tencent deploy can also succeed at image/revision/service level while authenticated routes return 500 because a non-secret runtime config file existed during build/Vercel deploy but was omitted from the Docker runner stage. If logs show `ENOENT` for a path such as `/app/front/config/system-access.yaml`, inspect `front/Dockerfile` runner-stage `COPY --from=builder` lines before resetting DB or redeploying blindly. See `references/tencent-container-runtime-config-file-packaging.md`.
- A Tencent Dev Seoul deploy can also succeed at exact image/revision/service level while authenticated routes or runtime smoke fail because the VM-local PostgreSQL schema is older than the repo's current single-baseline Prisma schema. If logs show Prisma `P2021` with a missing table such as `public.UserIdentity` or `public.DryRunSenderSettings`, verify the table and `_prisma_migrations` directly, then use the explicit reset+seed path (`Apply tencent/outbound-seoul DB Migration` with `reset_database=true`), followed by schema check and runtime smoke or the exact affected authenticated route. Migrate-only may not repair this when the baseline migration name is already recorded as applied. See `references/tencent-seoul-baseline-schema-drift-reset.md`.
- When the disk-full failure needs immediate cleanup and direct SSH from the agent runtime times out, use Tencent TAT if the agent is online. Run `docker image prune -a -f` and `docker builder prune -f` through TAT, preserving existing containers and volumes, then verify disk usage, remaining images, service state, running containers, and public `/login`. See `references/tencent-vm-docker-image-cleanup-via-tat.md`.
- The manual `Deploy Tencent container image` workflow assumes each VM already has the current repo layout under `/opt/outbound-agent/repo`, including `infra/compose.yml`. If a container-image deploy fails on dev-tokyo with `/opt/outbound-agent/repo/infra/compose.yml is required`, first run the repo deploy workflow `Deploy tencent/outbound-tokyo` on `main` to refresh the VM checkout/runtime layout, then rerun `Deploy Tencent container image` with the same image and options. This fixes VM state; it is not a Gmail secret failure.
- For Tencent VM diagnostic workflows, prefer a repo-tracked script that the workflow installs under `/opt/outbound-agent/tools/` and then executes with arguments, rather than keeping long SSH heredocs inline in workflow YAML. This keeps quoting, psql variable interpolation, and shell validation manageable; verify with `bash -n`, `actionlint`, `git diff --check`, and a branch-dispatched workflow run.
- For dev-seoul/dev-tokyo container image disk hygiene, prefer a repo-tracked remote cleanup script plus a `workflow_dispatch`/`workflow_call` GitHub Actions workflow. Keep the newest 10 `ireg.querypie.io/ci/outbound-front` images by default, protect any image referenced by existing containers, delete only old unused image refs, and prune image/build cache without pruning volumes. Wire the cleanup workflow after successful per-target deployments and propagate deploy dry-run into cleanup dry-run. See `references/tencent-container-image-retention-workflow.md`.
- If `#alerts-outbound-dev` receives no deploy Slack message, inspect the `Notify Slack - main deploy started` job before assuming deploy failure or Slack channel problems. A log error like `Missing input! A token must be provided` means repository Actions secret `SLACK_BOT_TOKEN` is missing/empty; verify with `gh secret list --repo querypie/outbound-agent --app actions`, restore the secret from 1Password Dev vault item `Slack App OAuth Token (Ironman)` without printing it, validate `auth.test`/`conversations.info`, then post a short diagnostic message. Already-running deploys whose start notification failed may not send a final update because the result job depends on the start message timestamp. See `references/tencent-dev-deploy-slack-notification-secret.md`.
- When maintaining the `#alerts-outbound-dev` main deploy Slack workflow, treat the notification contract as code + spec + runbook: update `.github/actions/notify-slack/action.yml`, `.github/workflows/build-outbound-front-image.yml`, `openspec/specs/infra-dev-notification/spec.md`, `infra/notification/README.md`, and the source-structure test `front/src/__tests__/container-deployment-artifacts.test.ts` together. Prefer Slack built-in emoji names over Deck-derived/custom git-icon emoji so the alert does not depend on workspace custom emoji. If the desired policy is “only failures remain visible,” update the final message first, wait 30 seconds, then call Slack `chat.delete` only for `success`/`cancelled`; keep `failure` messages for troubleshooting. Verify with `actionlint` on the workflow YAML, YAML parsing for both workflow/action files, and the focused container-deployment artifact test rather than running the full local build.
- During active merge windows, `origin/main` can move while deploy/migration runs are still executing. Re-fetch before final reporting, and if an older Tencent deploy is cancelled by a newer `main` push, follow the newest run rather than treating the cancelled run as a failure.
- In main-churn status checks, separate Vercel and Tencent timelines: Vercel may reach `Ready` and attach `outbound-dev.vercel.app` for a superseded SHA while a newer SHA starts building; Tencent may show image publish `cancelled` and Seoul/Tokyo deploy `skipped` for that superseded SHA. Classify Seoul/Tokyo `/login` 200 as public health only until the newest run reaches and completes the per-target deploy jobs. If runs remain in progress and the user did not ask to block, provide an interim diagnosis and start a short watcher instead of waiting silently. See `references/main-churn-interim-deploy-diagnosis.md`.
- If direct SSH from the operator workstation times out while GitHub Actions can still deploy through its runner, classify the SSH result as a local network/security-group ingress limitation rather than app/container failure. Use GHA deploy logs plus public smoke for completion evidence, and use QueryPie ACP seamless SSH or Tencent TAT only when VM-local container/log evidence is still required.
- Documentation-only or path-ignored changes can still move literal latest `main` without auto-deploying every environment. If the user asks for the exact latest version on all three servers, manually dispatch the missing deploy workflow and then rerun migrations/schema checks against the settled latest SHA.
- Avoid long passive waits. Poll once or twice, then report the exact in-progress job and reason if it is still running. If manually dispatched `E2E - Runtime Smoke` runs are still `in_progress`, inspect job steps via the Actions jobs API before diagnosing the app: if all targets are stuck in setup steps such as `Set up Node.js` and `Run runtime smoke E2E` has not started, classify it as runner/setup progress rather than application smoke failure, report the run IDs, and use a background watcher instead of blocking the chat.
- Public HTTP 200 is not exact-version proof. Always pair runtime smoke with deployment metadata checks.
- For deployed Tencent runtime smoke from `front/playwright.runtime-smoke.config.ts`, use `E2E_BASE_URL` or `PLAYWRIGHT_BASE_URL`; `BASE_URL` is ignored by that config and will fail before tests run.
- If Tencent `/login` is 200 but runtime smoke fails after login with Home showing `Internal Server Error`, inspect `docker logs outbound-front` for missing packaged config files. One observed failure on Dev Seoul was `ENOENT: no such file or directory, open '/app/front/config/system-access.yaml'`, meaning the latest image was deployed but authenticated SSR was broken by a missing file in the container image.
- Do not trust arbitrary hashes in rendered HTML as deployed git revision unless the app explicitly exposes them as build metadata.
- If runtime smoke fails only on a hard-coded UI assertion after the test has already reached `/.../home` and a visible H1, classify it separately from server-runtime failure. Compare the same smoke on Vercel and Tencent: identical failures such as missing `Setup checklist` heading usually indicate smoke-test/UI-data assertion drift, not a reason to reset DB or redeploy blindly. Use the Playwright artifact/error context to identify the expected text and then decide whether the test or product UI contract needs updating.
- However, do not stop at the Playwright assertion when authenticated smoke fails after login. SSH to Dev Seoul/Tokyo and inspect `docker logs outbound-front` plus VM-local PostgreSQL schema. If logs show Prisma `P2021` for a missing table such as `public.UserIdentity` while the VM is serving the intended image/revision and public `/login` is 200, classify it as shared dev DB schema drift under the baseline-only policy. Existing DBs that already recorded the baseline migration will not replay a revised baseline; use the approved reset+seed path, then schema-check and rerun runtime smoke. See `references/tencent-seoul-useridentity-schema-drift.md`.
- The same baseline-only drift pattern can occur on Vercel/outbound-dev even when Vercel deployment, alias, `/login`, and recent error logs are clean. If `Apply outbound-dev DB Migration` with `reset_database=false` reports `No pending migrations to apply` but the built-in schema check wants to create `UserIdentityProviderType`, `UserIdentity`, and make `User.username` / `User.passwordHash` nullable, classify it as existing outbound-dev DB baseline drift. Escalate to the approved `reset_database=true` reset+seed path, verify the reset and seed log lines, then run `Check outbound-dev DB Schema` and `E2E - Runtime Smoke` for `https://outbound-dev.vercel.app`. See `references/vercel-useridentity-baseline-schema-drift.md`.
- The same baseline-recorded-but-schema-drift pattern can affect Vercel/outbound-dev even when Vercel deploy is Ready, `/login` returns 200, and recent Vercel runtime error logs are empty. If `Apply outbound-dev DB Migration` with `reset_database=false` reports `No pending migrations to apply` but then fails `Check schema after migration` with drift SQL for `UserIdentityProviderType`, `UserIdentity`, or nullable `User.username` / `User.passwordHash`, classify it as outbound-dev baseline drift rather than a deploy/runtime failure. For dev recovery, dispatch the same workflow with `reset_database=true`, then verify that reset and seed actually ran, run the outbound-dev schema check, and rerun runtime smoke against `https://outbound-dev.vercel.app`. See `vercel-querypie-ops/references/outbound-dev-db-reset-and-smoke.md`.
- When a main Tencent deploy fails in the dev-seoul smoke job, downstream dev-tokyo deploy jobs can be skipped even though dev-tokyo `/login` remains 200 on the older image. Report Tokyo as “public health OK, latest SHA not deployed/skipped” until an exact-version deploy and smoke are completed.
- When simplifying outbound-agent DB migration workflows to a single baseline, keep workflow summaries current and operation-oriented. Avoid carrying stale feature-track wording such as `UUID v7 ID migration` after that migration has been completed/archived; prefer wording like `Schema mode: single baseline migration; reset_database=true runs a clean reset and seed`. Also avoid phrasing like `then rerun seed` when the workflow itself already runs seed.
- When a feature-track plan is verified complete during a migration/schema cleanup PR, move the planning document from `docs/feature/` to `docs/done/`, change its status to `Done`, add concise completion evidence, remove it from active feature indexes, and update `docs/feature-status.md` counts/status rows so stale `In-Progress` entries do not remain.

For active main churn, use the consolidated rules above: re-fetch before declaring latest, classify superseded/cancelled runs separately from runtime failure, and dispatch a watcher instead of waiting silently when jobs remain in progress.

## References

- `references/tencent-container-runtime-config-file-packaging.md` — Diagnose Tencent container deployments where exact image/revision is current but authenticated routes 500 because a runtime config file such as `front/config/system-access.yaml` was not copied into the Docker runner image.
- `references/tencent-seoul-baseline-schema-drift-reset.md` — Diagnose and repair Dev Seoul baseline schema drift, especially Prisma `P2021` missing-table errors such as `public.UserIdentity` after single-baseline migration changes.
- `references/tencent-targeted-gmail-oauth-env-sync.md` — Target-aware Tencent Gmail OAuth env sync workflow pattern so Seoul/Tokyo can be updated independently when the other VM is unhealthy.
- `references/dev-seed-drift-and-email-templates.md` — Email Template seed drift investigation and reset verification pattern from a dev-seoul incident.
- `references/deployed-dev-e2e-workflow.md` — Pattern for manual GitHub Actions Playwright E2E against the already-deployed dev servers, including seed-user and Email Sender auth-boundary guidance.
- `references/gmail-oauth-refresh-token-missing.md` — Pattern for debugging Email Senders OAuth reconnect failures where Google omits `refresh_token` after successful authorization.
- `references/tencent-gmail-oauth-negative-test-and-restore.md` — Pattern for intentionally deploying a bad Gmail OAuth client secret to validate token-exchange failure, then restoring the correct Outbound client secret from 1Password and redeploying Seoul/Tokyo.
- `references/dev-vercel-reset-after-main-advance.md` — Vercel dev DB reset + latest-main redeploy verification pattern when `origin/main` advances during operations.
- `references/gmail-oauth-dev-browser-smoke.md` — browser-based Gmail OAuth smoke pattern for dev environments after reset/config repair.
- `references/gmail-oauth-token-exchange-diagnostics.md` — preserve Google token endpoint error/status evidence before app-level missing-refresh-token handling.
- `references/gmail-oauth-sender-specific-error-precedence.md` — sender-specific Gmail OAuth error precedence and row/account mismatch guidance.
- `references/three-environment-deploy-verification.md` — Concrete post-merge verification pattern across Vercel, dev-seoul, and dev-tokyo, including latest remote SHA selection, Vercel commit-metadata lookup, `gh api` polling, Tencent VM exact-version checks, and manual Tokyo smoke when needed.
- `references/gmail-refresh-token-missing-after-dev-db-reset.md` — diagnostics when DB reset removes stored Gmail credentials and Google omits a new refresh token.
- `references/outbound-dev-supabase-seed-tls-compat.md` — Supabase seed/TLS compatibility note for outbound-dev reset workflows.
- `references/outbound-dev-baseline-drift-reset-seed.md` — Vercel/outbound-dev recovery pattern when deploy and `/login` are healthy but migrate-only fails at schema check because a revised single baseline migration will not replay against an existing shared dev DB.
- `references/tencent-seoul-gmail-oauth-diagnostics.md` — Tencent Seoul Gmail OAuth runtime diagnostics and evidence pattern.
- `references/tencent-vm-ubuntu-docker-group.md` — Tencent VM docker group/user maintenance via TAT/SSH.
- `references/tencent-seoul-active-deploy-triage.md` — Pattern for determining whether Dev Seoul is actively deploying the latest container image, verifying VM image/container/log state, and choosing smoke vs live-state reporting.
- `references/vercel-useridentity-baseline-schema-drift.md` — Vercel/outbound-dev baseline-only schema drift recovery when `migrate deploy` has no pending migrations but schema check requires `UserIdentity` changes; use reset+seed, schema check, and runtime smoke verification.
- `references/tencent-container-image-retention-workflow.md` — Repo-tracked GitHub Actions pattern for routine dev-seoul/dev-tokyo image retention cleanup after deployments, keeping newest 10 images and protecting active container images.
- `references/tencent-dev-deploy-slack-notification-secret.md` — Debugging pattern for missing `#alerts-outbound-dev` deploy notifications caused by absent `SLACK_BOT_TOKEN`, including safe secret restoration and Slack API validation.
