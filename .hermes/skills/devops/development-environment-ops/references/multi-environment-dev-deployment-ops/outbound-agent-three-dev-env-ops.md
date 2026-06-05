# Outbound Agent three-development-environment operations

This reference captures concrete details from an Outbound Agent session where the user repeatedly asked to confirm the latest deployment, run migrations, and reset/redeploy only if broken.

## Environments

- Vercel/Incheon: `https://outbound-dev.vercel.app/login`
- Tencent Seoul VM: `https://outbound-seoul.dev.querypie.io/login`
- Tencent Tokyo VM: `https://outbound-tokyo.dev.querypie.io/login`

## Canonical workflow classes

Migration workflows:

- `Apply outbound-dev DB Migration`
- `Apply tencent/outbound-seoul DB Migration`
- `Apply tencent/outbound-tokyo DB Migration`

Schema check workflows:

- `Check outbound-dev DB Schema`
- `Check tencent/outbound-seoul DB Schema`
- `Check tencent/outbound-tokyo DB Schema`

Deployment workflows:

- `Deploy outbound-dev Production`
- `PR Cache-Only Build Validation / Main Deploy outbound-front image`
- `Deploy Tencent container image`

## Latest-SHA stabilization pattern

During the session, `origin/main` moved several times while migrations and deployments were already running.
The durable lesson is not any particular SHA; it is the sequence:

1. `git fetch origin main --prune`.
2. Record `git rev-parse origin/main`.
3. If recent pushes are occurring, poll for about one minute and require the SHA to stay unchanged.
4. Dispatch migration/schema/deploy checks only for that stabilized SHA.
5. Re-fetch once before final reporting.
6. If the SHA changed mid-task, rerun migration/schema checks for the new final SHA before saying all environments are current.

## Tencent VM exact deployment signals

Use SSH and read both container deployment metadata and repo-local revision metadata:

- `/opt/outbound-agent/deployments/current-revision`
- `/opt/outbound-agent/deployments/current-image`
- `/opt/outbound-agent/repo/.deployed-revision`
- `systemctl is-active outbound-front`
- `systemctl is-active nginx`

A healthy expected image tag shape is:

- `ireg.querypie.io/ci/outbound-front:<7-char-sha>`

Do not rely on `/login` HTTP 200 alone for exact version verification.

## Vercel exact deployment signals

Use the production deploy workflow log to identify the deployment ID and URL, then inspect it:

- deployment status is `Ready`
- target is `production`
- alias includes `https://outbound-dev.vercel.app`
- build/runtime region is visible, e.g. `icn1`

If the app renders a deployment marker such as `data-dpl-id`, compare it to the inspected deployment ID as an additional runtime proof.

## Runtime smoke pattern

Public smoke:

- `GET /login` should return HTTP 200 on all three environments.

DB-backed/authenticated smoke:

- For Tencent VMs, safely obtain a seeded dev user id from the local Postgres container and call a lightweight team page with the session cookie.
- Example shape: `Cookie: outbound_session=<seed-user-id>` then `GET /sales-demo/home`.
- For Vercel, submit the rendered login form using the fixture account and verify redirect/final page `/sales-demo/home`, session cookie creation, and deployment marker if available.

Keep fixture secrets and environment secrets out of durable notes and chat unless they are already public repo-local dev fixtures.

## Reset escalation

Reset was not used in the session because all migration, schema, deployment, and runtime checks succeeded.
Future runs should follow the same escalation rule:

- reset only after a concrete migration/schema/runtime failure indicates incompatible dev data or schema state;
- do not reset for a mere deployment revision mismatch;
- redeploy first when revision/image is stale;
- report explicitly whether reset was required and whether it was performed.

## Gmail OAuth runtime pitfall

For this specific app class, Tencent VM container deployments can generate a wrong Google OAuth `redirect_uri` if the app derives origin from runtime host settings.
Set an explicit per-environment `GMAIL_OAUTH_REDIRECT_URI` in the VM runtime env and restart the app service.
Verify OAuth start by inspecting the Google authorization URL’s encoded `redirect_uri`, without printing secrets.

Also verify OAuth client configuration parity separately from latest-code deployment and DB migration:

- compare the effective OAuth start redirect URL in each dev environment;
- report only redacted/fingerprinted `client_id` values;
- verify the per-environment callback `redirect_uri`, Gmail send scope, and absence of Google `redirect_uri_mismatch` / `Error 400`;
- if a VM has stale `GMAIL_OAUTH_CLIENT_ID`, back up the runtime env file, update the client id from the authoritative dev source, restart the app service, and re-check the effective redirect;
- do not claim callback token exchange is fully verified unless the matching `GMAIL_OAUTH_CLIENT_SECRET` is known to be deployed or a real callback completed.

## GitHub Actions OAuth secret injection verification

When asked whether the current GitHub repository secrets make a deployment possible, verify the workflow path rather than answering conditionally from secret presence.
For Outbound Agent Tencent VM container deployments:

- `gh secret list --repo querypie/outbound-agent` can confirm names such as `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`, per-environment token encryption secrets, and per-environment OAuth state secrets exist, but it does not prove runtime injection.
- Inspect `.github/workflows/build-outbound-front-image.yml`, `.github/workflows/deploy-tencent-container-image.yml`, and `.github/workflows/reusable-deploy-tencent-container-image.yml`.
- Main push image deploy uses the reusable Tencent deploy workflow but does not pass `update_gmail_oauth_config`; the reusable workflow default is false. Therefore normal code/image deploy keeps existing VM runtime env and skips the Gmail OAuth config upload step.
- The manual `Deploy Tencent container image` workflow has an opt-in `update_gmail_oauth_config` input. With `dry_run=true` and `update_gmail_oauth_config=true`, it validates required secret values are non-empty and uploads a temporary env file, then prints `DRY-RUN would update Gmail OAuth config in /etc/outbound-agent/front.env` without mutating the VM env file.
- To actually update VM runtime env, run the same manual workflow with `dry_run=false`, `confirm_apply=APPLY`, and `update_gmail_oauth_config=true`; it rewrites only the Gmail OAuth keys in `/etc/outbound-agent/front.env` and creates a timestamped backup.
- Report deployment as two separate claims: (1) latest code/image deploy and smoke succeeded, and (2) OAuth runtime env update path was dry-run validated or actually applied.
