# Tencent Gmail OAuth negative test and restore

Use this reference when intentionally validating Gmail OAuth token-exchange failure handling on Tencent dev VMs, then restoring the correct OAuth client credentials.

## When to use

- The target environments are Tencent dev-seoul and/or dev-tokyo for `querypie/outbound-agent`.
- The app reads Gmail OAuth runtime env from VM-local `/etc/outbound-agent/front.env`.
- The operator needs to prove that an invalid `GMAIL_OAUTH_CLIENT_SECRET` produces the expected product error and that restoring the correct secret fixes OAuth connection.

## Safe workflow

1. Keep secret values out of chat, docs, PR bodies, shell output, and logs.
   - Report only secret names, item/section labels, value presence, lengths, suffixes, timestamps, and workflow run IDs.
2. Apply the intentionally wrong secret through the same path used for real repairs.
   - Update the repo-level GitHub secret `GMAIL_OAUTH_CLIENT_SECRET` with a clearly invalid test value.
   - Dispatch `Deploy Tencent container image` on `main` with:
     - `target=all` or the specific target
     - `image=<current known-good outbound-front image>`
     - `dry_run=false`
     - `confirm_apply=APPLY`
     - `update_gmail_oauth_config=true`
3. Verify the workflow at job/step level.
   - For each intended target, confirm `Upload Gmail OAuth config update` succeeded.
   - Confirm `Run deployment` succeeded.
   - Check public `/login` health for each target.
4. Run the product negative smoke from the public FQDN.
   - Start Gmail OAuth from `/{teamSlug}/settings/email-senders`.
   - Expected failure: `gmail_oauth_token_exchange_failed` after Google callback reaches the app.
   - Interpret this as token-exchange credential mismatch, not redirect URI/state/scope failure, when the setup intentionally used the wrong secret.
5. Restore the correct deployed OAuth client.
   - Use 1Password item `Outbound - OAuth Client - Dev`, section `GCP OAuth Client`.
   - Use the `querypie-saas-dev` / `Outbound` Web OAuth client pair, not Deck Dev Local or local-only fields.
   - Update both `GMAIL_OAUTH_CLIENT_ID` and `GMAIL_OAUTH_CLIENT_SECRET` repo secrets to avoid client-id/secret pair drift.
   - Redeploy with `update_gmail_oauth_config=true` through the same Tencent container image workflow.
6. Verify restore.
   - Confirm each target job's `Upload Gmail OAuth config update` and `Run deployment` steps succeeded.
   - Check `/login` health for dev-seoul and dev-tokyo.
   - Have the user/product smoke confirm Gmail OAuth connection succeeds from the Team Email Sender screen.

## Negative-test-only variant

When the user asks only to deploy the intentionally wrong `GMAIL_OAUTH_CLIENT_SECRET`, stop after the negative runtime update and availability checks. Report the GitHub Actions run URL, target, image, `update_gmail_oauth_config=true`, `dry_run=false`, per-target config upload/deploy status, public `/login` health, and that secret values were not exposed. Treat restore as the next operational step, not as already completed.

## Documentation pattern

When recording the result in docs/OpenSpec:

- Record workflow run IDs, target, image tag, public health URLs, observed product error reason, and user-confirmed success.
- Explicitly say secret values, token values, and raw env files were not recorded.
- Distinguish OAuth connection success from Gmail actual-send success. `users.messages.send` message id/thread id evidence is a separate smoke.
- In OpenSpec, add scenarios for:
  - wrong OAuth client secret fails at token exchange and surfaces `gmail_oauth_token_exchange_failed`
  - restored OAuth client secret allows sender connection

## Pitfalls

- Do not use the Deck Dev Local or local-only OAuth fields when restoring Tencent dev runtime. Use the deployed Outbound client section.
- Do not claim dev-tokyo OAuth connection was product-smoked unless it was actually exercised; `/login` health plus shared secret sync is only runtime availability/config rollout evidence.
- Do not collapse this failure into `refresh_token_missing`; failed token endpoint responses should preserve the safe provider/token-exchange failure category first.
