# Tencent VM Gmail OAuth deploy and verification pattern

Use this reference when a Tencent VM-hosted app reads Gmail OAuth runtime configuration from a VM-local env file such as `/etc/outbound-agent/front.env`, and updates are delivered by GitHub Actions rather than by direct local SSH.

## Durable pattern

1. Confirm where runtime env is actually loaded.
   - For outbound-agent Tencent VMs, the front-end container reads `/etc/outbound-agent/front.env`.
   - Vercel/project env changes are not sufficient for these VM environments.
2. Confirm the deployment workflow supports a safe target selector before applying secrets.
   - Prefer an explicit target input such as `all`, `dev-seoul`, or `dev-tokyo` over editing workflow YAML or relying on broad defaults.
   - For Seoul-only repairs, use a Seoul target when available to avoid being blocked by Tokyo runtime/layout problems.
3. Dispatch the deploy/restart workflow with secret-sync enabled.
   - Required intent shape:
     - `dry_run=false`
     - `confirm_apply=APPLY`
     - `update_gmail_oauth_config=true`
     - `image=<known-good current image>`
     - `target=<literal desired VM target>`
   - Do not print or persist OAuth client id/secret values. Report only env key names, presence, lengths, fingerprints, or workflow input booleans.
4. Verify the workflow result at the job/step level.
   - Confirm the intended target job(s) ran and succeeded.
   - Confirm the Gmail OAuth config upload/update step ran.
   - Confirm the deploy step pulled/started the intended image.
5. Verify public availability after restart.
   - Check the literal public `/login` URL for each target, e.g. `curl -fsS -o /dev/null -w 'status=%{http_code} time_total=%{time_total}\n' <url>`.
   - A `200` login page proves app availability only; it does not prove OAuth token exchange.
6. For actual OAuth correctness, run a focused diagnosis or manual product OAuth smoke.
   - Diagnosis should confirm service/container active state, current image, and Gmail env presence without exposing secret values.
   - Product smoke should start from the app OAuth connect route and exercise the callback/token exchange.

## Debugging `invalid_client`

If Google token exchange returns `401 invalid_client` after the callback reaches the app:

- Treat redirect/state/scope as already less likely; focus first on the OAuth client id/secret pair currently loaded by the runtime.
- Confirm GitHub/secret-store timestamps and then sync those secrets into the VM-local env file through the deploy workflow.
- Restart/redeploy the front container so the new env is loaded.
- Re-test from the product OAuth start route, not by manually replaying a callback URL.

## Reporting checklist

Include:

- workflow run URL and conclusion
- image tag/SHA deployed
- target value used
- whether `update_gmail_oauth_config=true` was used
- per-target job success
- public health status for each literal target URL
- statement that secret values were not exposed

Do not include:

- OAuth client id/secret values
- token values
- raw env files
- full workflow logs if they contain broad environment output
